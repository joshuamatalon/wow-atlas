"""Write site/data/blackfathom.json (a bestiary alone: no map, no route, no fight views) and add it to site/data/index.json.
Every ability line is worded from the live client's spell row in work/bfd/spells_live.json (and spells_extra.json).
python -I make_blackfathom.py
"""
import json
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
seed = {r["slug"]: r for r in json.load(open(R / "work/bfd/roster_seed.json"))}
LIVE = json.load(open(R / "work/bfd/spells_live.json", encoding="utf-8"))
LIVE.update(json.load(open(R / "work/bfd/spells_extra.json", encoding="utf-8")))
RANK = {r["id"]: r["classification"] for r in json.load(open(R / "work/bfd/wh/zone_npcs.json", encoding="utf-8"))}


def ab(spell, line, name=None):
    s = LIVE[str(spell)]
    return {"name": name or s["name"], "icon": s["icon"], "line": line, "spell": spell}


A = {
    # bosses
    "trample": ab(5568, "hits every player near him."),
    "slow": ab(246, "slows one player's attacks and movement for 10 seconds, and a magic dispel removes it."),
    "novaboss": ab(865, "roots everyone near her for up to 8 seconds."),
    "forked": ab(8435, "is a 2-second cast that hits everyone in a cone in front of her."),
    "shootboss": ab(6660, "hits from up to 30 yards away."),
    "net": ab(6533, "roots one player for 10 seconds from up to 20 yards."),
    "jettbolt": ab(12167, "is a 3-second cast that hits one player from up to 40 yards."),
    "jettshield": ab(12550, "shocks players who hit him, and a magic dispel strips it."),
    "leech": ab(8433, "drains health from players within 10 yards."),
    "sleep": ab(8399, "is a short cast that puts players near its target to sleep for up to 10 seconds, and a magic dispel wakes them."),
    "mindblast": ab(15587, "is a short cast that hits one player with shadow."),
    "cloud": ab(3815, "is a short cast that poisons players within 8 yards for 45 seconds, and a poison cure removes it."),
    "frenzy": ab(3490, "makes it attack much faster for 5 seconds, with weaker hits."),
    # satyrs and naga
    "weakness": ab(6205, "weakens one player's physical attacks for 2 minutes, and a curse removal ends it."),
    "sneak": ab(22766, "keeps it hidden until it strikes."),
    "manaburn": ab(8129, "is a 3-second cast that drains a caster's mana, so interrupt it."),
    "shadowbolt": ab(9613, "is a 3-second cast that hits one player from up to 40 yards."),
    "nova": ab(122, "roots everyone near it for up to 8 seconds."),
    "frostarmor": ab(12544, "slows anyone who hits it in melee, and a magic dispel strips it."),
    "disarm": ab(8379, "takes its target's weapon away for 10 seconds."),
    # the Twilight's Hammer
    "heal": ab(2055, "is a 3-second cast that heals an ally, so interrupt it."),
    "renew": ab(8362, "is a 2-second cast that heals an ally for 20 seconds, and a magic dispel removes it."),
    "smash": ab(8374, "hits everyone in a cone in front of it."),
    "guardian": ab(8372, "brings an Aqua Guardian to fight beside it."),
    "frostbolt": ab(9672, "is a 3-second cast that hits one player and slows them for 4 seconds."),
    "enlarge": ab(8365, "is a 2-second cast that makes an ally hit harder for a minute, and a magic dispel removes it."),
    "slowtrash": ab(18972, "slows one player's attacks and movement for 20 seconds, and a magic dispel removes it."),
    "voidwalker": ab(12746, "brings a Voidwalker Minion to fight beside it."),
    "earthshock": ab(8046, "is an instant hit that stops a player's cast."),
    "flameshock": ab(8052, "burns one player for 12 seconds."),
    "frostshock": ab(8056, "halves one player's movement speed for 8 seconds."),
    # murlocs
    "sunder": ab(7405, "cuts its target's armor, and it stacks."),
    "leechpoison": ab(8382, "poisons its target for 45 seconds and drains health to the murloc, and a poison cure removes it."),
    "oheal": ab(6063, "is a 3-second cast that heals an ally, so interrupt it."),
    "obolt": ab(9532, "is a 3-second cast that hits one player from range."),
    "orenew": ab(8362, "heals an ally over 20 seconds, and a magic dispel removes it."),
    # beasts and elementals
    "quicksnap": ab(4160, "is an extra melee hit on its target."),
    "ravage": ab(8391, "stuns its target for 3 seconds."),
    "tendon": ab(3604, "slows its target's movement for 8 seconds."),
    "volley": ab(8398, "is a 2-second cast that hits players within 20 yards and halves their movement."),
}

E = []


