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
idx = lexsort((start_times,))
# Sort:    
samples = samples[idx]
times,clats = samples[:,0], samples[:,1]
start_times = start_times[idx]

def weighted_percentile(percs, vs, ws):
    idx = np.argsort(vs)
    vs, ws = vs[idx], ws[idx]
    cdf = 100 * ws.cumsum() / ws.sum()
    return np.interp(percs, cdf, vs)

def weights(start_ts, end_ts, start, end):
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

    idx = where(lor ( land(start_times >= start, start_times <  end)
                    , land(times       >  start, times       <= end)))

    ss = samples[idx]
    if len(ss) == 0: continue
    
    start_ts = start_times[idx]
    end_ts, vs = ss[:,0], ss[:,1]
    
    ws = weights(start_ts, end_ts, start, end)
    ps = weighted_percentile(percs, vs, ws)

    row = [end, len(ss), np.min(vs), np.average(vs)] + list(ps) + [np.max(vs)]
    fmt = "%d, %d" + ', '.join(["%.4f"] * 7)
    print (fmt % tuple(row))

