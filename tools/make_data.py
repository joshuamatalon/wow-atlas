"""Write site/data/ruins.json: the route, every creature card, the boss fights and the loot.
Positions are pixels on work/shots/ortho.png (the top-down render with ortho=-122,1237,902,1877 at 1440x900);
the page finds the ground height itself.  python -I make_data.py
"""
import json
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
K = 1440 / 1024


HEIGHTS = json.load(open(R / "work/heights.json")) if (R / "work/heights.json").exists() else {}


def W(px, py):
    """ortho pixel -> world [x, y, z]; y comes from the page's own ground probe (tools/bake_heights.py)"""
    x, z = round(902 - px / K, 1), round(1877 - py / K, 1)
    return [x, HEIGHTS.get(f"{x:g},{z:g}"), z]


ICON = json.load(open(R / "work/spell_icons.json"))
seed = {r["slug"]: r for r in json.load(open(R / "work/roster_seed.json"))}


def ab(spell, name, line):
    return {"name": name, "icon": ICON[str(spell)], "line": line, "spell": spell}


A = {
    "leech": ab(3358, "Leech Poison", "drains your health into the caster for 40 seconds, and a poison cure removes it."),
    "poison": ab(744, "Poison", "deals nature damage over 30 seconds until a poison cure removes it."),
    "web": ab(745, "Web", "roots one player in place for 10 seconds."),
    "webspin": ab(24600, "Web Spin", "stuns its melee target for 7 seconds."),
    "deadly": ab(3583, "Deadly Poison", "is a short cast that poisons its target for two minutes."),
    "shriek": ab(1309823, "Deafening Shriek", "silences one player for 4 seconds."),
    "worms": ab(16143, "Cadaver Worms", "is a 10-minute disease that stops health regeneration."),
    "frostarmor": ab(12544, "Frost Armor", "slows anyone who hits it in melee, and a magic dispel strips it."),
    "chilled": ab(6136, "Chilled", "slows movement and attacks for 5 seconds."),
    "agony": ab(18266, "Curse of Agony", "deals shadow damage over 15 seconds until a curse removal clears it."),
    "slumber": ab(7144, "Stone Slumber", "turns it to stone for 15 seconds while it heals, and weapons do nothing to it."),
    "cleave": ab(15613, "Cleave", "hits its target and the player nearest that target."),
    "plague": ab(16458, "Ghoul Plague", "is a 30-minute disease that slows you and weakens your hits."),
    "nova": ab(14907, "Frost Nova", "roots everyone within 10 yards for up to 8 seconds."),
    "drain": ab(1266011, "Life Drain", "is a 2-second cast that drains your health, so interrupt it."),
    "bcurse": ab(17105, "Banshee Curse", "makes its target miss more often for 12 seconds until a curse removal clears it."),
    "chilltouch": ab(12531, "Chilling Touch", "halves its target's speed and slows its attacks for 8 seconds."),
    "veil": ab(7068, "Veil of Shadow", "cuts the healing its target receives for 15 seconds."),
    "enrage": ab(8599, "Enrage", "makes it attack much faster for two minutes."),
    "hamstring": ab(9080, "Hamstring", "slows its target's movement for 10 seconds."),
    "demo": ab(13730, "Demoralizing Shout", "weakens the melee attacks of everyone within 10 yards."),
    "fireshield": ab(13376, "Fire Shield", "burns everyone within 5 yards of him."),
    "flamestrike": ab(18399, "Flamestrike", "is a 3-second cast that sets 5 yards of ground on fire, so step out."),
    "trample": ab(5568, "Trample", "hits everyone standing close to him."),
    "knockout": ab(17307, "Knockout", "knocks the tank back and stuns him for 6 seconds."),
    "mindblast": ab(1326990, "Mind Blast", "is a ranged shadow hit that builds a lot of threat."),
    "mighty": ab(14099, "Mighty Blow", "is a heavy hit that knocks its target back."),
    "knockaway": ab(10101, "Knock Away", "is a heavy hit that knocks its target back."),
    "summon": ab(1322054, "Summon Skeletal Servant", "raises a skeleton that fights for 30 seconds."),
    "ams": ab(1301635, "Anti-Magic Shield", "is a 2-second cast that makes him immune to magic for 3 seconds."),
    "hoj": ab(13005, "Hammer of Justice", "stuns its target for 4 seconds."),
    "holystrike": ab(1280354, "Holy Strike", "adds holy damage to his next swing."),
    "cleave2": ab(5532, "Cleave", "hits you and the player nearest you."),
}

