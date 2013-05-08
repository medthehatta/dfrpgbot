#!/usr/bin/python -i

import dfrpgmon2 as dm
import yaml
import sys

if len(sys.argv)<2:
  print("Not enough arguments")
  sys.exit(1)

pickle = sys.argv[1]

def j(c): dm.run_command(c,"med","##dfrpg",dm.GAME,dm.COMMANDS)
j(".load {0}".format(pickle))
GAME = yaml.load(open("{0}-dump.yml".format(pickle)),yaml.CLoader)
GAME.save()