def enemy(slug, abilities, boss=False, kind=None, plain=None, view=None):
    s = seed[slug]
    kind = kind or ("Boss" if boss else {0: "Normal", 1: "Elite", 2: "Rare elite", 4: "Rare"}.get(RANK[s["npc"]], "Enemy"))
    E.append({"slug": slug, "name": s["name"], "boss": boss, "type": kind, "level": s["level"].replace(" - ", " to "),
              "abilities": [A[a] for a in abilities], "npc": s["npc"], "display": s["display"],
              **({"plain": plain} if plain else {}), **({"view": view} if view is not None else {})})


# bosses, in the order ForeverDB lists them for dungeon 48
enemy("ghamoo-ra", ["trample"], boss=True)
enemy("lady-sarevess", ["forked", "novaboss", "slow", "shootboss"], boss=True)
enemy("gelihast", ["net"], boss=True)
enemy("lorgus-jett", ["jettbolt", "jettshield"], boss=True)
enemy("old-serra-kis", ["leech"], boss=True)
enemy("twilight-lord-kelris", ["sleep", "mindblast"], boss=True)
enemy("aku-mai", ["cloud", "frenzy"], boss=True)

# satyrs and naga
enemy("fallenroot-hellcaller", ["manaburn", "shadowbolt"])
enemy("fallenroot-shadowstalker", ["weakness", "sneak"])
enemy("blackfathom-myrmidon", ["disarm"])
enemy("blackfathom-sea-witch", ["nova", "frostarmor"])
# murlocs
enemy("blindlight-oracle", ["oheal", "orenew", "obolt"])
enemy("blindlight-muckdweller", ["leechpoison"])
enemy("murkshallow-snapclaw", ["disarm"])
enemy("blindlight-murloc", ["sunder"])
enemy("murkshallow-softshell", [])
# the Twilight's Hammer
enemy("twilight-acolyte", ["heal", "renew"])
enemy("twilight-elementalist", ["earthshock", "frostshock", "flameshock"])
enemy("twilight-shadowmage", ["shadowbolt", "voidwalker"])
enemy("voidwalker-minion", [], plain="Twilight Shadowmages bring it, and it only swings in melee.")
enemy("twilight-aquamancer", ["frostbolt", "guardian"])
enemy("aqua-guardian", ["nova"])
enemy("twilight-loreseeker", ["slowtrash", "enlarge"])
enemy("twilight-reaver", ["smash"])
# beasts and elementals
enemy("aku-mai-servant", ["volley", "novaboss"])
enemy("aku-mai-snapjaw", ["ravage"])
enemy("aku-mai-fisher", [])
enemy("deep-pool-threshfin", ["tendon"])
enemy("snapping-crustacean", ["quicksnap"])
enemy("skittering-crustacean", [])
enemy("barbed-crustacean", [])
# friends
enemy("argent-guard-thaelrid", [], kind="Friendly", plain="He starts a quest inside the dungeon.")
enemy("morridune", [], kind="Friendly", plain="She is friendly to the Alliance.")

# Kill order for the tank's skull mark, by the rule in make_shadowfang.py: three for what heals the pack or stops the
# healer, two for casters that cost the whole group, one for what is worse than the plain melee beside it.
SKULLS = {
    "twilight-acolyte": (3, "Kill it first, because it heals the others."),
    "blindlight-oracle": (3, "Kill it first, because it heals the other murlocs."),
    "fallenroot-hellcaller": (2, "Kill it early, because it drains your healer's mana."),
    "twilight-elementalist": (2, "Kill it early, because its Earth Shock stops your healer's casts."),
    "twilight-shadowmage": (2, "Kill it early, because its Shadow Bolts hit your group from range."),
    "aku-mai-servant": (2, "Kill it early, because its volley hits everyone near it."),
    "twilight-aquamancer": (1, "Kill it before the melee, because it casts from range."),
    "twilight-loreseeker": (1, "Kill it before the melee, because it slows your attacks."),
    "blackfathom-myrmidon": (1, "Kill it before the Sea Witch, because it disarms you."),
    "blindlight-muckdweller": (1, "Kill it soon, because its poison drains health back to it."),
    "murkshallow-snapclaw": (1, "Kill it soon, because it disarms you."),
    "aku-mai-snapjaw": (1, "Kill it soon, because its bite stuns you."),
}
for e in E:
    if e["slug"] in SKULLS:
        e["skull"], e["why"] = SKULLS[e["slug"]]
assert not set(SKULLS) - {e["slug"] for e in E}

data = {"dungeon": {"name": "Blackfathom Deeps"}, "assets": "bfd/", "enemies": E,
        "skullNote": "The skulls show the kill order in a pull. More skulls die first, and no skull dies last."}
out = R / "site/data/blackfathom.json"
json.dump(data, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
ip = R / "site/data/index.json"
idx = [r for r in json.load(open(ip, encoding="utf-8")) if r["d"] != "blackfathom"]
idx.append({"d": "blackfathom", "name": "Blackfathom Deeps", "short": "BFD"})
json.dump(idx, open(ip, "w", encoding="utf-8"), indent=1)
print("enemies", len(E), "->", out)
print("roster without a card:", [s for s in seed if s not in {e["slug"] for e in E}])