# ---------------- creatures ----------------
E = []


def enemy(slug, kind, where, tank, group, abilities, level=None, say=None, boss=False, view=None):
    s = seed[slug]
    E.append({"slug": slug, "name": s["name"], "boss": boss, "type": kind, "level": level, "where": where,
              "tank": tank, "group": group, "abilities": [A[a] for a in abilities], "say": say, "npc": s["npc"],
              "display": s["display"], **({"view": view} if view is not None else {})})


# bosses
enemy("witherfang", "Boss", "She patrols the length of King's Alley with two spiders.",
      "Pull her when her path takes her clear of the other packs, and hold all three.",
      "Kill her two spiders first, then her. Cure her poison on the tank.", ["leech"], 17, boss=True)
enemy("the-baron", "Boss", "He guards a hole in the wall at the end of the south-east hallway.",
      "Fight him with your back to a wall and taunt him back after every Knockout.",
      "Melee stands behind him and ranged players spread out.", ["knockout", "trample", "mindblast"], 17, boss=True)
enemy("the-abandoned", "Boss", "He rises from the glowing-eyed statue in Market Street after three waves.",
      "Hold the middle of the courtyard so you meet adds from both corridors.",
      "Interrupt every Life Drain and stay out of Frost Nova.", ["drain", "nova", "frostarmor"], 18, boss=True)
enemy("viktor-the-vile", "Boss", "He comes on the sixth wave after you light the campfire in the burned house.",
      "Gather each wave before the group opens fire, then hold Viktor where he lands.",
      "Save mana for the waves and cure the poison on the tank.", ["leech"], 19, boss=True)
enemy("bjork", "Boss", "He patrols the road along the north-west wall.",
      "Keep your back to a wall so Mighty Blow cannot throw you into a ghoul pack.",
      "Casters stop for 3 seconds when his green shield goes up.", ["mighty", "ams"], 19, boss=True)
enemy("rath-mael", "Boss", "He stands on the purple rune in the fenced graveyard.",
      "Pull him off the rune and step out of every Flamestrike.",
      "Two players take turns interrupting Flamestrike.", ["flamestrike", "fireshield"], 20, boss=True)
enemy("lordaeron-captain", "Rare", "He appears in the west after the other bosses fall. Alliance players see him as a friend.",
      "Turn him away from the group so his Cleave hits only you.",
      "Ranged players keep their distance from his Hamstring.", ["cleave2", "hamstring"], 19, boss=True)

# spiders
enemy("spider", "Elite", "Spiders stand in pairs in King's Alley.",
      "Pull each pack back toward the stairs before a patrol walks into it.",
      "Kill the biggest spider first.", [])
enemy("deep-widow", "Elite", "It stands in King's Alley beside plain spiders.",
      "Hold it on you with the rest of its pack.", "Kill it first, because it hits hardest.", [])
enemy("broodling", "Normal", "Broodlings run in threes in King's Alley and walk beside Witherfang.",
      "Broodlings die fast and feed you rage, so let them hit you.", "Cleave and area attacks clear them.", [])
enemy("broodwidow", "Elite", "It lurks in King's Alley.",
      "Use Shield Block when it stuns you, because the rest of the pack keeps hitting.",
      "Cure its poison after the pull.", ["webspin", "poison"])
enemy("tarantula", "Elite", "It waits behind a broken tree with two Venom Lurkers.",
      "Pull it around a corner so its web lands near your healer.",
      "Cure the poison afterward.", ["web", "poison"])
