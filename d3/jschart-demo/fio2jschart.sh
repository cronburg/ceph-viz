#!/bin/bash

makePlot() {
  echo "#LABEL:$4-$5" > $3
  cat $1 | grep -v end-time | cut -f1,$2 -d, | sed 's/,//g' >> $3;
}

makePlot "$1" 3 min.log "Minimum" "$2"
makePlot "$1" 4 avg.log "Average" "$2"
makePlot "$1" 5 med.log "Median" "$2"
makePlot "$1" 6 p90.log "90th Percentile" "$2"
makePlot "$1" 7 p95.log "95th Percentile" "$2"
makePlot "$1" 8 p99.log "99th Percentile" "$2"
makePlot "$1" 9 max.log "Maximum" "$2"

