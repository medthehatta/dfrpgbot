from functools import reduce
import random
import re
import pickle

class StressTrack(object):
  """
  CLASS STRESS_TRACK
  This object keeps track of stress: mental, physical, social, hunger.
  """
  def __init__(self,name="Stress",boxes=2,persist=False,shortname=None):
    self.name = name       #what to call this stress track
    self.boxes = boxes     #number of available boxes
    self.persist = persist #does this persist after conflict?
    self.shortname = shortname or str(name[0]).upper() #how the track is displayed
    self.checked = []      #which boxes are currently checked

  def check(self,box=1):
    """
    Check the box specified, unless it
    falls off the stress track
    """
    while box in self.checked: box+=1
    if box <= self.boxes:
      self.checked.append(box)
      return self

  def clear(self,box=None): 
    """
    Clear either the specified box or
    the whole stress track
    """
    if box:
        try:
          self.checked.remove(box)
        except ValueError:
          return None
    else:
      self.checked = []
    return self

  def __str__(self):
    """
    How to print the stress track.
    """
    delim=" "; unchk="o"; chk="x"
    track = []
    for i in range(1,self.boxes+1):
      if i in self.checked:
        track.append(chk)
      else:
        track.append(unchk)
    return "({0}) ".format(self.shortname) + delim.join(track)

class Aspect(object):
  """
  CLASS ASPECT
  This object keeps track of aspects on a game element.
  How the flags are actually USED is up to the implementation
  of the invocation function.
  """
  def __init__(self,name,flags=[],persist=False):
    self.name = str(name)
    self.persist = persist
    self.flags = []
    self.flag_transformers = {"ConsMild":(["mild"],True)
                             ,"ConsMod":(["moderate"],True)
                             ,"ConsModerate":(["moderate"],True)
                             ,"ConsSevere":(["severe"],True)
                             ,"ConsSev":(["severe"],True)
                             ,"fragile":(["f"],False)
                             ,"style":(["#","#"],None)
                             }
    for f in flags: 
      flag = self.fix_flag(f) 
      self.flags.extend(flag[0])
      if flag[1] != None:
        self.persist = flag[1]

  def __str__(self):
    return " ".join(["({0})".format(f) for f in self.flags]+[self.name])

  def drop_flag(self,flag):
    if flag.lower() in self.flags:
      self.flags.remove(flag.lower())
      return self

  def fix_flag(self,flag):
    xformer = self.flag_transformers.get(flag) or self.flag_transformers.get(flag.lower()) or ([flag],None)
    return (xformer[0],xformer[1])
      

class Fate(object):
  """
  CLASS FATE
  Just fate and refresh
  """
  def __init__(self,refresh=1,fate=None):
    self.refresh = refresh
    self.fate = fate or self.refresh

  def dorefresh(self):
    if self.fate<self.refresh: self.fate=self.refresh
    return self

  def increment(self,d=1):
    if self.fate+d<0:
      return None
    else:
      self.fate+=d
      return self.fate

  def __str__(self):
    return "(FP) {0}/{1}".format(self.fate,self.refresh)

class TurnOrdering(object):
  """
  CLASS TURNORDERING
  Holds characters in a turn order and allows display etc
  """
  def __init__(self):
    self.index = None
    self.ordering = []

  def insert(self,*chis):
    for (initiative,character) in chis:
      if not initiative: initiative=0
      if character not in [a[1] for a in self.ordering]:
        self.ordering.append((initiative,character))
      if self.index == None:
        self.ordering.sort(key=lambda ch: ch[0]+random.random(),reverse=True)
    return self

  def __iter__(self):
    return iter([c[1] for c in self.ordering])

  def __getitem__(self,k):
    "Return the character at 1-BASED index k"
    return self.ordering[k-1][1]

  def establish(self,start=0):
    "Zeros the index"
    if self.ordering: #should probably do more thorough sanity checks
      self.index = start
      return self

  def stop(self):
    "Unsets the index, effectively freezing advancement"
    self.index = None
    return self

  def current(self):
    "Returns the current character"
    if self.index!=None:
      return self.ordering[self.index][1]

  def advance(self,d=1):
    """"
    Advances the index, wrapping to the beginning
    of the list if necessary
    """
    if self.index!=None:
      self.index = (self.index + d) % len(self.ordering)
      return self

  def claim_turn(self,ch):
    """
    Claims the turn at the current spot for character ch
    """
    if self.index!=None:
      # look up the ch in the order
      chi = [s[1] for s in self.ordering].index(ch)
      # adjust the index for the list with a missing element
      if chi<=self.index: 
        self.index = self.index - 1
      # pop and reinsert at new location
      self.ordering.insert(self.index, self.ordering.pop(chi))
      return self

  def drop_current(self):
    "Removes the current entry in the order"
    if self.index!=None:
      self.ordering.pop(self.index)
      if len(self.ordering)==0:
        self.index = None
      else:
        self.index = (self.index % len(self.ordering))
      return self

  def reset(self):
    "Clears the order"
    self.ordering=[]
    self.index=None
    return self

  def __str__(self):
    "Display the turn order"
    if self.ordering:
      lines = ["{i}.{ch}".format(i=i,ch=ch[1]) 
                for (i,ch) in zip(range(1,len(self.ordering)+1),self.ordering)]
      # put a box around the current player if index exists
      if self.index!=None:
        def marked(s): return "["+s+"]"
        lines[self.index]=marked(lines[self.index])
      return " ".join(lines)
    else:
      return "No turn order established yet."

