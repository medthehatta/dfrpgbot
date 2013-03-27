#!/usr/bin/python -i

import dfrpgmon2 as dm
import yaml
def j(c): dm.run_command(c,"med",dm.GAME,dm.COMMANDS)
j(".load sb.pkl")
GAME = yaml.load(open("sb-dump.yml"),yaml.CLoader)
GAME.save()

