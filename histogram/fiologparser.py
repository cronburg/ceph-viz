#!/usr/bin/env python2.7
import sys
import numpy as np
from numpy import genfromtxt, lexsort, around, where, logical_and, logical_or
land = logical_and
lor  = logical_or

# Load samples into 4 x N array, sorted by start time.
samples = genfromtxt(sys.argv[1], dtype=int, delimiter=',')    
times,clats = samples[:,0], samples[:,1]
start_times = times - (clats / 1000.0)
# Sort by start time:    
idx = lexsort((start_times,))
samples = samples[idx]
times,clats = samples[:,0], samples[:,1]
start_times = start_times[idx]

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
mx = around(times[-1], decimals=-4) # round up to nearest 10,000
for start in range(0, mx, INTERVAL):
    end = start + INTERVAL

    # Determine which samples are in the current window:
    idx = where(lor ( land(start_times >= start, start_times <  end)
                    , land(times       >  start, times       <= end)))
    ss = samples[idx]
    if len(ss) == 0: continue
    
    start_ts = start_times[idx]
    end_ts, vs = ss[:,0], ss[:,1]

    # Compute weights and subsequently compute the weighted
    # percentiles we are interested in:
    ws = weights(start_ts, end_ts, start, end)
    ps = weighted_percentile(percs, vs, ws)

    # Output formatting same as current fiologparser:
    row = [end, len(ss), np.min(vs), np.average(vs)] + list(ps) + [np.max(vs)]
    fmt = "%d, %d" + ', '.join(["%.4f"] * 7)
    print (fmt % tuple(row))