class Character(object):
  """
  One DFRPG character, PC or NPC
  """
  def __init__(self,name,NPC=True):
    self.name=str(name)
    self.NPC=NPC
    self.fate = Fate(3)
    self.stress = \
      dict([(n[0].lower(),StressTrack(n)) 
        for n in ["Physical","Mental","Social"]])
    self.aspects = {}

  def __str__(self):
    return str(self.name)

  def status(self):
    dlim=" | "
    def stress_order(s): 
      return (list("PMS")+[s.shortname]).index(s.shortname)
    def aspectpp(asp): return "[{0}]".format(asp)

    if self.NPC:
      stat = [self.name.upper(),
              str(self.fate),
              "  ".join(map(aspectpp, self.aspects.values()))]
    else:
      stat = [self.name.upper(),
              dlim.join(map(str,
                sorted(self.stress.values(),key=stress_order))),
              str(self.fate),
              "  ".join(map(aspectpp, self.aspects.values()))]
    return dlim.join(stat[:-1])+"\n"+stat[-1]

  def conflict_cleanup(self):
    # stress
    for s in self.stress.values():
      if not s.persist: s.clear()

    # aspects
    newaspects = {}
    for s in self.aspects:
      if self.aspects[s].persist:
        if "#" not in self.aspects[s].flags and "f" not in self.aspects[s].flags:
          self.aspects[s].flags.append("#") # restore free invoke
        newaspects.update([(s,self.aspects[s])])
    self.aspects.clear()
    self.aspects.update(newaspects)
    return self

  def add_aspect(self,name,persist=False,flags=None):
    if "#" not in flags and "fragile" not in flags and "style" not in flags: flags.append("#") # one free invoke
    self.aspects[name.lower()] = Aspect(name,flags,persist)
    return self

  def del_aspect(self,name):
    asp = self.aspects.get(name.lower())
    if asp:
      self.aspects.pop(asp.name.lower()) 
      return self

  def add_fate(self):
    if self.fate.increment(): return self

  def del_fate(self):
    if self.fate.increment(-1)!=None: return self

  def add_stress(self,track,amt):
    stress = self.stress.get(track.lower())
    if stress:
      if stress.check(amt):
        return self

  def del_stress(self,track,amt=None):
    stress = self.stress.get(track.lower())
    if stress:
      if stress.clear(amt):
        return self

  
    
