"""Print the ARGS JSON for one export step of a dungeon subfolder.
python -I we_args.py SUB ex1|exchar3|spells
For spells, the ids are every row above Dazed (1604) on each creature's saved Wowhead page.
"""
import json, sys
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
sub, step = sys.argv[1], sys.argv[2]
W = R / "work" / sub
if step == "ex1":
    a = {"jobs": str(W / "creature_jobs.json").replace("\\", "/"), "out": str(W / "export").replace("\\", "/")}
elif step == "exchar3":
    a = {"chars": str(W / "creature_chars.json").replace("\\", "/"), "out": str(W / "export").replace("\\", "/")}
else:
    ab = json.load(open(W / "wh/npc/abilities.json", encoding="utf-8"))
    ids = []
    for v in ab.values():
        for s in v["spells"]:
            if s["id"] == 1604:
                break
            if s["id"] not in ids:
                ids.append(s["id"])
    a = {"ids": ids, "out": str(W / "spells_live.json").replace("\\", "/"), "icons": str(R / "site/icons").replace("\\", "/")}
print(json.dumps(a))
