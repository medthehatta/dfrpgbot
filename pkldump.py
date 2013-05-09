#!/usr/bin/python -i

import dfrpgmon2 as dm
import pickle
import yaml
import sys

if len(sys.argv)<2:
  print("Not enough arguments")
  sys.exit(1)

pfile = sys.argv[1]

yaml.dump(pickle.load(open(pfile,'rb')),open("{0}-dump.yml".format(pfile),'w'),yaml.CDumper)