enemy("venom-lurker", "Elite", "Two Lurkers guard the Tarantula in King's Alley.",
      "Hold both Lurkers together with the Tarantula.",
      "A poison cure clears the long poison.", ["deadly"])

# undead of the streets
enemy("shrieking-banshee", "Elite", "Two patrol the street south of Witherfang.",
      "Pick it up first in any pull it joins.", "Kill it first, because a silenced healer loses the pull.", ["shriek"],
      say="Banshee first.")
enemy("wailing-banshee", "Elite", "It haunts the south end of King's Alley.",
      "Its curse makes you miss, so ask for the curse removed.", "Mages and druids remove the curse.", ["bcurse"])
enemy("skeletal-soldier", "Elite", "Soldiers stand in threes with a mage at the south end of King's Alley.",
      "Gather the soldiers on you while the group kills the mage.", "Stun soldiers that turn on casters.", [])
enemy("skeletal-mage", "Elite", "Mages stand with Skeletal Soldiers.",
      "Let casters kill it.",
      "Kill it first and remove its curse.", ["frostarmor", "agony"], say="Mage first.")
enemy("mangled-cadaver", "Elite", "The hallway that leads to the Baron.",
      "Ask for its disease cured before the Baron, because you cannot heal it off.",
      "Priests and paladins cure Cadaver Worms.", ["worms"])
enemy("mindless-undead", "Elite", "They swarm along the south edge of the city.",
      "Gather the whole swarm before anyone attacks.", "Area attacks kill them together.", [])
enemy("ghoul", "Elite", "Ghouls stand in packs of up to five in Market Street and on Bjork's road.",
      "Gather the pack tight and keep Shield Block up.", "Kill the Ragged Ghoul in each pack first.", [])
enemy("ragged-ghoul", "Elite", "It stands with Ghouls on Bjork's road and at the graveyard.",
      "Hold it with its pack.", "Kill it first in every ghoul pack.", [], say="Kill the Ragged Ghoul first.")
enemy("plague-ghoul", "Elite", "It walks with Skeletal Soldiers.",
      "Turn it so its Cleave hits only you.",
      "Cure Ghoul Plague, because it lasts half an hour.", ["cleave", "plague"])
enemy("fallen-berserker", "Elite", "It walks Market Street.",
      "Face it away from everyone so its Cleave hits only you.",
      "Kill it quickly once it enrages.", ["enrage", "cleave", "hamstring"])
enemy("fallen-necromancer", "Elite", "Necromancers stand on the south edge of the city.",
      "Hold its skeletons until they crumble.", "Kill the necromancer and ignore the skeletons.", ["summon"])
enemy("skeleton", "Normal", "Fallen Necromancers raise them.",
      "Let them hit you, because they crumble after 30 seconds.", "Ignore them and kill the necromancer.", [])
enemy("flesh-golem", "Elite", "It patrols the south edge and stops short of a statue.",
      "Fight it with your back against a wall or a house.",
      "Stay behind it so its knockback sends nobody into a pack.", ["knockaway"])
enemy("living-monstrosity", "Elite", "It guards an outhouse in the far north-west corner.",
      "Put your back to the outhouse wall before it hits you.", "Pull it alone, away from Bjork's road.", ["mighty"])
enemy("stone-watcher", "Elite", "Gargoyles perch like statues on the upper ledges.",
      "Pick it up again when it wakes from stone.", "Casters burn it while it sleeps, because weapons do nothing.",
      ["slumber"])
enemy("vengeful-citizen", "Normal", "They drift through the streets by the graveyard.",
      "Gather them with the next pack.", "Area attacks clear them.", [])
enemy("spiteful-phantom", "Normal", "Phantoms drift near the graveyard.",
      "Its touch slows you, so fight it where you stand.", "Kill it before it slows a caster.", ["chilltouch"])
