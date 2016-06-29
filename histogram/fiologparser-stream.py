#!/usr/bin/env python2.7
import sys
import numpy as np
from numpy import genfromtxt, lexsort, around, where, logical_and, logical_or
land = logical_and
lor  = logical_or
from itertools import islice

def weighted_percentile(percs, vs, ws):
    """ Use linear interpolation to calculate the weighted percentile """
    idx = np.argsort(vs)
    vs, ws = vs[idx], ws[idx] # weights and values sorted by value
    cdf = 100 * ws.cumsum() / ws.sum() # cumulative distribution function
    return np.interp(percs, cdf, vs) # linear interpolation

def weights(start_ts, end_ts, start, end):
    """ Calculate weights based on fraction of sample falling in the
        given interval [start,end] """
    sbounds = np.maximum(start_ts, start).astype(float)
    ebounds = np.minimum(end_ts,   end).astype(float)
    return (ebounds - sbounds) / (end_ts - start_ts)

columns = ["end-time", "samples", "min", "avg", "median", "90%", "95%", "99%", "max"]
percs   = [50, 90, 95, 99]
print(', '.join(columns))
INTERVAL = 10000

def process_interval(samples, start, end):
    
    times,clats = samples[:,0], samples[:,1]
    start_times = times - (clats / 1000.0)
    # Sort by start time:    
    idx = lexsort((start_times,))
    samples = samples[idx]
    times,clats = samples[:,0], samples[:,1]
    start_times = start_times[idx]

    # Determine which samples are in the current window:
    idx = where(lor ( land(start_times >= start, start_times <  end)
                    , land(times       >  start, times       <= end)))
    ss = samples[idx]
    if len(ss) > 0:
        
        start_ts = start_times[idx]
        end_ts, vs = ss[:,0], ss[:,1]

        # Compute weights and subsequently compute the weighted
        # percentiles we are interested in:
        ws = weights(start_ts, end_ts, start, end)
        ps = weighted_percentile(percs, vs, ws)

        # Output formatting same as current fiologparser:
        row = [end, len(ss), np.min(vs), np.average(vs)] + list(ps) + [np.max(vs)]
        fmt = "%d, %d, " + ', '.join(["%.4f"] * 7)
        print (fmt % tuple(row))

BUFF_SIZE = 10000
def read_next(fp, sz):
    with np.warnings.catch_warnings():
        np.warnings.simplefilter("ignore")
        return genfromtxt(islice(fp, BUFF_SIZE), dtype=int, delimiter=',')

def main(ctx):
    with open(sys.argv[1], 'r') as fp:
        start = 0
        end = INTERVAL
        arr = read_next(fp, BUFF_SIZE)
        more_data = True
        while more_data or len(arr) > 0:

            # Read up to 5 minutes of data from end of current interval.
            while len(arr) == 0 or arr[-1][0] < 300 * 1000 + end:
                new_arr = read_next(fp, BUFF_SIZE)
                if new_arr.shape[0] < BUFF_SIZE:
                    more_data = False
                    break
                arr = np.append(arr, new_arr, axis=0)

            process_interval(arr, start, end)
        
            # Update arr to throw away samples we no longer need - samples which
            # end before the start of the next interval, i.e. the end of the
            # current interval:
            idx = where(arr[:,0] > end)
            arr = arr[idx]

            start += INTERVAL
            end = start + INTERVAL

if __name__ == '__main__':
    main(None) # TODO: argparse

