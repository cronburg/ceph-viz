#!/usr/bin/python
#
# rsptimes_histogram.py -- python program to reduce response time sample data from smallfile benchmark to
# histograms.  It generates two histograms:
# response times, using histogram with bins that are powers of 10.  Since smallest measurable response time is 1 microsec in iostat (really larger than that), lowest bin is 0.0001, and we proceed upward to 1000 microsec).
# times - from start of test, define 10 bins so that minimum value in bin is 0 and max value is max time
# print out .csv record format for the resulting histograms

import sys
import os
import string
import numpy
import scipy
import scipy.stats
from scipy.stats import histogram, histogram2

debug = os.getenv("DEBUG")

rsptime_fn = sys.argv[1]
f = open(rsptime_fn, "r")
records = f.readlines()

times = numpy.array( [ float(r.strip().split(',')[1]) for r in records ] )
maxtime = max(times)
(time_histo, time_low_range, time_binsize, time_extrapoints) = histogram( times, defaultlimits=(0.0, maxtime))
assert(time_low_range == 0.0)
assert(time_extrapoints == 0)
if debug: 
  print(time_histo, ' shape ', time_histo.shape, ' low_range ', time_low_range, ' binsize ', time_binsize, ' extrapoints ', time_extrapoints)
print('time histogram: %s'%string.join([ str(v) for v in time_histo.tolist() ], ','))

rsptimes = numpy.array( [ float(r.strip().split(',')[2]) for r in records ] )
rsptime_histo = histogram2( rsptimes, [ 0.0001, 0.00032, 0.001, 0.0032, 0.01, 0.032, 0.1, 0.32, 1, 3.2, 10, 32, 100 ] )
if debug: 
  print(rsptime_histo,rsptime_histo.shape)
print('response time histogram: %s'%string.join( [ str(v) for v in rsptime_histo.tolist() ], ','))

