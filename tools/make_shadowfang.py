"""Write site/data/shadowfang.json (a bestiary alone: no map, no route, no fight views) and add it to site/data/index.json.
Every ability line is worded from the live client's spell row in work/sfk/spells_live.json.  python -I make_shadowfang.py
"""
import json
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
seed = {r["slug"]: r for r in json.load(open(R / "work/sfk/roster_seed.json"))}
LIVE = json.load(open(R / "work/sfk/spells_live.json", encoding="utf-8"))
RANK = {r["id"]: r["classification"] for r in json.load(open(R / "work/sfk/wh/zone_npcs.json", encoding="utf-8"))}


def ab(spell, line, name=None):
    s = LIVE[str(spell)]
    return {"name": name or s["name"], "icon": s["icon"], "line": line, "spell": spell}


A = {
    "gift": ab(7124, "is a short cast that curses one player for 5 minutes, and a curse removal ends it."),
    "frostarmor": ab(12544, "slows anyone who hits it in melee, and a magic dispel strips it."),
    "antimagic": ab(7121, "is a 2-second cast that makes it immune to magic for 10 seconds, so interrupt it."),
    "restore": ab(7106, "is a 2-second cast that heals its worg, so interrupt it."),
    "callworg": ab(7107, "brings a Wolfguard Worg to fight beside it."),
    "pain": ab(970, "burns one player with shadow for 18 seconds, and a magic dispel removes it."),
    "befuddle": ab(8140, "halves one player's casting speed for 15 seconds, and a magic dispel removes it."),
    "bloodtap": ab(7122, "drains its target's health and heals the Glutton for up to twice as much."),
    "wildrage": ab(7072, "makes it hit harder for a minute."),
    "wavering": ab(7127, "slows its target's attacks and casts for a minute and its movement too, and a magic dispel removes it."),
    "delusions": ab(7132, "is a 1-second cast that calls two Lupine Delusions for 4 minutes."),
    "felstomp": ab(7139, "stuns players within 10 yards for 3 seconds and raises the physical damage they take."),
    "disarm": ab(6713, "takes its target's weapon away for 6 seconds."),
    "sweep": ab(7145, "hits its target and the players nearest that target."),
    "expose": ab(7140, "raises the physical damage its target takes for 5 seconds, and a magic dispel removes it."),
    "cleave": ab(5532, "hits its target and the player nearest that target."),
    "hamstring": ab(9080, "slows its target's movement by more than half for 10 seconds."),
    "skills": ab(7054, "is a short cast that curses its target for 5 minutes and lowers one skill again and again."),
    "spirits": ab(7057, "is a 2-second cast that curses its target for 5 minutes, and ghosts come for that player."),
    "screams": ab(7074, "silences players within 5 yards for 5 seconds, and a magic dispel ends it."),
    "veil": ab(7068, "is a short cast that cuts the healing one player receives by three quarters for 15 seconds."),
    "souldrain": ab(7295, "is a 2-second cast that roots one player for 10 seconds and drains health to him."),
    "bleak": ab(7487, "is a short cast that brings a Bleak Worg for 4 minutes."),
    "slavering": ab(7488, "is a short cast that brings a Slavering Worg for 4 minutes."),
    "horror": ab(7489, "is a short cast that brings a Lupine Horror for 4 minutes."),
    "saliva": ab(7125, "poisons its target for 2 minutes and drains mana, and a poison cure removes it."),
    "voidbolt": ab(7588, "is a 3-second cast that hits one player with shadow from any range."),
    "curse": ab(7621, "turns one player into a worgen under his control for 10 seconds, and a curse removal ends it."),
    "thunder": ab(7803, "stuns players within 5 yards for 5 seconds."),
    "shield": ab(642, "makes him immune to everything for 10 seconds."),
    "holylight": ab(1026, "is a short cast that heals him or an ally, so interrupt it."),
    "hammer": ab(5588, "stuns one player for 4 seconds from up to 10 yards, and a magic dispel ends it."),
    "howl": ab(7481, "is a 5-second cast that makes him and allies within 10 yards hit harder."),
    "offering": ab(7154, "heals an ally within 10 yards."),
}

E = []


def enemy(slug, abilities, boss=False, kind=None, plain=None, view=None):
    s = seed[slug]
    kind = kind or ("Boss" if boss else {0: "Normal", 1: "Elite", 2: "Rare elite", 4: "Rare"}.get(RANK[s["npc"]], "Enemy"))
    E.append({"slug": slug, "name": s["name"], "boss": boss, "type": kind, "level": s["level"].replace(" - ", " to "),
              "abilities": [A[a] for a in abilities], "npc": s["npc"], "display": s["display"],
              **({"plain": plain} if plain else {}), **({"view": view} if view is not None else {})})


