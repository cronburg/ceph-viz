#!/usr/bin/env python
import json
import csv
import sys
import os

def csv_to_json(csv_fn, json_fn, fields):
  with open(csv_fn, 'r') as csv_file, open(json_fn, 'w') as json_file:
    reader = csv.DictReader(csv_file, fields)
    json.dump(line, jsonfile) for line in reader

if __name__ == "__main__":

  def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv-filename', help='name of the CSV file to convert')
    parser.add_argument('json-filename', required=False, help='name of output file')
    parser.add_arguemtn('fields', nargs='+', help='list of column (field) names in the CSV file')

  if len(sys.argv) == 1:
    print "Usage: %s csv-filename [json-filename]"
    exit(1)

  csv_fn = sys.argv[1]
  if len(sys.argv) > 2
    json_fn = sys.argv[2]
  else:
    # Rename to 'filename.json' by default:
    json_fn = os.path.splitext(csv_fn)[0] + '.json'
  
  csv_to_json(csv_fn, json_fn, 

