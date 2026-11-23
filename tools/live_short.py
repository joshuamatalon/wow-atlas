"""Short form of live_dump.py: one line per ability above Dazed, same-name rows folded, for picking the real ones.
python -I live_short.py SUB
"""
import json, sys
from pathlib import Path

W = Path("C:/Users/joshu/wow-atlas/work") / sys.argv[1]
ab = json.load(open(W / "wh/npc/abilities.json", encoding="utf-8"))
live = json.load(open(W / "spells_live.json", encoding="utf-8"))
o = []
for nid, v in ab.items():
    o.append("== " + nid + " " + v["name"])
    seen = set()
    for s in v["spells"]:
        if s["id"] == 1604:
            break
        x = live.get(str(s["id"]))
        if not x or x["name"] in seen:
            continue
        seen.add(x["name"])
        eff = " ".join("e%s/a%s/b%s/r%s/t%s/m%s" % (e["eff"], e["aura"], e["base"], e["radius"], e["trigger"], e["misc"]) for e in x["effects"])
        o.append("  %s %s c%s d%s cd%s r%s disp%s mech%s | %s | %s" % (s["id"], x["name"], x["cast_ms"], x["dur_ms"], x["cd_ms"], x["range"][1],
                                                                  x["dispel"], x["mechanic"], eff, (x["text"] or x["aura"] or "")[:120]))
sys.stdout.buffer.write("\n".join(o).encode("ascii", "replace"))