class Lookup(object):
  "Used for looking up objects by aliases.  Mostly characters."
  def __init__(self,characters=None):
    self._aliases={}
    self._nicks={}
    self.characters=[]
    if characters:
      for c in characters:
        self.add(c,player=str(c))

  def __iter__(self):
    "Iterable of the characters in alphabetic order."
    return iter(sorted(self.characters,key=str))

  def __getitem__(self,alias):
    "Looks up a character from its alias"
    a=alias.strip().lower()
    if a in self._aliases:
      return self._aliases[a]

  def __str__(self):
    return str(sorted([str(c) for c in self]))
  def __repr__(self):
    return self.__str__() 

  def nick(self,character):
    "Looks up a nick for a character"
    if type(character)==Character:
      #passed a character directly
      n=str(character)
    else:
      #passed a character name (an alias)
      n=self[character]
    return self._nicks.get(n)

  def add(self,character,player=None):
    "Adds a character to the game"
    if character not in self.characters: 
      self.characters.append(character)
      self._aliases[str(character).lower()]=character
      if player:
        self.alias_nick(str(character),player)
      return character

  def alias(self,target,alias):
    "Adds an alias for an already existing character"
    t=target.lower()
    a=alias.lower()
    if t in self._aliases:
      self._aliases[alias.lower()]=self._aliases[t]
      return self

  def alias_nick(self,target,nick):
    """
    Adds an alias for the irc nick, and also a backwards lookup
    to get from the character to the nick
    """
    n=nick+'#nick'
    if self.alias(target,n):
      self._nicks[str(self[n])]=nick
      return self

  def pop(self,character):
    "Pops (and removes) a character from the lookup table"
    if character in self.characters:
      lookupname = str(character).lower()
      self.characters.remove(character)
      if lookupname in self._nicks:
        self._nicks.pop(lookupname)
      if lookupname+"#nick" in self._nicks:
        self._nicks.pop(lookupname+"#nick")
      for k in [kk for kk in self._aliases if self._aliases[kk]==character]:
          self._aliases.pop(k)
      return character

class PlayerDice(object):
  def __init__(self):
    self.rolls = {}

  def roll(self,character,spec):
    base  = list(map(random.choice,[[-1,0,1]]*4))
    boons = list(map(int,re.findall(r'(?:\+|\-)[0-9]+',spec)))
    self.rolls[character] = sum(base) + sum(boons)
    
    dbase = " ".join([{1:"+",0:"0",-1:"-"}[b] for b in base])
    dboons = " ".join(["{0:+}".format(b) for b in boons])

    if dboons:
      return "{0} rolled: [{1}] {{{2}}} ({3}) = {{{4}}}".format(character,dbase,sum(base),dboons,self.rolls[character])
    else:
      return "{0} rolled: [{1}] {{{2}}} = {{{3}}}".format(character,dbase,sum(base),self.rolls[character])

  def amend(self,character,spec):
    if self.rolls.get(character)!=None:
      old = self.rolls[character]

      boons = list(map(int,re.findall(r'(?:\+|\-)[0-9]+',spec)))
      self.rolls[character] = old + sum(boons)
      
      if not boons: boons=[0]
      dboons = " ".join(["{0:+}".format(b) for b in boons])

      return "{0} rolled: {{{1}}} ({2}) = {{{3}}}".format(character,old,dboons,self.rolls[character])





## GLOBALS ##
class FATEGAME(object):
  def __init__(self,characters=[],rolling=PlayerDice(),order=TurnOrdering(),config={}):
    self.lookup = Lookup(characters)
    self.characters = characters
    self.config = config
    self.rolling = rolling
    self.order = order

  def add(self,character,nick):
    self.lookup.add(character)
    self.lookup.alias_nick(str(character),nick)
    if character not in self.characters:
      self.characters.append(character)
      return character
  
  def npc_purge(self):
    npcs = [c for c in self.characters if c.NPC]
    for c in npcs:
      self.characters.remove(c)
      self.lookup.pop(c)
    return self

  def load(self):
    if self.load_revisions(self.config['revisionfile']):
      return self

  def save(self,redir=None):
    picklepath = redir or self.config.get('pickle')
    if picklepath:
      picklefile = open(picklepath,'wb')
      if picklefile:
        pickle.dump(self,picklefile)
        return self

  def load_revisions(self,revpath): 
    pass

  def cleanup(self):
    self.rolling = PlayerDice()
    self.order = TurnOrdering()
    for c in self.characters:
      c.conflict_cleanup()
    return self

def parse(s,rexes=[r'^\.(\S+)',r'\((\S+)\)',r'\@ (\S+)']):
  """
  Takes phenny input and returns the requested token
  matches, plus the rest of the stuff in the match
  """
  rest = reduce(lambda S,r: re.sub(r,'',S), rexes, s).strip()
  return [re.findall(r,s) for r in rexes] + [rest]

def say(lines,phenny=None):
  "Say multiple lines with phenny"
  lines = lines.strip()
  for l in lines.split("\n"):
    if phenny:
      phenny.say(l)
    else:
      print(l)

