"""Extract the 'abilities' listview (spell ids + names) from each saved Wowhead NPC page."""
import json, re, sys
from pathlib import Path

d = Path("C:/Users/joshu/wow-atlas/work/dl/wh/npc")
summ = json.load(open(d / "npcs_summary.json", encoding="utf-8"))
out = {}
for nid, v in summ.items():
    h = (d / f"npc_{nid}.html").read_text(encoding="utf-8")
    m = re.search(r"id: 'abilities'.*?data:\s*(\[.*?\])\s*\}\);", h, re.S)
    spells = []
    if m:
        try:
            for r in json.loads(m.group(1)):
                spells.append({"id": r.get("id"), "name": r.get("name")})
        except Exception as e:
            ids = re.findall(r'"id":(\d+)', m.group(1))
            spells = [{"id": int(i)} for i in ids]
    # spell name lookups from the g_spells table on the page
    for s in spells:
        if not s.get("name"):
            n = re.search(r"g_spells\[" + str(s["id"]) + r"\][^;]*?name_enus['\"]?:\s*['\"]([^'\"]+)", h)
            if n:
                s["name"] = n.group(1)
    out[nid] = {"name": v["name"], "spells": spells}
    print(nid, v["name"], [(s["id"], s.get("name")) for s in spells])
json.dump(out, open(d / "abilities.json", "w", encoding="utf-8"), indent=1)