# bosses, in the order the keep leads to them
enemy("rethilgore", ["souldrain"], boss=True)
enemy("razorclaw-the-butcher", [], boss=True, plain="The game lists no ability for him.")
enemy("baron-silverlaine", ["veil"], boss=True)
enemy("commander-springvale", ["holylight", "hammer", "shield"], boss=True)
enemy("odo-the-blindwatcher", ["howl"], boss=True)
enemy("deathsworn-captain", ["cleave", "hamstring"], boss=True, kind="Rare elite")
enemy("fenrus-the-devourer", ["saliva"], boss=True)
enemy("wolf-master-nandos", ["bleak", "slavering", "horror"], boss=True)
enemy("archmage-arugal", ["voidbolt", "curse", "thunder"], boss=True)

# the worgen
enemy("shadowfang-whitescalp", ["frostarmor"])
enemy("shadowfang-moonwalker", ["antimagic"])
enemy("shadowfang-wolfguard", ["restore", "callworg"])
enemy("wolfguard-worg", [], plain="Shadowfang Wolfguards bring it, and it only bites in melee.")
enemy("shadowfang-darksoul", ["pain", "befuddle"])
enemy("shadowfang-glutton", ["bloodtap"])
enemy("shadowfang-ragetooth", ["wildrage"])
enemy("son-of-arugal", ["gift"])
# the beasts
enemy("bleak-worg", ["wavering"])
enemy("slavering-worg", [])
enemy("fel-steed", ["felstomp"])
enemy("shadow-charger", [])
enemy("vile-bat", ["sweep", "disarm"])
enemy("blood-seeker", ["expose"])
# the dead of the keep
enemy("haunted-servitor", ["spirits"])
enemy("haunting-spirit", [], plain="A Haunted Servitor's curse calls it, and it only swings in melee.")
enemy("wailing-guardsman", ["screams"])
enemy("tormented-officer", ["skills"])
enemy("gefell", ["screams"])
enemy("gemela", [])
enemy("lupine-horror", ["delusions"])
enemy("lupine-delusion", [], plain="A Lupine Horror calls two of them, and they only swing in melee.")
enemy("arugal-s-voidwalker", ["offering"])
# the prisoners
enemy("sorcerer-ashcrombe", [], kind="Friendly", plain="He waits in a cell near the entrance, and he opens the courtyard door for the Alliance.")
enemy("deathstalker-adamant", [], kind="Friendly", plain="He waits in a cell near the entrance, and he opens the courtyard door for the Horde.")
enemy("deathstalker-vincent", [], kind="Friendly", plain="He ends a quest inside the keep.")

# Kill order for the tank's skull mark: more skulls die first, no skull dies last. Judged from the ability rows alone:
# three for what stops the healer or heals the pack, two for curses that keep costing the group, one for what is worse
# than the plain melee beside it. Bosses carry no mark. Pack make-up in Forever is not known, so tiers hold across packs.
SKULLS = {
    "shadowfang-darksoul": (3, "Kill it first, because it halves your healer's casting speed."),
    "arugal-s-voidwalker": (3, "Kill them one at a time, because each one heals the others."),
    "haunted-servitor": (2, "Kill it early, because its curse keeps sending ghosts at one player."),
    "son-of-arugal": (2, "Kill it early, because each cast puts a heavy curse on another player."),
    "shadowfang-moonwalker": (1, "Kill it before its shield goes up and wastes your casters' spells."),
    "shadowfang-wolfguard": (1, "Kill it before its worg, because it heals the worg."),
    "shadowfang-glutton": (1, "Focus it down, because it heals itself with every drain."),
    "shadowfang-ragetooth": (1, "Kill it soon, because its rage makes it hit you harder."),
    "wailing-guardsman": (1, "Kill it before it reaches a caster, because its scream silences everyone near it."),
    "gefell": (1, "Its scream silences everyone near it, so it dies before it reaches a caster."),
    "vile-bat": (1, "Kill it before the Blood Seekers, because it disarms you."),
    "fel-steed": (1, "Kill it before the Shadow Chargers, because its stomp stuns everyone in melee."),
}
for e in E:
    if e["slug"] in SKULLS:
        e["skull"], e["why"] = SKULLS[e["slug"]]
assert not set(SKULLS) - {e["slug"] for e in E}

data = {"dungeon": {"name": "Shadowfang Keep"}, "assets": "sfk/", "enemies": E,
        "skullNote": "The skulls show the kill order in a pull. More skulls die first, and no skull dies last."}
out = R / "site/data/shadowfang.json"
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
ip = R / "site/data/index.json"
idx = [r for r in json.load(open(ip, encoding="utf-8")) if r["d"] != "shadowfang"]
idx.append({"d": "shadowfang", "name": "Shadowfang Keep", "short": "SFK"})
json.dump(idx, open(ip, "w", encoding="utf-8"), indent=1)
print("enemies", len(E), "->", out)
print("roster without a card:", [s for s in seed if s not in {e["slug"] for e in E}])
