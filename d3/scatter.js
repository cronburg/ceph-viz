
var margin = {top: 10, bottom: 30, left: 110, right: 10}
  , width = 900 - (margin.left + margin.right)
  , height = 500 - (margin.top + margin.bottom);

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    ;

lines = 
  [ {c: 0, value: "min", label: "Minimum"}
  , {c: 1, value: "avg", label: "Average"}
  , {c: 2, value: "med", label: "Median"}
  , {c: 3, value: "p90", label: "90th Percentile"}
  , {c: 4, value: "p95", label: "95th Percentile"}
  , {c: 5, value: "p99", label: "99th Percentile"}
  //, {c: 6, value: "max", label: "Maximum"}
  ]

d3.select("body").selectAll("input")
  .data(lines).enter()
  .append("label")
    .html(d => d.label)
  .insert("input", ":first-child")
    .attr("type", "checkbox")
    .attr("checked", true)
    .attr("class", d => d.value);

d3.selectAll("input").on("change", d => {
  var cbox = d3.selectAll("input." + d.value);
  console.log(cbox,cbox.attr("checked"));
  if (cbox.attr("checked")) {
    console.log("Removing:",d);
    // Remove all the circles and the path corresponding to this line:
    svg.selectAll("circle." + d.value).remove();
    svg.selectAll("path." + d.value).remove();
  } else {
    // Plot the data for this line again:
    console.log("Re-adding:",d);
    plotMeEnd(d);
  }
});

//d3.selectAll(".label_div").insert("br", ":first-child");

var xScale = d3.scale.linear().range([0,width])
  , yScale = d3.scale.linear().range([height,0])
  , color  = d3.scale.category10()
  ;

var xAxis = d3.svg.axis().scale(xScale).orient("bottom")
  , yAxis = d3.svg.axis().scale(yScale).orient("left")
  ;
  
plotMe = xFncn => {
  return line => {
    svg.selectAll(".point")
        .data(data)
      .enter().append("circle")
        .attr("class", line.value)
        .attr("r", 2)
        .attr("cx", d => xScale(xFncn(d)))
        .attr("cy", d => yScale(d[line.value]))
        .style("fill", d => color(line.c))
        ;

    var lineFncn = d3.svg.line()
      .x(d => xScale(xFncn(d)))
      .y(d => yScale(d[line.value]))
      .interpolate("linear")
      ;

    svg.append("path")
        .attr("class", line.value)
        .attr("d", lineFncn(data))
        .attr("stroke", color(line.c))
        .attr("stroke-width", 2)
        .attr("fill", "none")
        ;
  };
};
plotMeEnd = plotMe(d => d.end);

d3.text("clat-numpy.log", txt => {
  data = d3.csv.parseRows(txt);
  data.splice(0,1);
  data = data.map(row => {
    return { end:     parseInt(row[0])
           , samples: parseInt(row[1])
           , min:     parseFloat(row[2])
           , avg:     parseFloat(row[3])
           , med:     parseFloat(row[4])
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
    , mxY  = d3.max(data, d => d.min)
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

  lines.forEach(plotMeEnd);

});

