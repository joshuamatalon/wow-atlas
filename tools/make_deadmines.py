"""Write site/data/deadmines.json (a bestiary alone: no map, no route, no fight views) and site/data/index.json.
Every ability line is worded from the live client's spell row in work/dm/spells_live.json.  python -I make_deadmines.py
"""
import json
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
seed = {r["slug"]: r for r in json.load(open(R / "work/dm/roster_seed.json"))}
LIVE = json.load(open(R / "work/dm/spells_live.json", encoding="utf-8"))
RANK = {r["id"]: r["classification"] for r in json.load(open(R / "work/dm/wh/zone_npcs.json", encoding="utf-8"))}


def ab(spell, line, name=None):
    s = LIVE[str(spell)]
    return {"name": name or s["name"], "icon": s["icon"], "line": line, "spell": spell}


A = {
    "pierce": ab(6016, "halves its target's armor for 20 seconds."),
    "golem": ab(3605, "is a 3-second cast that calls a golem to fight for a minute, so interrupt it."),
    "shoot": ab(6660, "hits from 5 to 30 yards away."),
    "command": ab(5115, "makes nearby allies attack much faster for 6 seconds, and a magic dispel removes it."),
    "stealth": ab(1785, "keeps it hidden until it strikes."),
    "thrash": ab(3391, "gives him two extra attacks at once."),
    "allies": ab(5200, "calls two Defias Blackguards to his side."),
    "cleave": ab(5532, "hits its target and the player nearest that target."),
    "axetoss": ab(6466, "is a thrown axe that stuns its target for 3 seconds from up to 20 yards."),
    "pain": ab(3603, "slows its target's spell casts for 15 seconds."),
    "terrify": ab(7399, "makes one player run in fear for 4 seconds, and a magic dispel ends it."),
    "eject": ab(5141, "drops Sneed out of the shredder for a second fight."),
    "disarm": ab(6713, "takes its target's weapon away for 6 seconds."),
    "rslam": ab(6304, "is a heavy hit that stuns its target for 3 seconds."),
    "cooking": ab(5174, "is a 2-second cast that heals him, so interrupt it."),
    "acid": ab(6306, "is a quick cast that burns nearby players for 30 seconds, and no cure removes it."),
    "reflexes": ab(6264, "lets him parry most attacks for 8 seconds."),
    "stomp": ab(6432, "stuns the whole group for 10 seconds."),
    "sslam": ab(6435, "is a heavy hit that stuns its target for 3 seconds."),
    "harpoon": ab(5208, "is a 2-second cast that poisons its target for a minute until a poison cure removes it."),
    "parrot": ab(5172, "brings a parrot, the Defias Companion, to fight beside it."),
    "flameward": ab(4979, "makes one ally immune to fire for 10 seconds."),
    "flamestrike": ab(11829, "is a 3-second cast that sets a patch of ground on fire for 8 seconds, so step out."),
    "frostarmor": ab(12544, "slows anyone who hits it in melee, and a magic dispel strips it."),
    "meltore": ab(5159, "is a short cast that burns players within 5 yards and slows them for 20 seconds."),
    "nova": ab(122, "roots everyone near it for up to 8 seconds."),
    "fireblast": ab(2138, "is an instant fire hit from up to 20 yards."),
    "molten": ab(5213, "is a 2-second cast that burns its target and slows its movement and attacks by half for 15 seconds."),
    "pshot": ab(6685, "is a ranged shot that cuts its target's armor for 15 seconds."),
    "chains": ab(113, "is a short cast that roots one player for 15 seconds, and a magic dispel frees them."),
    "fireball": ab(9053, "is a 3-second cast that hits one player from up to 40 yards."),
}

E = []


def enemy(slug, abilities, boss=False, kind=None, plain=None, view=None):
    s = seed[slug]
    kind = kind or ("Boss" if boss else {0: "Normal", 1: "Elite", 2: "Rare elite", 4: "Rare"}.get(RANK[s["npc"]], "Enemy"))
    E.append({"slug": slug, "name": s["name"], "boss": boss, "type": kind, "level": s["level"].replace(" - ", " to "),
              "abilities": [A[a] for a in abilities], "npc": s["npc"], "display": s["display"],
              **({"plain": plain} if plain else {}), **({"view": view} if view is not None else {})})


# bosses, in the order the mine leads to them
enemy("rhahk-zor", ["rslam"], boss=True)
enemy("miner-johnson", [], boss=True, kind="Rare elite")
enemy("sneed-s-shredder", ["pain", "terrify", "eject"], boss=True)
enemy("sneed", ["disarm"], boss=True)
enemy("gilnid", ["molten"], boss=True)
enemy("mr-smite", ["stomp", "sslam", "reflexes", "thrash"], boss=True)
enemy("captain-greenskin", ["harpoon", "cleave"], boss=True)
enemy("edwin-vancleef", ["allies", "thrash"], boss=True)
enemy("cookie", ["cooking", "acid"], boss=True)

# the mine crews
enemy("defias-miner", ["pierce"])
enemy("defias-strip-miner", ["pierce"])
enemy("defias-overseer", ["command"])
enemy("defias-evoker", ["flamestrike", "frostarmor", "flameward"])
enemy("defias-watchman", ["shoot"])
enemy("defias-taskmaster", ["pshot", "shoot"])
enemy("defias-wizard", ["chains", "fireball", "flameward"])
# the goblin works
enemy("goblin-woodcarver", ["axetoss", "cleave"])
enemy("goblin-craftsman", ["meltore"])
enemy("goblin-engineer", ["golem", "shoot"])
enemy("remote-controlled-golem", [], plain="Goblin Engineers summon it, and it only swings in melee.")
enemy("goblin-shipbuilder", [])
# the ship
enemy("defias-pirate", ["parrot"])
enemy("defias-companion", [], plain="Defias Pirates bring this parrot, and it only pecks in melee.")
enemy("defias-squallshaper", ["nova", "fireblast", "frostarmor"])
enemy("defias-blackguard", ["stealth"])

data = {"dungeon": {"name": "The Deadmines"}, "assets": "dm/", "enemies": E}
out = R / "site/data/deadmines.json"
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
json.dump([{"d": "ruins", "name": "Ruins of Lordaeron", "short": "Ruins"}, {"d": "deadmines", "name": "The Deadmines", "short": "Deadmines"}],
          open(R / "site/data/index.json", "w", encoding="utf-8"), indent=1)
print("enemies", len(E), "->", out)
print("roster without a card:", [s for s in seed if s not in {e["slug"] for e in E}])
