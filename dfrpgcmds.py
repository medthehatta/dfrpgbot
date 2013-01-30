## IRC COMMANDS ##
def c_cleanup(GAME,args,character,nick,flags): 
  GAME.cleanup()
  return "Stress, temporary aspects, and turn order cleared."
def c_add_npc(GAME,args,character,nick,flags): return GAME.add(GAME.mkcharacter(args),nick)
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
"clean":c_cleanup
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
