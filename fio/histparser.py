#!/usr/bin/env python
import pandas
import numpy as np
import argparse
from itertools import islice
from fiostat import plat_idx_to_val

default_bins = map(plat_idx_to_val, np.arange(1216))
def percentile(percs, histogram, bin_locs=default_bins):
    cdf = 100 * histogram.cumsum() / histogram.sum()
    return np.interp(percs, cdf, bin_locs)

class Reader(object):
    def __init__(self, g): 
        self.g = g 
    def read(self, n=0):
        try:
            return next(self.g)
        except StopIteration:
            return ''

__read_hist_csv_last = np.zeros(1217)
def read_hist_csv(fp, sz, last=__read_hist_csv_last):
    try:
        data = pandas.read_csv(Reader(islice(fp, sz)), dtype=int, header=None).values[0]
    except ValueError:
        return None
    data = data - last
    data[0] += last[0]
    return data

#columns = ["end-time", "samples", "median", "90%", "95%", "99%"]
percs   = [50, 90, 95, 99]

def main(ctx):
    fps  = [open(f, 'r') for f in ctx.FILE]
    arrs = {fp: __read_hist_csv_last for fp in fps}

    arr = np.zeros(1217)
    while True:
        arrs = {fp: read_hist_csv(fp, 1, last=arrs[fp]) for fp in fps}
        merged = np.sum(np.array(arrs.values()), axis=0)[1:]
        ps = percentile(percs, merged)
        print (arrs.values()[0][0],ps)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    arg = p.add_argument
    arg('FILE', help='space separated list of histogram log filenames', nargs='+')
    main(p.parse_args())

