"""Write site/data/dalaran.json (bestiary with a need list, sections of enemies that fight together, and skull marks)
and add it to site/data/index.json.  python -I make_dalaran.py
Ability lines are worded from the live client's spell rows in work/dal/spells_live.json. Sections, company lines and
skull tiers rest on the guides saved in work/dal/guides and work/dal/wh/guide.txt; work/dal/ledger.md names each one.
"""
import json
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
seed = {r["slug"]: r for r in json.load(open(R / "work/dal/roster_seed.json"))}
LIVE = json.load(open(R / "work/dal/spells_live.json", encoding="utf-8"))
RANK = {r["id"]: r["classification"] for r in json.load(open(R / "work/dal/wh/zone_npcs.json", encoding="utf-8"))}


def ab(spell, line, name=None):
    s = LIVE[str(spell)]
    return {"name": name or s["name"], "icon": s["icon"], "line": line, "spell": spell}


A = {
    # bosses
    "raise": ab(1303266, "raises two Skeletons for 30 seconds."),
    "frenzy": ab(1303264, "speeds an ally's attacks by three quarters for 20 seconds, and a magic dispel removes it."),
    "bdisarm": ab(6713, "takes its target's weapon away for 6 seconds."),
    "thrash": ab(3391, "gives it two extra attacks at once."),
    "strike": ab(12057, "is a heavy weapon hit on its target."),
    "volley": ab(17228, "hits every player within 30 yards with shadow."),
    "thorns": ab(1304473, "is a short cast that makes its target's own attacks hurt them for 3 minutes, and a curse removal ends it."),
    "focal": ab(1241501, "is a 3-second cast, then a beam for 6 seconds that hits anyone it sweeps over, so stay out of its path."),
    "abolt": ab(1240682, "is a 2-second cast that hits one player from up to 40 yards."),
    "debilitate": ab(1240750, "is a 2-second cast that drains mana from the players it hits."),
    "vitality": ab(1240738, "hits its target and keeps burning for 10 seconds, and a magic dispel removes it."),
    "timbers": ab(1240692, "sends vines at one player that hit everyone within 5 yards of them, so step away from that spot."),
    "entangle": ab(1240688, "roots nearby players for up to 6 seconds, and a magic dispel frees them."),
    "trample": ab(1240687, "hits every player near it."),
    "malfunction": ab(1241329, "is a 2-second wind-up, then arcane blasts around it for 6 seconds, so step away."),
    "bsmash": ab(16169, "hits everyone in a cone in front of it."),
    "silence": ab(8988, "is a short cast that silences players near it for 10 seconds, and a magic dispel ends it."),
    "manamorph": ab(1240869, "is a short cast that turns one player into an animal for 8 seconds, and a magic dispel ends it."),
    "manaling": ab(1304455, "calls two Arcane Manalings for 30 seconds."),
    "sbolt": ab(1241506, "is a short cast that hits one player from up to 40 yards."),
    "bounding": ab(1241515, "is a 2-second cast that throws a bolt at one player and hits anyone in its path."),
    "sexplosion": ab(1304398, "hits every player near him."),
    "masspoly": ab(1303598, "is a short cast that turns nearby players into animals for 8 seconds, and a magic dispel ends it."),
    "evocation": ab(1303599, "is a 6-second channel that refills his mana."),
    # the sewers
    "tfrenzy": ab(1303264, "speeds an ally's attacks for 20 seconds, and a magic dispel removes it."),
    "frostbolt": ab(1303226, "is a 3-second cast that slows one player for 4 seconds."),
    "frostarmor": ab(12544, "slows anyone who hits it in melee, and a magic dispel strips it."),
    "terrify": ab(7399, "makes one player run in fear for 4 seconds, and a magic dispel ends it."),
    "hamstring": ab(9080, "slows its target's movement by more than half for 10 seconds."),
    "slam": ab(15655, "stuns its target for 2 seconds."),
    "sunder": ab(15572, "cuts its target's armor, and it stacks five times."),
    "fury": ab(3416, "makes it hit harder and slower for 10 seconds."),
    "heal": ab(1303227, "is a short cast that heals an ally, so interrupt it."),
    "shadowbolt": ab(1303228, "is a 3-second cast that hits one player from up to 40 yards."),
    # the streets
    "manaburn": ab(11981, "is a 3-second cast that burns a caster's mana and hurts them for it, so interrupt it."),
    "reflect": ab(1303458, "turns spells cast at it and at its nearby allies back on the caster."),
    "sfrostbolt": ab(20822, "is a 3-second cast that hits one player and slows them for 4 seconds."),
    "nova": ab(11831, "roots everyone within 10 yards for up to 8 seconds."),
    "chain": ab(1303551, "is a 3-second cast that arcs from its target to nearby players."),
    "blink": ab(14514, "moves it 20 yards forward and frees it from roots."),
    "missiles": ab(1303499, "is a 6-second channel that hits one player each second."),
    "fexplosion": ab(1242252, "hits every player near it, and it goes off again when the fiend dies."),
    "leak": ab(1303503, "leaves a pool where it dies that restores mana, so casters stand in it."),
    "tsmash": ab(8374, "hits everyone in a cone in front of it."),
}

