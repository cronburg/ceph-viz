#!/usr/bin/env python2.7
import sys
import numpy as np
from numpy import genfromtxt, lexsort, around, where
land, lor, lnot = np.logical_and, np.logical_or, np.logical_not
from itertools import islice
import argparse
import os
import pandas

debug = not (os.getenv("DEBUG") is None)

def weighted_percentile(percs, vs, ws):
    """ Use linear interpolation to calculate the weighted percentile.
        
        Value and weight arrays are first sorted by value. The cumulative
        distribution function (cdf) is then computed, after which np.interp
        finds the two values closest to our desired weighted percentile(s)
        and linearly interpolates them.
        
        percs  :: List of percentiles we want to calculate
        vs     :: Array of values we are computing the percentile of
        ws     :: Array of weights for our corresponding values
        return :: Array of percentiles
    """
    idx = np.argsort(vs)
    vs, ws = vs[idx], ws[idx] # weights and values sorted by value
    cdf = 100 * ws.cumsum() / ws.sum()
    return np.interp(percs, cdf, vs) # linear interpolation

def weights(start_ts, end_ts, start, end):
    """ Calculate weights based on fraction of sample falling in the
        given interval [start,end]. Weights computed using vector / array
        computation instead of for-loops.
    
        start_ts :: Array of start times for a set of samples
        end_ts   :: Array of end times for a set of samples
        start    :: int
        end      :: int
        return   :: Array of weights
    """
    sbounds = np.maximum(start_ts, start).astype(float)
    ebounds = np.minimum(end_ts,   end).astype(float)
    return (ebounds - sbounds) / (end_ts - start_ts)

columns = ["end-time", "samples", "min", "avg", "median", "90%", "95%", "99%", "max"]
percs   = [50, 90, 95, 99]
print(', '.join(columns))
def process_interval(ctx, samples, start, end):
    """ Determine which of the given samples occur during the given interval,
        then compute and print the desired statistics - min, avg, percentiles, max.

        samples :: Array / matrix of samples (as seen in fio log files)
        start   :: int
        end     :: int
    """
    
    times,clats = samples[:,0], samples[:,1]
    start_times = times - (clats / 1000.0)   # convert end time array to start times
    # Sort by start time:    
    idx = lexsort((start_times,))
    samples = samples[idx]
    times,clats = samples[:,0], samples[:,1]
    start_times = start_times[idx]

    # Determine which samples occured during the current interval [start,end]:
    idx = where(lnot(lor(start_times >= end, times <= start)))
    ss = samples[idx]
    start_ts = start_times[idx]
    end_ts, vs = ss[:,0], ss[:,1]
    
    if len(ss) > 0:
        ws = weights(start_ts, end_ts, start, end)
        if debug: assert(np.all(ws > 0))
        ps = weighted_percentile(percs, vs, ws)

        # Output formatting same as '-A' option of fiologparser:
        row = [end, len(ss), np.min(vs), np.average(vs)] + list(ps) + [np.max(vs)]
        fmt = "%d, %d, " + ', '.join(["%%.%df" % ctx.decimals] * 7)
        print (fmt % tuple(row))

def read_next(fp, sz):
    """ Helper to get rid of 'empty file' warnings """
    with np.warnings.catch_warnings():
        np.warnings.simplefilter("ignore")
        #data = genfromtxt(islice(fp, sz), dtype=int, delimiter=',')
        data = pandas.read_csv(Reader(islice(fp, sz)), dtype=int, header=None).values
        if len(data.shape) == 1:
            return np.array([data]) # Single-line files are dumb.
        return data

def fio_generator(fps):
    """ Create a generator for reading multiple fio files in end-time order """
    lines = {fp: fp.next() for fp in fps}
    while True:
        # Get fp with minimum value in the first column (fio log end-time value)
        fp = min(lines, key=lambda k: int(lines.get(k).split(',')[0]))
        yield lines[fp]
        lines[fp] = fp.next() # read a new line into our dictionary

class Reader(object):
    def __init__(self, g):
        self.g = g
    def read(self, n=0):
        try:
            return next(self.g)
        except StopIteration:
            return ''

#iter_csv = pandas.read_csv('file.csv', iterator=True, chunksize=1000)
#df = pd.concat([chunk[chunk['field'] > constant] for chunk in iter_csv])

def main(ctx):
    fps = [open(f, 'r') for f in ctx.files]
    fp = fio_generator(fps)
    
    try:
        start = 0
        end = ctx.interval
        arr = read_next(fp, ctx.buff_size)
        more_data = True
        while more_data or len(arr) > 0:

            # Read up to 5 minutes of data from end of current interval.
            while len(arr) == 0 or arr[-1][0] < ctx.max_latency * 1000 + end:
                new_arr = read_next(fp, ctx.buff_size)
                if new_arr.shape[0] < ctx.buff_size:
                    more_data = False
                    break
                arr = np.append(arr, new_arr, axis=0)

            process_interval(ctx, arr, start, end)
        
            # Update arr to throw away samples we no longer need - samples which
            # end before the start of the next interval, i.e. the end of the
            # current interval:
            idx = where(arr[:,0] > end)
            arr = arr[idx]

            start += ctx.interval
            end = start + ctx.interval
    finally:
        map(lambda f: f.close(), fps)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    arg = p.add_argument
    arg('-f', '--files', required=True, help='space separated list of latency log filenames', nargs='+')
    arg('--max_latency', default=300, type=float, help='number of seconds of data to process at a time')
    arg('-i', '--interval', default=10000, type=int, help='interval width (ms)')
    arg('--buff_size', default=10000, type=int, help='number of samples to buffer into numpy at a time')
    arg('-d', '--decimals', default=3, type=int, help='number of decimal places to print floats to')
    main(p.parse_args())

