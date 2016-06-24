#!/usr/bin/python
#
# fiologparser.py
#
# This tool lets you parse multiple fio log files and look at interaval
# statistics even when samples are non-uniform.  For instance:
#
# fiologparser.py -s *bw*
#
# to see per-interval sums for all bandwidth logs or:
#
# fiologparser.py -a *clat*
#
# to see per-interval average completion latency.

import argparse
import math

USEC_PER_MILLISEC = 1000.0  # microseconds per millisecond


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', required=False, type=int, default=1000, help='interval of time in seconds.')
    parser.add_argument('-d', '--divisor', required=False, type=int, default=1, help='divide the results by this value.')
    parser.add_argument('-f', '--full', dest='full', action='store_true', default=False, help='print full output.')
    parser.add_argument('-A', '--all', dest='allstats', action='store_true', default=False, 
                        help='print all stats for each interval.')
    parser.add_argument('-a', '--average', dest='average', action='store_true', default=False, help='print the average for each interval.')
    parser.add_argument('-s', '--sum', dest='sum', action='store_true', default=False, help='print the sum for each interval.')
    parser.add_argument('-D', '--debug', dest='debug', action='store_true', default=False, help ='print intermediate variables')
    parser.add_argument("FILE", help="collectl log output files to parse", nargs="+")
    args = parser.parse_args()
    return args

# this contains all latency samples for this interval from ALL LOG FILES

class Interval():
    def __init__(self, ctx, start, end, series):
        self.ctx = ctx
        self.start = start
        self.end = end
        self.samples = []
        self.weight_sum = None  # force initialization
        self.is_sorted = False

    # defer sorting samples until you know that at least 
    # one method that requires this is being used

    def ensure_sorted(self):
        if not self.is_sorted:
            if len(self.samples) > 2:
                self.samples.sort(key = lambda x : x.value)
            self.weight_sum = sum([s.get_weight(self.start, self.end)
                                   for s in self.samples])
            self.is_sorted = True

    def get_min(self):
        self.ensure_sorted()
        return self.samples[0].value if len(self.samples) > 0 else None

    def get_max(self):
        self.ensure_sorted()
        last_idx = len(self.samples) - 1
        return self.samples[last_idx].value if last_idx >= 0 else None

    def get_count(self):
        return len(self.samples)

    def get_wa(self, weight):
        return sum([ sample.value * sample.get_weight(self.start, self.end)
                      for sample in self.samples]) / float(weight)

    def get_wa_list(self):
        return self.get_wa(1)

    def get_wa_sum(self):
        return sum([ sample.value * sample.get_weight(self.start, self.end) 
                      for sample in self.samples ])

    def get_wa_avg(self):
        return float(self.get_wa_sum()) / len(self.samples)

    def get_wp(self, p):
        #import pdb; pdb.set_trace()
        self.ensure_sorted()
        if self.ctx.debug:
            print('get_wp: pct=%f, start=%f, end=%f, wsum=%f' % 
                   (p, self.start, self.end, self.weight_sum))
        if len(self.samples) == 1:
            return self.samples[0].value  # same value no matter what p is
        weight = 0.0
        last = None
        cur = None

        # first find the two samples that straddle the percentile based on weight
        for sample in self.samples:
            if weight >= self.weight_sum * p:
                break
            weight += sample.get_weight(self.start, self.end)
            #assert( weight <= self.weight_sum )
            last = cur
            cur = sample
        if cur == None:
            # this can only happen if weight == 0.0, 
            # we can only exit loop if p == 0.0.  Then just return min value
            # since samples are sorted by value, then this is first element
            return sample.value
        if last == None:
            # this can only happen if interval has 1 value,  
            # just return that value
            return cur.value

        # next find weights based inversely on the distance to the percentile boundary
        wgt_before = weight - cur.get_weight(self.start, self.end)
        wgt_diff = weight - wgt_before
        pct_before = wgt_before / self.weight_sum
        pct_after = weight / self.weight_sum
        if self.ctx.debug:
            print('get_wp: wb=%f wd=%f pb=%f pa=%f' % (
                  wgt_before, wgt_diff, pct_before, pct_after))
        #assert( p >= pct_before )
        #assert( p <= pct_after )
        #assert( wgt_diff > 0.0 )
        # use linear interpolation to get percentile value
        return (last.value + 
                ((cur.value - last.value) * 
                 (p - pct_before)/(pct_after - pct_before)))

# this class corresponds to processing of latency log files
# all latencies from all log files are merged into a single
# sequence of Interval objects corresponding to time intervals in test
# we then only need to sort samples in each interval object to get 
# all percentiles, median, min, and max for each interval