def run_command(st,nick,GAME,COMMANDS,phenny=None):
  (commands,flags,character1,args) = parse(st)
  try:
    cmd1 = commands[0]
  except Exception:
    return None

  # lookup character
  try:
    character = GAME.lookup[character1[0]] or GAME.lookup[nick+"#nick"] or GAME.lookup[nick]
  except Exception:
    try:
      character = GAME.lookup[nick+"#nick"] or GAME.lookup[nick]
    except Exception:
      character = None

  # lookup command
  cmd = COMMANDS.get(cmd1)
  if cmd:
    if not GAME and cmd!=load_game:
      say("Game not loaded.  Load with .load <gamefile>",phenny)
      return 
    ret = cmd(GAME,args,character,nick,flags)
    if GAME: GAME.save()
    if ret!=None:
      if type(ret)==Character:
        say(ret.status(),phenny)
      else:
        say(str(ret),phenny)

def phenny_hook(phenny,input):
  #please let the closure work
  run_command(str(input),input.nick,GAME,COMMANDS,phenny=phenny)
phenny_hook.rule = r'.*'
phenny_hook.threaded = False
  
def load_game(GAME_,args,character,nick,flags):
  global GAME
  GAME = pickle.load(open(args,'rb'))
  if type(GAME)==FATEGAME:
    GAME.load()
    num_players = len([c for c in GAME.characters if not c.NPC])
    num_npcs    = len(GAME.characters) - num_players
    short_status = "Loaded: {0}\n{1} PCs, {2} NPCs.  {3} players in turn order.".format(\
      GAME.config['title'], num_players, num_npcs, len(GAME.order.ordering))
    return short_status

## IRC COMMANDS ##
def c_cleanup(GAME,args,character,nick,flags): 
  GAME.cleanup()
  return "Stress, temporary aspects, and turn order cleared."
def c_add_npc(GAME,args,character,nick,flags): return GAME.add(Character(args),nick)
def c_del_npc(GAME,args,character,nick,flags): 
  # lookup by argument first, so you don't need @
  character = GAME.lookup[args] or character
  # remove if the character is an npc
  if character and character.NPC: 
    GAME.characters.remove(character)
    GAME.lookup.pop(character)
    return "Removed {0}".format(character)
def c_npc_purge(GAME,args,character,nick,flags): 
  GAME.npc_purge()
  return "NPCs purged."
def c_roll(GAME,args,character,nick,flags): return GAME.rolling.roll(character,args)
def c_amend(GAME,args,character,nick,flags): return GAME.rolling.amend(character,args)
def c_add_aspect(GAME,args,character,nick,flags): 
  if character:
    return character.add_aspect(args,flags=flags)
def c_add_persist_aspect(GAME,args,character,nick,flags):
  if character:
    return character.add_aspect(args,flags=flags,persist=True)
def c_del_aspect(GAME,args,character,nick,flags): 
  if character:
    return character.del_aspect(args)
def c_tag(GAME,args,character,nick,flags): 
  if character:
    largs = args.lower()
    if character.aspects.get(largs): 
      if "#" in character.aspects[largs].flags:
        character.aspects[largs].flags.remove("#") 
      elif "f" in character.aspects[largs].flags:
        character.aspects.pop(largs)
      # can tag for roll bonus or not
      if "noroll" in flags:
        return character
      else:
        amended = GAME.rolling.amend(GAME.lookup[str(nick)+"#nick"],"+2")
        return amended or character
def c_stats(GAME,args,character,nick,flags): 
  flags = " ".join(flags) + args #search through the whole shebang
  if "all" in flags:
    return c_all_stats(GAME,args,character,nick,flags)
  elif "npc" in flags or "npcs" in flags:
    return c_show_npcs(GAME,args,character,nick,flags)
  elif "pc" in flags or "pcs" in flags:
    return c_show_pcs(GAME,args,character,nick,flags)
  else:
    character = GAME.lookup[args] or character
    return character.status()
def c_all_stats(GAME,args,character,nick,flags): return "\n".join(sorted([str(c.status()) for c in GAME.characters]))
def c_show_npcs(GAME,args,character,nick,flags): return "\n".join([str(c.status()) for c in GAME.characters if c.NPC])
def c_show_pcs(GAME,args,character,nick,flags): return "\n".join([str(c.status()) for c in GAME.characters if not c.NPC])
def c_add_fp(GAME,args,character,nick,flags): 
  if character:
    character.add_fate()
    return character