E = []


def enemy(slug, abilities, boss=False, kind=None, plain=None, packs=None):
    s = seed[slug]
    kind = kind or ("Boss" if boss else {0: "Normal", 1: "Elite", 2: "Rare elite", 4: "Rare"}.get(RANK[s["npc"]], "Enemy"))
    E.append({"slug": slug, "name": s["name"], "boss": boss, "type": kind, "level": s["level"].replace(" - ", " to "),
              "abilities": [A[a] for a in abilities], "npc": s["npc"], "display": s["display"],
              **({"plain": plain} if plain else {}), **({"packs": packs} if packs else {})})


NONE = "The game lists no ability for it."
# the sewers
enemy("kirin-tor-necromancer", ["raise", "tfrenzy"], packs="Three of them are around Atrexis, so kill two before you pull him.")
enemy("skeleton", [], kind="Summoned", plain="Necromancers and both sewer bosses raise them two at a time, and they only swing in melee.")
enemy("dark-caster", ["heal", "shadowbolt"])
enemy("mindless-horror", ["terrify"])
enemy("fallen-mage", ["frostbolt", "frostarmor"], packs="It pulls with Fallen Warriors, so use a corner.")
enemy("fallen-warrior", ["hamstring"], packs="It is found with Fallen Mages.")
enemy("skeletal-warder", ["slam", "sunder"])
enemy("risen-terror", [], plain=NONE)
enemy("sewer-fiend", ["fury"])
enemy("atrexis-the-grave-knight", ["raise", "frenzy", "bdisarm", "thrash", "strike"], boss=True,
      packs="Three Kirin Tor Necromancers are around him, so kill two before the pull.")
enemy("lyn-the-ignored", ["volley", "thorns", "raise"], boss=True, kind="Hidden boss",
      packs="He appears when you use your Tome of Dalaran at the rune circle in the north sewer.")
# the streets
enemy("mana-phantom", ["manaburn"], packs="Two of them are beside Arcanic Enigma at the pull.")
enemy("phantasm", ["reflect"])
enemy("mana-stalker", ["sfrostbolt", "nova"])
enemy("mana-echo", ["chain", "blink"])
enemy("arcane-elemental", ["missiles"])
enemy("mana-fiend", ["fexplosion"])
enemy("saturated-remnant", ["leak"], packs="It is found with Seeking Remnants, and your shield cannot block its arcane melee.")
enemy("seeking-remnant", ["thrash"], packs="It is found with Saturated Remnants.")
enemy("fragmented-sentry", ["tsmash", "thrash"])
enemy("arcane-echo", [], plain=NONE)
enemy("mana-wraith", [], plain=NONE)
# the city bosses and what stands with them (this section keeps its order)
enemy("arcane-anomaly", ["focal", "abolt"], boss=True, packs="Small adds wait at the edge of his room, so fight him inside the circle.")
enemy("mana-devourer", ["debilitate", "vitality"], boss=True, packs="Any trash left in his area joins the fight, so clear it first.")
enemy("fel-ancient", ["timbers", "entangle", "trample"], boss=True, packs="Suffused Treants stand in front of it behind a barrier.")
enemy("suffused-treant", [], plain="It stands in front of the Fel Ancient, and the game lists no ability for it.")
enemy("unstable-sentinel", ["malfunction", "bsmash"], boss=True, packs="Angry Tomes come out of the buildings as you walk up, so kill them first.")
enemy("angry-tome", [], plain="It comes out of the buildings near the Unstable Sentinel, and the game lists no ability for it.")
enemy("arcanic-enigma", ["silence", "manamorph", "manaling"], boss=True, packs="Two Mana Phantoms are beside it at the pull, and they die first.")
enemy("arcane-manaling", [], kind="Summoned", plain="Arcanic Enigma calls them two at a time, and they only swing in melee.")
enemy("shade-of-the-archmage", ["sbolt", "bounding", "sexplosion", "masspoly", "evocation"], boss=True,
      packs="He resets if he leaves his room.")
# friends
enemy("archmage-modera", [], kind="Friendly", plain="She opens the portal to the last boss.")