enemy("ghostly-citizen", "Normal", "Three stand where King's Alley bends toward the Baron.",
      "Leave them alone, because they stay calm unless hit.",
      "A curse removal clears their Veil of Shadow.", ["veil"])
enemy("captain-truman", "Quest giver", "He stands just inside the gate on the left.",
      "Alliance players take Abominable Creatures from him.",
      "Horde players fight him, and he stuns his target.", ["hoj", "holystrike"])

# ---------------- route ----------------
S = []


def stop(kind, px, title, text, enemies=(), say=None, boss=None):
    S.append({"kind": kind, "part": 0, "pos": W(*px), "title": title, "text": text, "enemies": list(enemies),
              **({"say": say} if say else {}), **({"boss": boss} if boss else {})})


stop("entrance", (930, 40), "The North Gate",
     ["You enter the old capital at its north gate. The streets run south in a U, and the group walks them clockwise, east side first."])
stop("quest", (990, 115), "Captain Truman",
     ["Alliance players take Abominable Creatures here and bring the Head of the Baron back before leaving.",
      "Bloodied Insignia drops from the undead, and Stormwind takes ten."], ["captain-truman"])
stop("pack", (1200, 165), "King's Alley",
     ["Take the stairs east. Spider packs fill the alley in twos and threes, and fast spiders patrol it.",
      "Pull each pack back up the stairs so no patrol joins."], ["spider", "deep-widow", "broodling", "broodwidow"])
stop("quest", (1158, 162), "Crest of Lordaeron",
     ["The Crest hangs on one of five walls each run. Check the top of this tower, the crypt by the south-east fountain, Bjork's tower, the wall behind his road and the Market Street tower."])
stop("pack", (1200, 250), "The Broken Tree",
     ["A Tarantula and two Venom Lurkers wait behind a broken tree. The Tarantula webs one player for 10 seconds.",
      "Pull the pack around the corner so the web lands near your healer."], ["tarantula", "venom-lurker"])
stop("boss", (1200, 322), "Witherfang",
     ["Witherfang walks the alley with two spiders. Wait until her path takes her clear of the other packs, then pull."],
     ["witherfang", "broodling"], say="Wait for her to come to us. Spiders first, then the boss.", boss="witherfang")
stop("hazard", (1200, 420), "Banshee Patrol",
     ["Two Shrieking Banshees patrol south of Witherfang. Each one silences a caster for 4 seconds.",
      "Kill a banshee first in any pull it joins."], ["shrieking-banshee", "wailing-banshee"], say="Banshee first.")
stop("pack", (1110, 470), "Skeleton Watch",
     ["Skeletons stand in threes at the south end of the alley. Kill the mage first, because its frost armor slows your swings."],
     ["skeletal-soldier", "skeletal-mage", "stone-watcher"], say="Mage first, then soldiers.")
stop("event", (1062, 482), "Three Ghosts",
     ["Three Ghostly Citizens stand where the street bends. Turn right here, through the passage, into the Baron's hallway.",
      "The ghosts stay calm unless someone hits them."], ["ghostly-citizen"])
stop("pack", (1045, 520), "The Baron's Hallway",
     ["Mangled Cadavers guard the hallway. Their Cadaver Worms stop your health regenerating for 10 minutes.",
      "Get the disease cured before you pull the Baron."], ["mangled-cadaver", "skeletal-soldier"],
     say="Cure my disease before the boss.")
stop("boss", (1027, 562), "The Baron",
     ["The Baron blocks a hole in the wall. Clear the hallway, put your back to the wall and pull."],
     ["the-baron"], say="He knocks me out and turns on someone. Run to me and I'll taunt him back.", boss="the-baron")
stop("event", (1000, 605), "The Pillar Jump",
     ["A broken pillar leans on the low wall behind the Baron. Jump onto it and over the wall to skip the packs in the street.",
      "Hunters and warlocks dismiss pets first."])
stop("hazard", (905, 655), "The South Edge",
     ["Flesh Golems patrol the south edge, and their Knock Away throws the tank into other packs.",
      "Fight them with your back to a wall. Fallen Necromancers raise skeletons, so kill the necromancer."],
     ["flesh-golem", "fallen-necromancer", "skeleton", "mindless-undead"], say="Back to the wall for golems.")
