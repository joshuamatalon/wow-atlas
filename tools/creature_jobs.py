"""Build the export job list (and roster seed) from Wowhead display ids plus the client display tables.
python -I creature_jobs.py            (Ruins: reads work/dl/wh/npc, writes work/)
python -I creature_jobs.py dm         (another dungeon: reads work/dm/wh/npc, writes work/dm/)
"""
import csv, json, re, sys
from pathlib import Path

W = Path("C:/Users/joshu/wow-atlas/work")
sub = sys.argv[1] if len(sys.argv) > 1 else ""
src = (W / sub / "wh/npc") if sub else (W / "dl/wh/npc")
out = (W / sub) if sub else W
cdi = {r["ID"]: r for r in csv.DictReader(open(W / "dl/wago/CreatureDisplayInfo.csv", encoding="utf-8"))}
cmd = {r["ID"]: r for r in csv.DictReader(open(W / "dl/wago/CreatureModelData.csv", encoding="utf-8"))}
s = json.load(open(src / "npcs_summary.json", encoding="utf-8"))
jobs, chars, roster = [], [], []
for nid, v in s.items():
    d = v["display"][0]
    r = cdi[d]
    slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
    m = cmd[r["ModelID"]]
    entry = {"npc": int(nid), "name": v["name"], "slug": slug, "display": int(d), "fdid": int(m["FileDataID"]),
             "tex": [int(r[f"TextureVariationFileDataID_{i}"]) for i in range(4) if int(r[f"TextureVariationFileDataID_{i}"] or 0) > 0],
             "scale": float(r["CreatureModelScale"]), "extra": int(r["ExtendedDisplayInfoID"]),
             "level": (v.get("level") or [""])[0].strip(), "rank": (v.get("class") or [""])[0].strip()}
    roster.append(entry)
    (chars if entry["extra"] else jobs).append(entry)
json.dump(jobs, open(out / "creature_jobs.json", "w"), indent=1)
json.dump(chars, open(out / "creature_chars.json", "w"), indent=1)
json.dump(roster, open(out / "roster_seed.json", "w"), indent=1)
print(len(jobs), "model jobs:", [c["slug"] for c in jobs])
print(len(chars), "character jobs:", [c["slug"] for c in chars])
