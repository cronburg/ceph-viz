#!/bin/bash
LOGS_DIR="/home/karl-fio-twothreads-justreadwrite-10minutes/00000000/LibrbdFio/osd_ra-00004096/op_size-00131072/concurrent_procs-001/iodepth-032/read"

# Coarse data method
echo "Running coarse fiologparser..."
outfn=out/fiologparser-coarse.csv
echo -n "# " > "$outfn"
fiologparser.py -A $LOGS_DIR/log_avg_msec/*_lat* &>> "$outfn"

echo "Running exact fiologparser..."
outfn=out/fiologparser-exact.csv
echo -n "# " > "$outfn"
fiologparser.py -A $LOGS_DIR/*_lat* &>> "$outfn"

echo "Done!"
