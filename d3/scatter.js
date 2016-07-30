
var margin = {top: 10, bottom: 30, left: 80, right: 10}
  , width = 900 - (margin.left + margin.right)
  , height = 500 - (margin.top + margin.bottom);

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var xScale = d3.scale.linear().range([0,width])
  , yScale = d3.scale.linear().range([height,0])
  , color  = d3.scale.category10()
  ;

var xAxis = d3.svg.axis().scale(xScale).orient("bottom")
  , yAxis = d3.svg.axis().scale(yScale).orient("left")
  ;

d3.text("test.csv", txt => {
  data = d3.csv.parseRows(txt);
  data.splice(0,1);
  data = data.map(row => {
    return { end:     parseInt(row[0])
           , samples: parseInt(row[1])
           , min:     parseFloat(row[2])
           , avg:     parseFloat(row[3])
           , median:  parseFloat(row[4])
           , p90:     parseFloat(row[5])
           , p95:     parseFloat(row[6])
           , p99:     parseFloat(row[7])
           , max:     parseFloat(row[8])
           };
  });

  var mnX  = d3.min(data, d => d.end)
    , mxX  = d3.max(data, d => d.end)
    , rngX = mxX - mnX
    , mnY  = d3.min(data, d => d.min)
    , mxY  = d3.max(data, d => d.max)
    , rngY = mxY - mnY
    ;

  xScale.domain([mnX - 0.05 * rngX, mxX + 0.05 * rngX]);
  yScale.domain([mnY - 0.05 * rngY, mxY + 0.05 * rngY]);

  svg.append("g")
      .attr("class", "axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("End-Time (ms)")
      ;
  
  svg.append("g")
      .attr("class", "axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".9em")
      .style("text-anchor", "end")
      .text("Latency (ms)")
      ;

  plotMe = xFncn => {
    return (c, yFncn) => {
      svg.selectAll(".point")
          .data(data)
        .enter().append("circle")
          .attr("class", "dot")
          .attr("r", 3)
          .attr("cx", d => xScale(xFncn(d)))
          .attr("cy", d => yScale(yFncn(d)))
          .style("fill", d => color(c))
  
      var lineFncn = d3.svg.line()
        .x(d => xScale(xFncn(d)))
        .y(d => yScale(yFncn(d)))
        .interpolate("linear")
        ;

      svg.append("path")
          .attr("class", "data_path")
          .attr("d", lineFncn(data))
          .attr("stroke", color(c))
          .attr("stroke-width", 2)
          .attr("fill", "none")
          ;
    };
  };

  p = plotMe(d => d.end)
  p(0, d => d.min);
  p(1, d => d.median)
  p(2, d => d.p90)
  p(3, d => d.p95)
  p(4, d => d.p99)
  p(5, d => d.max)

});

