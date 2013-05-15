import dfrpgmon2 as dm
import pickle
import sys

def make_game(name,characters,pickle):
  G = dm.FATEGAME(config={'pickle':pickle})
  G.config['title']=name
  G.config['revisionfile']=''
  for c in characters:
    G.add(c,c.name.replace(" ","_"))
  G.save()
  return G

def make_char(name,refresh=1,health=2,composure=2,hunger=None):
  char = dm.Character(name,NPC=False)
  char.stress={}
  char.stress['p'] = dm.StressTrack('Physical',boxes=health)
  char.stress['m'] = dm.StressTrack('Mental',boxes=composure)
  if hunger:
    char.stress['h'] = dm.StressTrack('Hunger',boxes=hunger,persist=True)
  char.fate.refresh=refresh
  char.fate.fate=refresh
  return char

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Not enough arguments.  Need pickle file, number of chars.")
        sys.exit(1)
    
    (game,pickle,raw_numchars) = sys.argv
    numchars = int(raw_numchars)

    characters = [make_char("Character{0}".format(i)) for i in range(1,1+numchars+1)]
    make_game("New DFRPG Game",characters,pickle)
    sys.exit(0)
