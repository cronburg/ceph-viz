#!/usr/bin/env python
import csv
import sys
import numpy as np

# Print lengths of each row in a csv file
with open(sys.argv[1], 'r') as f:
  rdr = csv.reader(f, delimiter=',')
  #for x in rdr:
  #  print(x[0],x[:10])
  data = [row for row in rdr][1:]
  print(map(len, data))
  
  ds = [np.array(data[i]) for i in range(len(data))]
  print(ds[1])
  #print(map(lambda x: x[0], data))

