"""Print each creature's ability rows above Dazed with the live client's spell facts, so a person can pick the real ones.
python -I live_dump.py SUB      (reads work/SUB/wh/npc/abilities.json and work/SUB/spells_live.json)
"""
import json, sys
from pathlib import Path

W = Path("C:/Users/joshu/wow-atlas/work") / sys.argv[1]
ab = json.load(open(W / "wh/npc/abilities.json", encoding="utf-8"))
live = json.load(open(W / "spells_live.json", encoding="utf-8"))
out = []
for nid, v in ab.items():
    out.append(f"== {nid} {v['name']}")
    for s in v["spells"]:
        if s["id"] == 1604:
            break
        x = live.get(str(s["id"]))
        if not x:
            out.append(f"   {s['id']} (no live row)")
            continue
        eff = "; ".join(f"e{e['eff']} a{e['aura']} b{e['base']} p{e['period']} r{e['radius']} t{e['trigger']} m{e['misc']}" for e in x["effects"])
        out.append(f"   {s['id']} {x['name']} cast {x['cast_ms']} dur {x['dur_ms']} cd {x['cd_ms']} rng {x['range']} sch {x['school']} "
                   f"disp {x['dispel']} mech {x['mechanic']} | {eff} | {(x['text'] or '')[:170]} | aura: {(x['aura'] or '')[:110]}")
txt = "\n".join(out)
(W / "abilities_live.txt").write_text(txt, encoding="utf-8")
sys.stdout.buffer.write(txt.encode("utf-8", "replace"))