# Kill order for the tank's skull mark, judged inside each section because those enemies can share a pull.
# Three: it makes more enemies or empties the healer, and three guides say to kill it first. Two: it undoes the group's
# work (heals, reflects spells). One: a caster or a fear that is worse than the plain melee beside it. Bosses carry none.
SKULLS = {
    "kirin-tor-necromancer": (3, "Kill it first, because it keeps raising Skeletons until it dies."),
    "dark-caster": (2, "Kill it after any Necromancer, because it heals the others."),
    "mindless-horror": (1, "Kill it before the plain melee, because its fear sends a player into the next pack."),
    "fallen-mage": (1, "Kill it before the Fallen Warriors, because it casts from range."),
    "mana-phantom": (3, "Kill it first, because its Mana Burn empties your healer."),
    "phantasm": (2, "Kill it next, because your casters' spells bounce back while it lives."),
    "mana-stalker": (1, "Kill it before the melee, because it roots everyone near it and casts from range."),
    "mana-echo": (1, "Kill it before the melee, because its lightning arcs through your group."),
}
for e in E:
    if e["slug"] in SKULLS:
        e["skull"], e["why"] = SKULLS[e["slug"]]
assert not set(SKULLS) - {e["slug"] for e in E}

GROUPS = [
    {"name": "The sewers", "note": "Undead fill the sewers, and two bosses wait at the end of them.",
     "slugs": ["kirin-tor-necromancer", "dark-caster", "mindless-horror", "fallen-mage", "fallen-warrior", "skeletal-warder",
               "risen-terror", "sewer-fiend", "skeleton", "atrexis-the-grave-knight", "lyn-the-ignored"]},
    {"name": "The streets", "note": "Arcane spells do nothing to most enemies up here, and your shield blocks little of their melee.",
     "slugs": ["mana-phantom", "phantasm", "mana-stalker", "mana-echo", "arcane-elemental", "mana-fiend", "saturated-remnant",
               "seeking-remnant", "fragmented-sentry", "arcane-echo", "mana-wraith"]},
    {"name": "The city bosses and their company", "keep": True,
     "slugs": ["arcane-anomaly", "mana-devourer", "fel-ancient", "suffused-treant", "unstable-sentinel", "angry-tome",
               "arcanic-enigma", "arcane-manaling", "shade-of-the-archmage"]},
    {"name": "Friends", "slugs": ["archmage-modera"]},
]
assert not {s for g in GROUPS for s in g["slugs"]} ^ {e["slug"] for e in E}

# What he rolls need on, biggest gain first: gear_sources.py against the gear Scribe saved on 2026-11-26 11:08,
# ForeverDB file of 2026-11-26 (build 1.60.1.71139). Points gained are in work/dal/ledger.md.
NEEDS = [
    {"item": 273055, "name": "Bonepile Gaze", "icon": 134948, "slot": "Shield", "from": "lyn-the-ignored", "where": "Lyn the Ignored, 2 of 5 kills"},
    {"item": 286995, "name": "Guardian's Emblem", "icon": 135733, "slot": "Neck", "from": None, "where": "any enemy, binds when worn"},
    {"item": 286996, "name": "City Guard's Tarnished Blade", "icon": 135324, "slot": "One-hand sword", "from": None, "where": "any enemy, binds when worn"},
    {"item": 286992, "name": "Construct's Grips", "icon": 132938, "slot": "Hands", "from": None, "where": "any enemy, binds when worn"},
    {"item": 273035, "name": "Mana-Warped Chain Shirt", "icon": 132626, "slot": "Chest", "from": "arcane-anomaly", "where": "Arcane Anomaly, 3 of 12 kills"},
    {"item": 273032, "name": "Bonebinder's Signet", "icon": 133370, "slot": "Ring", "from": "atrexis-the-grave-knight", "where": "Atrexis the Grave Knight, 6 of 13 kills"},
]

data = {"dungeon": {"name": "City of Dalaran"}, "assets": "dal/", "enemies": E, "groups": GROUPS, "needs": NEEDS,
        "needTitle": "Roll need, biggest gain first",
        "skullNote": "The skulls show the kill order in a pull. More skulls die first, and no skull dies last."}
out = R / "site/data/dalaran.json"
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
ip = R / "site/data/index.json"
idx = [r for r in json.load(open(ip, encoding="utf-8")) if r["d"] != "dalaran"]
idx.append({"d": "dalaran", "name": "City of Dalaran", "short": "Dalaran"})
json.dump(idx, open(ip, "w", encoding="utf-8"), indent=1)
print("enemies", len(E), "->", out)
print("roster without a card:", [s for s in seed if s not in {e["slug"] for e in E}])
