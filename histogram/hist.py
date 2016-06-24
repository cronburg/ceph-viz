#!/usr/bin/env python2.7
import argparse
import sys
import numpy as np
from glob import glob
import os
import pprint
import matplotlib
matplotlib.use("Agg")
import pylab
from helpers import *

p = argparse.ArgumentParser()
def arg(*args, **kwargs): p.add_argument(*args, **kwargs)

arg('log_dir', help='location of fio data files')
arg('window_size', help='size of window to calculate percentiles in, in milliseconds')
arg('percentile', help='what percentile to calculate, in (0,100]')
arg('log_type', default="clat", help='which data set to use. defaults to "clat"')
ctx = p.parse_args()

pctile = int(ctx.percentile)

data_files = glob(os.path.join(ctx.log_dir, '1_%s.*.log' % (ctx.log_type,)))
#print data_files

data = sort_data(load_all_fio_files(data_files), lambda x: x[0])

print "Dimensions: (%d,%d)" % (len(data), len(data[0]))
times,values,directions,size = np.transpose(data)
values = values / 1000.
#map(lambda i: data[:,i], range(len(data[0])))
print times

def do_hist(vs, fn):
  pylab.hist(vs, bins=int(len(vs)/10))
  pylab.xlabel(ctx.log_type)
  pylab.ylabel("frequency (# samples)")
  pylab.title("Histogram: " + fn)
  pylab.savefig(fn)
  pylab.close()

i = 0
percentiles = []
while i < len(data):

  # Determine the endpoint of this window:
  j = i
  while j < len(times) and (times[j] - times[i] < ctx.window_size):
    j += 1
  j += 1
#    print (times[j]-times[i],ctx.window_size)

  ts = times[i:j]
  vs = values[i:j]

  #pdb.set_trace()
  percentiles.append((len(ts), ts[-1] - ts[0], np.percentile(vs, pctile)))
  #print i,j,len(times)
  done = int(100 * float(ts[-1]) / times[-1])
  print "%02d%%) percentile=%d for time=[%d,%d]: %s" % (done, pctile, ts[0], ts[-1], str(percentiles[-1]))
 
  do_hist(vs, "out/%d-%d.png" % (ts[0],ts[-1]))

  i = j

print "Window percentiles: "
pprint.pprint(percentiles)

pctile_overall_exact = np.percentile(values, pctile)
print "Overall %d-percentile: %d" % (pctile, pctile_overall_exact)

weighted_pct = lambda (n_ops, time, pct): n_ops * pct
get_n_ops = lambda x: x[0] # get just the n_ops from percentiles list

pctile_weighted_estimate = sum(map(weighted_pct, percentiles)) / sum(map(get_n_ops, percentiles))
print "Merged %d-percentile from window percentiles: " + str(pctile_weighted_estimate)

error = 100.0 * abs(pctile_weighted_estimate - pctile_overall_exact) / pctile_overall_exact
print "error: %6.2f %%" % error

do_hist(values, "out/all.png")

