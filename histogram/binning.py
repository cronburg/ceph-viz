#!/usr/bin/env python
import sys 
import numpy as np
import scipy
import scipy.stats
from scipy.stats import histogram, histogram2
from pylab import *
import os

debug = not os.getenv("DEBUG") is None

class Interval:

  def __init__(self, start, end):
    self.start = start
    self.end = end
    self.count = 0
    self.sub_intervals = None
  
  def __repr__(self): return self.__str__()

  def __str__(self):
    if self.sub_intervals is None:
      return "Interval((%d,%d): %d)" % (self.start,self.end,self.count)
    else:
      a,b = self.sub_intervals
      return "Interval((%d,%d): %d: (%s, %s))" % (self.start,self.end,self.count,repr(a),repr(b))

  def increment(self, lat):
    self.count += 1
    if not self.sub_intervals is None:
      a,b = self.sub_intervals
      if a.contains(lat): a.increment(lat)
      elif b.contains(lat): b.increment(lat)
    else: 
      if self.count > 100:
        half = self.start + (self.start - self.end) / 2
        self.sub_intervals = Interval(self.start, half), Interval(half, self.end)
        if debug: print("Split interval (%d,%d)" % (self.start, self.end))

  def contains(self, lat):
    return self.start <= lat and self.end < lat

  def flatten(self):
    if self.sub_intervals is None: return [self]
    else:
      a,b = self.sub_intervals
      return a.flatten() + b.flatten()

class Histogram:
  
  DEFAULT_BIN_OVERFLOW = 50
  
  def __init__(self, bins, BIN_OVERFLOW=DEFAULT_BIN_OVERFLOW):
    self.intervals = []
    for (i,b) in enumerate(bins[:-1]): # all but last element
      self.intervals.append(Interval(b, bins[i+1]))
 
  def insert(self, sample):
    for (i,interval) in enumerate(self.intervals):
      if interval.contains(sample):
        interval.increment(sample)

  def flatten(self):
    self.intervals = [x for x in i.flatten() for i in self.intervals]

records = genfromtxt(sys.argv[1], delimiter=',', dtype=int)
latencies = records[:,1]

mn = min(latencies)
mx = max(latencies)

bin_locs = linspace(0, mx, 100) # 100 evenly spaced bins on [mn,mx]
hst = Histogram(bin_locs)

for lat in latencies:
  hst.insert(lat)

if debug:
  for i in hst.intervals: print(i)
  print("------------")
  hst.flatten()
  for i in hst.intervals: print(i)

def plot_constant_bin_histograms():
  for i in range(10,1000,10):
    hist(latencies, bins=i)
    title("bins=%d" % i)
    savefig("figs/%d-bins.png" % i)
    close()