stop("boss", (700, 530), "Viktor the Vile",
     ["Light the Grim Campfire in the burned house to start five waves. Viktor comes on the sixth.",
      "You can skip him."], ["viktor-the-vile"], say="Five waves, then Viktor. Let me grab each wave first.",
     boss="viktor-the-vile")
stop("pack", (662, 420), "Market Street",
     ["Market Street runs north along the west wall. Ghouls stand five together, and Plague Ghouls spread a slowing disease.",
      "Fallen Berserkers cleave the player beside you."], ["ghoul", "plague-ghoul", "fallen-berserker", "skeletal-mage"])
stop("hazard", (720, 352), "Stone Watchers",
     ["Gargoyles perch like statues on the ledges here. A hurt gargoyle turns to stone and heals while weapons do nothing to it.",
      "Casters burn it while it sleeps."], ["stone-watcher"])
stop("boss", (674, 262), "The Abandoned",
     ["Walk up to the statue with glowing eyes to start three waves of ghosts. The Abandoned steps out after them.",
      "You can skip him."], ["the-abandoned"], say="Three waves, then the boss. Kick every Life Drain.",
     boss="the-abandoned")
stop("pack", (765, 195), "Bjork's Road",
     ["Jump through the large window north of Market Street into the fog. Ghoul packs sit along Bjork's road.",
      "A Living Monstrosity guards the outhouse in the far corner."], ["ghoul", "ragged-ghoul", "living-monstrosity"],
     say="Kill the Ragged Ghoul first.")
stop("boss", (732, 150), "Bjork",
     ["Bjork walks the road along the north-west wall. Clear the ghouls near his path, then pull him to a wall."],
     ["bjork"], say="I'll fight him with my back to the wall. Casters hold when he goes green.", boss="bjork")
stop("pack", (795, 345), "The Graveyard Gate",
     ["Head south to the fenced graveyard and its purple rune. Three ghoul packs guard it, with ghosts drifting between them.",
      "Kill the Ragged Ghoul in each pack first."],
     ["ghoul", "ragged-ghoul", "vengeful-citizen", "spiteful-phantom"])
stop("quest", (735, 425), "Edward Heartweaver",
     ["Edward's body lies on the west side of the graveyard. Alliance players take his letter for Remember That I Love You.",
      "Horde players find him for A Frightened Request."])
stop("boss", (763, 398), "Rath'mael",
     ["The last boss stands on the rune. Pull him off it, back toward the gate you came through."],
     ["rath-mael"], say="Two kickers on Flamestrike. I'll step out of the fire, so follow me.", boss="rath-mael")
stop("boss", (844, 467), "Lordaeron Captain",
     ["A rare captain sometimes walks the west side after the bosses fall. Only Horde groups fight him.",
      "Alliance players run back to Captain Truman with the Baron's head."], ["lordaeron-captain"],
     boss="lordaeron-captain")

# ---------------- boss fights ----------------
B = []


def boss(slug, name, enemy_slug, sub, px, r, tank, party, intro, steps, shapes, loot, say=None, level=None, view=0.0):
    B.append({"slug": slug, "name": name, "enemy": enemy_slug, "sub": sub, "level": level,
              "room": {"center": W(*px), "radius": r, "view": view},
              "tankSpot": W(*tank), "partySpot": W(*party), "intro": intro, "steps": steps, "shapes": shapes,
              "loot": loot, **({"say": say} if say else {})})


def shape(kind, px, step, **kw):
    return {"type": kind, "at": W(*px), "step": step, **kw}


