#!/usr/bin/env python2.7
import csv
import argparse
from glob import glob
import os
from helpers import *

p = argparse.ArgumentParser()
def arg(*args, **kwargs): p.add_argument(*args, **kwargs)

arg('log_dir', help='location of fio data files')
arg('log_avg_msec', type=int, help='size of window to average samples over, in milliseconds')
arg('log_type', default="clat", help='which data set to use. defaults to "clat"')

# TODO: can deduce these from filenames:
arg('num_threads', default=1, type=int, help='number of log file threads')
arg('num_files_per_thread', default=1, type=int, help='number of log files produce by fio per thread')

ctx = p.parse_args()

#data_files = get_files_in_dir_matching(ctx.log_dir, 'output\.\d_%s\..*\.log' % (ctx.log_type,))

# Manually perform the averaging that fio does, purposefully degrading
# the granularity of the data, for input to fiologparser.
def do_log_avg_msec(data):
  t0 = data[0][0]
  data_out = []
  curr_data = []
  for line in data:
    time,val,rw,sz = line
    if time - t0 > ctx.log_avg_msec:
      #pdb.set_trace()
      data_out.append([t0, int(np.average(curr_data)), rw, sz]) # assuming rw & size are constant
      t0 = time
      curr_data = []
    else:
      curr_data.append(line)
  
  # Reached end, but maybe tiny bit of data left at end:
  if len(curr_data) > 0:
    data_out.append([t0, int(np.average(curr_data)), rw, sz]) # assuming rw & size are constant
  
  return data_out

for thread in range(ctx.num_threads):
  data = []
  for filenum in range(ctx.num_files_per_thread):
    data.extend(load_fio_file(os.path.join(ctx.log_dir, \
        "output.%d_%s.%d.log.gprfc073" % \
        (filenum, ctx.log_type, thread+1))))
  #print data
  data = do_log_avg_msec(data)
  
  out_fn = join(ctx.log_dir, "log_avg_msec")
  makedirs(out_fn)
  out_fn = join(out_fn, "output.1_%s.%d.log.gprfc073" % (ctx.log_type, thread+1))
  with open(out_fn, "w") as f:
    for line in data:
      f.write("%u, %u, %u, %u\n" % tuple(line))
  #pdb.set_trace()

