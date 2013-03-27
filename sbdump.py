#!/usr/bin/python -i

import dfrpgmon2 as dm
import yaml
def j(c): dm.run_command(c,"med",dm.GAME,dm.COMMANDS)
j(".load sb.pkl")
yaml.dump(dm.GAME,open("sb-dump.yml",'w'),yaml.CDumper)