boss("witherfang", "Witherfang", "witherfang", "King's Alley · spider", (1200, 322), 56, (1200, 330), (1200, 285),
     "A giant spider walks King's Alley with two spiders at her side.",
     ["Wait at the north end until she walks toward you, clear of the other packs.",
      "Pull her with a ranged shot and pick up both spiders as they arrive.",
      "The group kills the two spiders first while you hold all three.",
      "Leech Poison drains your health into her, so a shaman or druid cures it.",
      "Save Shield Block for the moments when all three hit you together."],
     [shape("circle", (1200, 330), 3, r=3.5), shape("arrow", (1200, 352), 1, r=14, dir=0.0, color="safe")],
     [{"name": "Atrophic Girdle", "slot": "mail waist", "mine": True}, {"name": "Witherbite Bracers", "slot": "leather wrist"},
      {"name": "Segmented Spider Leg", "slot": "staff"}],
     say="Wait for her to come to us. Spiders first, then the boss. Cure the poison on me.", level=17, view=0.0)
boss("the-abandoned", "The Abandoned", "the-abandoned", "Market Street · optional", (674, 262), 59, (674, 266), (674, 300),
     "A wraith rises from the glowing-eyed statue after three waves of ghosts.",
     ["Start the event only when the whole group has full health and mana.",
      "Hold the middle of the courtyard, because the waves come down both corridors.",
      "Leave the last ghost of each wave alive for a moment so the healer can drink.",
      "Life Drain is a 2-second cast on you, so one player interrupts every one.",
      "Frost Nova roots everyone within 10 yards of him, so ranged players stand outside it.",
      "Frost Armor slows anyone who hits him, so a priest or shaman strips it."],
     [shape("circle", (674, 262), 4, r=10), shape("arrow", (674, 220), 1, r=22, dir=3.14159),
      shape("arrow", (674, 330), 1, r=22, dir=0.0)],
     [{"name": "Grip of Fear", "slot": "mail hands", "mine": True}, {"name": "Scepter of the Abandoned", "slot": "mace"},
      {"name": "Rotmender's Leggings", "slot": "cloth legs"}],
     say="Three waves, then the boss. Leave one ghost alive for drinks. Kick every Life Drain.", level=18)
boss("the-baron", "The Baron", "the-baron", "South-east hallway · abomination", (1027, 562), 52, (1047, 560), (995, 575),
     "A huge abomination blocks a hole in the wall at the end of the south-east hallway.",
     ["Clear the cadavers and the skeleton patrol in the hallway before you pull.",
      "Hold him with your back to the wall so Knockout cannot throw you into a pack.",
      "Knockout stuns you for 6 seconds and drops your threat, so taunt him back the moment it ends.",
      "Melee players stand behind him, and ranged players spread out so Trample catches one at most.",
      "Healers keep you near full health, because Knockout hits for close to half of it.",
      "Anyone he chases runs straight back to you."],
     [shape("arrow", (1033, 561), 1, r=12, dir=-1.5708), shape("circle", (1027, 562), 3, r=8)],
     [{"name": "Abomination Bones", "slot": "mail chest", "mine": True}, {"name": "Meathook Slicer", "slot": "dagger"},
      {"name": "Leftover Abomination Skin", "slot": "cloth chest"}, {"name": "Head of the Baron", "slot": "Alliance quest"},
      {"name": "Abominable Head", "slot": "Horde quest"}],
     say="He knocks me out and turns on someone. Run to me and I'll taunt him back.", level=17, view=-1.2)
boss("lordaeron-captain", "Lordaeron Captain", "lordaeron-captain", "West side · rare, Horde only", (844, 467), 54, (844, 467), (844, 430),
     "A rare captain who walks the west side once the other bosses fall. Alliance players see him as a friend.",
     ["Clear his patrol path before you engage him.",
      "Turn him away from the group, because his Cleave hits you and the player nearest you.",
      "Hamstring slows whoever he hits, so ranged players keep their distance.",
      "Hold him in place while the group burns him down."],
     [shape("cone", (844, 467), 1, r=6, angle=1.6, dir=3.14159)],
     [{"name": "Phantom Armor"}, {"name": "Haunting Blade"}], level=19)
