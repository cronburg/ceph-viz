#!/usr/bin/env python
from helpers import *
import numpy as np

# In this order for headless server:
import matplotlib
matplotlib.use("Agg")
import pylab as p

coarse = load_fio_file("out/fiologparser-coarse.csv", dtype=float)
exact  = load_fio_file("out/fiologparser-exact.csv", dtype=float)

mx = min(len(coarse), len(exact))

coarse_vals = coarse[:, 2:9] [:mx]
exact_vals  = exact[:, 2:9]  [:mx] 

errors = abs(1.0 * (exact_vals - coarse_vals) / exact_vals)

labels = ["min", "avg", "median", "90%", "95%", "99%", "max"]
colors = "bgrcmykw"

print errors.tolist()

t_errors = np.transpose(errors)
t_coarse_vals = np.transpose(coarse_vals)
t_exact_vals = np.transpose(exact_vals)

# Plot errors of coarse vs exact:
for i,err in enumerate(t_errors):
  x = exact[:,0][:mx]
  y = 100.0 * err
  p.plot(x, y, '-o', label=labels[i], c=colors[i])
p.legend()
p.xlabel("time (msec)")
p.ylabel(r"Percent Error")
p.ylim([-10,100])
p.title("fiologparser Coarse vs Exact (10x sample sizes, same data set)")
p.savefig("out/fiologparser-coarse-vs-exact-errors.png")
p.close()

#for i in range(len(labels)):
fig, axes2d = p.subplots(nrows=2, ncols=3, sharex=True, sharey=True, figsize=(8*3, 8))
#fig.xlabel("time (msec)")
#fig.ylabel(r"Latency (msec)")
for i,(cval,ex_val,err) in enumerate(zip(t_coarse_vals, t_exact_vals, t_errors)):
  p.subplot(2, 4, i) # 2 vertical, 4 horizontal, select subplot #i

  # Plot coarse values with error bars:
  x = coarse[:,0][:mx]
  y = cval
  yerr = err * ex_val
  p.errorbar(x, y, yerr=yerr, label=labels[i], c=colors[i])
  #p.legend(loc=4)
  #p.xlabel("time (msec)")
  #p.ylabel(r"Latency (msec)")
  p.ylim([00000,100000])
  p.title(labels[i])
p.savefig("out/fiologparser-coarse-vs-exact-latencies.png")
p.close()


#exact_vals = exact[:,i]
#error = [(c - e) / e for (c,e) in zip(coarse_vals,exact_vals)]
#print coarse_vals

print "Average samples coarse:", np.average(coarse[:,1])
print "Average samples exact:", np.average(exact[:,1])

