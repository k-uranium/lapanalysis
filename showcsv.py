import csv
import sys
import os

if len(sys.argv) != 2:
    exit()

path = sys.argv[1]

with open(os.path.join(path, '平均指数表.csv')) as f:
    reader = csv.reader(f)
    for row in reader:
        print(row[0], *row[9:])