boss("viktor-the-vile", "Viktor the Vile", "viktor-the-vile", "Burned house · optional", (700, 530), 56, (700, 522), (700, 495),
     "Viktor answers the campfire in the burned house on the sixth wave.",
     ["Clear the streets around the house, drink, then light the Grim Campfire.",
      "Five waves of undead follow with almost no break, so gather each one before the group attacks.",
      "Healers save mana for the waves, and everyone brings potions and bandages.",
      "Viktor arrives on the sixth wave and hits hard in melee.",
      "Leech Poison drains your health into him, so a shaman or druid cures it."],
     [shape("circle", (700, 522), 4, r=3.5)],
     [{"name": "Vileblood Scimitar", "slot": "sword", "mine": True}, {"name": "Vilewalkers", "slot": "mail feet", "mine": True},
      {"name": "Death Bindings", "slot": "mail wrist", "mine": True}, {"name": "Bloodied Chestwraps", "slot": "leather chest"},
      {"name": "Sword of the Fallen", "slot": "two-hand sword"}],
     say="Five waves, then Viktor. Let me grab each wave first.", level=19)
boss("bjork", "Bjork", "bjork", "North-west road · wight", (732, 150), 56, (712, 150), (770, 170),
     "A giant wight walks the road along the north-west wall.",
     ["Clear every ghoul pack near his road before you pull him.",
      "Hold him with your back to a wall, because Mighty Blow knocks you back about every 8 seconds.",
      "Face him away from the group.",
      "When the green Anti-Magic Shield goes up, casters stop for 3 seconds.",
      "Healers stay in range after each knockback, because a tank out of reach dies here."],
     [shape("arrow", (720, 150), 1, r=10, dir=1.5708), shape("circle", (770, 170), 4, r=6, color="party")],
     [{"name": "Bonerust Leggings", "slot": "mail legs", "mine": True}, {"name": "Corpse Chopper", "slot": "two-hand axe"},
      {"name": "Tuskwrap Belt", "slot": "cloth waist"}, {"name": "Sword of the Fallen", "slot": "two-hand sword"}],
     say="I'll fight him with my back to the wall. Casters hold when he goes green.", level=19, view=0.6)
boss("rath-mael", "Rath'mael", "rath-mael", "The graveyard · last boss", (763, 398), 59, (775, 370), (795, 330),
     "The last boss stands on the purple rune inside the fenced graveyard.",
     ["Clear the three ghoul packs around the graveyard first.",
      "Pull him off the rune and back toward the gate, where the group has room.",
      "Flamestrike lands where you stood when the cast began, so step out of it as soon as you see it.",
      "Name two interrupters, and they take turns stopping Flamestrike.",
      "Fire Shield burns everyone within 5 yards of him, so healers plan for the melee.",
      "He has the most health of any boss here, so the fight runs long."],
     [shape("circle", (775, 370), 2, r=5), shape("arrow", (775, 370), 2, r=9, dir=0.9, color="safe"),
      shape("circle", (763, 398), 4, r=5)],
     [{"name": "Mirror of Rath'mael", "slot": "shield", "mine": True}, {"name": "Coldspire Staff", "slot": "staff"},
      {"name": "Rotmender's Treads", "slot": "cloth feet"}],
     say="Two kickers on Flamestrike. I'll step out of the fire, so follow me.", level=20, view=2.6)

data = {
    "dungeon": {"name": "Ruins of Lordaeron", "levels": "15 to 22"},
    "parts": [{"name": "The Ruins", "short": "Ruins", "clipBelow": 40}],
    "map": {"model": "models/map.glb", "center": [241, 62, 1607], "camOffset": [0, 760, -600], "gridRadius": 420,
            "floorY": 30, "startPart": 0, "groundMax": 76},
    "stops": S, "enemies": E, "bosses": B,
}
out = R / "site/data/ruins.json"
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("stops", len(S), "enemies", len(E), "bosses", len(B), "->", out)
missing = [s for s in seed if s not in {e["slug"] for e in E}]
print("roster without a card:", missing)
