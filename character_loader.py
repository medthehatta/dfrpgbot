import dfrpgmon2 as dm
import pickle

def make_game(name,characters,pickle):
  G = dm.FATEGAME(config={'pickle':pickle})
  G.config['title']=name
  G.config['revisionfile']=''
  for c in characters:
    G.add(c,c.name.replace(" ","_"))
  G.save()
  return G

def make_char(name,health,composure,refresh):
  char = dm.Character(name,NPC=False)
  char.stress={}
  char.stress['p'] = dm.StressTrack('Physical',boxes=health)
  char.stress['m'] = dm.StressTrack('Mental',boxes=composure)
  char.fate.refresh=refresh
  char.fate.fate=refresh
  return char
