#!/usr/bin/env python2.7
import sys, os
import numpy as np
import argparse
import math

debug = not os.getenv("DEBUG") is None

class Interval:
    def __init__(self, start, end, ctx):
        self.start = start
        self.end = end
        self.hist = ExpHistogram(ctx)
        self.processed = False

    def contains(self, sample):
        """ Whether or not the given sample falls (at least partially) in this interval"""
        return (self.start <= sample.start and self.end > sample.start) \
                or (sample.end > self.start and sample.end <= self.end)

    def weight(self, sample):
        if not self.contains(sample):
            return 0.0
        if sample.end <= self.end:
            return 1.0
        return float(self.end - sample.start) / sample.duration

    def add(self, sample):
        if debug: assert(self.contains(sample))
        self.hist.add(sample, self.weight(sample))

    def __repr__(self): return self.__str__()
    def __str__(self):
        return "Interval(%d,%d,%s)" % (self.start, self.end, repr(self.hist))

    def process(self):
        print ("%s, %s," % (self.start, self.end)),
        self.hist.process(self.start, self.end)
        self.processed = True

class Sample:
    def __init__(self, data):
        self.end, self.clat, self.rw, self.sz = data
        self.duration = self.clat / 1000.0    # clat in microseconds (to match times)
        self.start = self.end - self.duration

    def starts_after(self, interval):
        """ Whether or not this sample occurs completely after the given interval """
        return self.start >= interval.end

    def ends_after(self, interval):
        """ Whether or not this sample ends at a time after the given interval """
        return self.end > interval.end

    def __repr__(self): return self.__str__()
    def __str__(self):
        return "Sample(%d,%d,%d,%d,%d)" % (self.start, self.end, self.clat, self.rw, self.sz)

class ExpHistogram:
        
    def get_bins(self, num_bins):
        return np.logspace(self.ctx.min_power, self.ctx.max_power, num=num_bins, base=2.0)
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.bins = self.get_bins(ctx.bins)
        self.samples = []
        self.weights = []
        self.processed = False

    def add(self, sample, weight):
        self.samples.append(sample)
        self.weights.append(weight)

    def process(self, start, end):
        
        if len(self.samples) == 0:
            self.pctiles = None
            self.processed = True
            print('no samples')
            return

        clats = np.fromiter(map(lambda x: x.clat, self.samples), dtype=int)
        #clats_hist = histogram2(clats, self.bins).tolist()
        clats_hist,_ = np.histogram(clats, self.get_bins(self.ctx.bins + 1), weights=self.weights)
        print (', '.join(map(str, clats_hist)))

        cdf = np.cumsum(clats_hist) / len(clats)

        ps = np.array([0.50, 0.90, 0.95, 0.99])
        if debug: print(self.bins, cdf, len(self.bins), len(cdf))
        pctiles = np.interp(ps, cdf, self.bins)
        #import pdb; pdb.set_trace()
        exact_pctiles = np.percentile(clats, 100*ps)
        
        self.pctiles = pctiles
        self.exact_pctiles = exact_pctiles

        self.processed = True
        

def main(ctx):
    INTERVAL_WIDTH = ctx.interval
    inters = [Interval(0, INTERVAL_WIDTH, ctx)]
    

    def add_new_intervals(sample):
        """ Add new intervals until we have all the ones necessary covering the
            given sample. Pre & post condition: inters is (always) in sorted order.
        """
        last = inters[-1]
        while sample.ends_after(last):
            #print(last)
            last = Interval(last.end, last.end + INTERVAL_WIDTH, ctx)
            inters.append(last)
    
    def bin_fmt(bin_value):
        return str(round(bin_value,2))

    pctiles = []
    exact_pctiles = []
    print("# start-time end-time " + ', '.join(map(bin_fmt, inters[0].hist.bins)))
    # Assumption: samples are given in sorted (by time) order
    
    with open(ctx.filename, 'r') as fp:
        for (count, line) in enumerate(fp):
            sample = Sample(tuple(map(int, line.split(', '))))
            
            # Do we need any new intervals added to the end of our interval list?
            add_new_intervals(sample)
        
            for i in inters:
                if i.contains(sample):
                    i.add(sample)
                
                if sample.start > ctx.max_latency * 1000 + i.end:
                    i.process()
                    if not i.hist.pctiles is None: pctiles.append(i.hist.pctiles)
                    inters.remove(i)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    def arg(*args ,**kwargs): p.add_argument(*args, **kwargs)
    arg('-b', '--bins', default=8, type=int, help='number of exponential-sized bins to use per interval')
    arg('-mi', '--min_power', default=0, type=int, help='smallest clat value (us) expected (lower bound on bins, power of 2)')
    arg('-ma', '--max_power', default=28, type=int, help='largest clat value (us) expected (upper bound on bins, power of 2)')
    arg('--max_latency', default=300, type=float, help='number of seconds (s) after which we drop intervals')
    arg('-i', '--interval', default=1000, type=int, help='interval width (ms)')
    arg('--filename', help='filename of clat log file')
    main(p.parse_args())
     
