import numpy as np
import os
from os import listdir
from os.path import isfile, join
import re
import pdb
DEF_PROGRESS = True

get_files_in = lambda path: [f for f in listdir(path) if isfile(join(path, f))]

def get_files_in_dir_matching(directory, regex, matches=False):
  fs = get_files_in(directory)
  ms = [(fn,re.match(regex,fn)) for fn in fs]
  ms = [m for m in ms if m[1] != None]
  if matches: return ms
  return [m[0] for m in ms]

def load_fio_file(fn):
  return np.genfromtxt(fn, delimiter=',', dtype=int)

def load_all_fio_files(fns, progress=DEF_PROGRESS):
  data = []
  for i,log_fn in enumerate(fns):
    arr = load_fio_file(log_fn)
    data.extend(arr)
    if progress: print "Loaded: %03d/%03d" % (i,len(fns))
  return data

def sort_data(data, by, progress=DEF_PROGRESS):
  print "Sorting..."
  data = sorted(data, key=by)
  print "Done sorting."
  return data

def makedirs(path):
  """ http://stackoverflow.com/a/14364249 """
  try: 
      return os.makedirs(path)
  except OSError:
      if not os.path.isdir(path):
          raise