class TimeSeries():
    max_interval_num = -1
    intervals = []   # array of time intervals containing samples
    def __init__(self, ctx, fn):
        self.ctx = ctx
        self.last = None 
        self.read_data(fn)

    @staticmethod
    def get_ftime():
        # sample with longest end time is included in last time interval,
        # only have to look there
        last_interval = TimeSeries.intervals[TimeSeries.max_interval_num]
        chrono_sort = sorted(last_interval.samples, key = lambda s : s.end)
        ftime = chrono_sort[len(chrono_sort)-1].end
        return ftime

    def read_data(self, fn):
        f = open(fn, 'r')
        p_time = 0
        for line in f:
            (time, value, foo, bar) = line.rstrip('\r\n').rsplit(', ')
            itime = int(time)
            ivalue = int(value)
            end_time = itime + (ivalue / USEC_PER_MILLISEC)
            self.add_sample(itime, end_time, ivalue)
 
    def add_sample(self, start, end, value):
        interval_duration = self.ctx.interval   # integer
        sample = Sample(self.ctx, start, end, value)
        if not self.last or self.last.end < end:
            self.last = sample
        end_intvl = int(end / interval_duration)
        if TimeSeries.max_interval_num < end_intvl:
            TimeSeries.max_interval_num = end_intvl # where last interval is

        # so .intervals list is at least long enough to hold last interval
        if len(TimeSeries.intervals) <= end_intvl:
            # we don't know yet how long this list must be
            # extend interval array by 20 + 2 * intvl
            # so time spent extending is O(1)
            extra_length = 20 + 2 * end_intvl
            appended_elements = [ None for j in range(0, extra_length) ]
            self.intervals.extend(appended_elements)

        # add sample to each interval overlapping it

        intvl = int(start / interval_duration)
        intvl_start = int(intvl * interval_duration)
        while end > intvl_start:
            intvlobj = self.intervals[intvl]
            if intvlobj == None:
                intvl_start = intvl * interval_duration
                intvl_end = intvl_start + interval_duration
                intvlobj = Interval(self.ctx, intvl_start, intvl_end, [])
                self.intervals[intvl] = intvlobj
            intvlobj.samples.append(sample)
            intvl += 1
            intvl_start += interval_duration

class Sample():
    def __init__(self, ctx, start, end, value):
        self.ctx = ctx
        self.start = start
        self.end = end
        self.value = value

    def get_weight(self, start, end):
        # short circuit if not within the bound
        if (end < self.start or start > self.end):
            return 0
        sbound = self.start if start < self.start else start
        ebound = self.end if end > self.end else end
        weight = float(ebound-sbound) / (self.end - self.start)
        #print('ist=%f, iend=%f, v=%f, s=%f, e=%f, sbnd=%f, ebnd=%f, w=%f' % 
        #         (start, end, 
        #          self.value, self.start, self.end, sbound, ebound, weight))
        return weight

class Printer():
    def __init__(self, ctx):
        self.ctx = ctx
        self.ffmt = "%0.3f"

    def format(self, data):
        if isinstance(data, float) or isinstance(data, int):
            data = data / self.ctx.divisor
            return self.ffmt % data
        return data

    def print_full(self):
        for i in TimeSeries.intervals:
          if i != None:
            print "%s, %s" % (self.ffmt % i.end, i.get_wa(1))

    def print_sums(self):
        for i in TimeSeries.intervals:
          if i != None:
            print "%s, %s" % (self.ffmt % i.end, self.format(i.get_wa_sum()))


    def print_averages(self):
        for i in TimeSeries.intervals:
          if i != None:
            print( "%s, %s" % 
                       (self.ffmt % i.end, self.format(i.get_wa_avg())))

    def print_all_stats(self):
        print('end-time, samples, min, avg, median, 90%, 95%, 99%, max')
        for i in TimeSeries.intervals:
            if i != None:
             if len(i.samples) > 1:
              print(', '.join([
                self.ffmt % i.end,
                "%d" % i.get_count(),
                self.format(i.get_min()),
                self.format(i.get_wa_avg()),
                self.format(i.get_wp(0.5)),
                self.format(i.get_wp(0.9)),
                self.format(i.get_wp(0.95)),
                self.format(i.get_wp(0.99)),
                self.format(i.get_max())
            ]))

    def print_default(self):
        interval = TimeSeries.intervals[0]
        print self.format(interval.get_wa_sum())



def mainprog():
    ctx = parse_args()
    for fn in ctx.FILE:
        TimeSeries(ctx, fn)

    p = Printer(ctx)

    if ctx.sum:
        p.print_sums()
    elif ctx.average:
        p.print_averages()
    elif ctx.full:
        p.print_full()
    elif ctx.allstats:
        p.print_all_stats()
    else:
        p.print_default()

if __name__ == '__main__':
    mainprog()

