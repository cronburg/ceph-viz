#!/usr/bin/env python3
import sys, os
import numpy as np
import scipy
import scipy.stats
from scipy.stats import histogram, histogram2

debug = not os.getenv("DEBUG") is None

class Interval:
  def __init__(self, start, end):
    self.start = start
    self.end = end
    self.samples = []

  def contains(self, sample):
    """ Whether or not the given sample falls (at least partially) in this interval"""
    return (self.start <= sample.time and self.end < sample.end) \
        or (sample.end > self.start and sample.end <= self.end)

  def add(self, sample):
    if debug: assert(self.contains(sample))
    self.samples.append(sample)

  def __repr__(self): return self.__str__()
  def __str__(self):
    return "Interval(%d,%d,%s)" % (self.start, self.end, repr(self.samples))

class Sample:
  def __init__(self, data):
    self.time, self.clat, self.rw, self.sz = data
    self.end = self.time + self.clat
  
  def starts_after(self, interval):
    """ Whether or not this sample occurs completely after the given interval """
    return self.time >= interval.end

  def ends_after(self, interval):
    """ Whether or not this sample ends at a time after the given interval """
    return self.end > interval.end

  def __repr__(self): return self.__str__()
  def __str__(self):
    return "Sample(%d,%d,%d,%d)" % (self.time,self.clat,self.rw,self.sz)

bins = [10**i for i in range(1,9)]
INTERVAL_WIDTH = 1000
inters = [Interval(0, INTERVAL_WIDTH)]

def process_interval(inter):
  if debug: print("Interval(%d,%d):" % (inter.start,inter.end))
  clats = np.fromiter(map(lambda x: x.clat, inter.samples), dtype=int)
  clats_hist = histogram2(clats, bins).tolist()
  start,end = str(inter.start), str(inter.end)
  print ("%s, %s, " % (start,end) + ', '.join(map(str, clats_hist)))
#  print(start + ', ' + end + ', '.join(map(str, clats_hist)))

def add_new_intervals(sample):
  """ Add new intervals until we have all the ones necessary covering the
      given sample. Pre & post condition: inters is (always) in sorted order.
  """
  global inters
  last = inters[-1]
  while sample.ends_after(last):
    #print(last)
    last = Interval(last.end, last.end + INTERVAL_WIDTH)
    inters.append(last)

print("# start-time end-time " + ', '.join(map(str, bins)))
# Assumption: samples are given in sorted (by time) order
for line in sys.stdin:
  sample = Sample(tuple(map(int, line.split(', '))))
  
  # Do we need any new intervals added to the end of our interval list?
  add_new_intervals(sample)

  for i in inters:
    # If we have gone past an interval, process it and remove it from the list
    if sample.starts_after(i):
      process_interval(i)
      inters.remove(i)
    elif i.contains(sample):
      i.add(sample)

