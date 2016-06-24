#!/usr/bin/env python2.7
# Taken from Ben to compare percentile methods.
import math
import random
import os
import sys
import numpy
from numpy import percentile

n1 = int(sys.argv[1])
n2 = int(sys.argv[2])
pctile = int(sys.argv[3])

print('sample[1] size = %d , sample[2] size = %d, percentile = %d' % 
     (n1, n2, pctile))

sample1 = numpy.array(
               [ numpy.random.standard_exponential() for k in range(0, n1) ])
sample2 = numpy.array(
               [ 3*numpy.random.standard_exponential() for k in range(0, n2) ])

print('sample1: %s' % str(sample1))
print('sample2: %s' % str(sample2))

allsamples = numpy.append(sample1, sample2)
print('all: %s' % str(allsamples))

pct1 = percentile(sample1, 90)
pct2 = percentile(sample2, 90)
pctall = percentile(allsamples, 90)
pct_estimate = ((n1 * pct1) + (n2 * pct2)) / (n1 + n2)
estimate_error = 100.0 * abs(pctall - pct_estimate) / pctall

print('pct1: %f' % pct1)
print('pct2: %f' % pct2)
print('pctall: %f' % pctall)
print('estimate: %f' % pct_estimate)
print('error: %6.2f %%' % estimate_error)