def c_del_fp(GAME,args,character,nick,flags): 
  if character:
    character.del_fate()
    return character
def c_refresh(GAME,args,character,nick,flags): 
  for c in GAME.characters: c.fate.dorefresh()
  return "Ahhhhhhh.  Refreshing."
def c_alias(GAME,args,character,nick,flags): 
  GAME.lookup.alias(str(character),args)
  return "{0} is now also known as {1}".format(str(character),args)
def c_im(GAME,args,character,nick,flags): 
  character = GAME.lookup[args] or character
  if character:
    GAME.lookup.alias_nick(str(character),nick)
    return "{0} is now {1}.".format(nick,str(character))
def c_copy(GAME,args,character,nick,flags):
  source = GAME.lookup[args]
  if source and character:
    character.stress['p'].checked = source.stress['p'].checked[:]
    character.stress['m'].checked = source.stress['m'].checked[:]
    character.stress['s'].checked = source.stress['s'].checked[:]
    character.fate.fate = source.fate.fate
    character.aspects = {}
    character.aspects.update(source.aspects)
    return character
  else:
    if not character:
      return "Target character is invalid."
    else:
      return "Source character is invalid."
def c_add_stress(GAME,args,character,nick,flags): return character.add_stress(flags[0],int(args))
def c_del_stress(GAME,args,character,nick,flags): return character.del_stress(flags[0],int(args))
def c_whosturn(GAME,args,character,nick,flags):
  if GAME.order.index!=None:
    return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
  else:
    return str(GAME.order)
def c_ordered(GAME,args,character,nick,flags): 
  GAME.order.establish()
  return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
def c_next(GAME,args,character,nick,flags): 
  if GAME.order.advance():
    return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
  else:
    return "Turn order empty or inactive.  To activate, run .done_ordering"
def c_back(GAME,args,character,nick,flags): 
  if GAME.order.advance(-1):
    return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
  else:
    return "Turn order empty or inactive.  To activate, run .done_ordering"
def c_add_order(GAME,args,character,nick,flags): 
  # compute the net alertness like you would a die roll
  boons = sum(map(int,re.findall(r'(?:\+|\-)[0-9]+',args)))
  return GAME.order.insert((boons,character))
def c_del_order(GAME,args,character,nick,flags): 
  if GAME.order.drop_current():
    return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
  else:
    return str(GAME.order)
def c_reset_order(GAME,args,character,nick,flags):
  return GAME.order.reset()
def c_claim(GAME,args,character,nick,flags): 
  character = GAME.lookup[args] or character
  GAME.order.claim_turn(character)
  if GAME.order.index!=None:
    return "{0}: {1}".format(GAME.lookup.nick(GAME.order.current()) or GAME.order.current(),GAME.order)
  else:
    return str(GAME.order)
def c_stop_order(GAME,args,character,nick,flags):
  return GAME.order.stop()
COMMANDS = {\
"load": load_game #since GAME isn't defined yet, this one is different
,"clean":c_cleanup
,"pcs":c_show_pcs
,"npcs":c_show_npcs
,"npc+":c_add_npc
,"npc":c_add_npc
,"npc-":c_del_npc
,"npcclean":c_npc_purge
,"npc#":c_npc_purge
,"roll":c_roll
,"amend":c_amend
,"aspect+":c_add_aspect
,"aspect":c_add_aspect
,"aspect-":c_del_aspect
,"sticky+":c_add_persist_aspect
,"sticky":c_add_persist_aspect
,"sticky-":c_del_aspect
,"tag":c_tag
,"invoke":c_tag
,"stats":c_stats
,"status":c_stats
,"all":c_all_stats
,"fp+":c_add_fp
,"fp-":c_del_fp
,"refresh":c_refresh
,"alias":c_alias
,"i'm":c_im
,"copy":c_copy
,"stress+":c_add_stress
,"stress":c_add_stress
,"stress-":c_del_stress
,"whosturn":c_whosturn
,"show_ordering":c_whosturn
,"show_order":c_whosturn
,"stop":c_stop_order
,"ordered":c_ordered
,"done_ordering":c_ordered
,"next":c_next
,"back":c_back
,"order+":c_add_order
,"order":c_add_order
,"order-":c_del_order
,"remove_from_order":c_del_order
,"reset_order":c_reset_order
,"claim":c_claim
,"claim_turn":c_claim
}
GAME = None
