"""Build the export job list (and roster seed) from Wowhead display ids plus the client display tables."""
import csv, json, re, sys
from pathlib import Path

W = Path("C:/Users/joshu/wow-atlas/work")
cdi = {r["ID"]: r for r in csv.DictReader(open(W / "dl/wago/CreatureDisplayInfo.csv", encoding="utf-8"))}
cmd = {r["ID"]: r for r in csv.DictReader(open(W / "dl/wago/CreatureModelData.csv", encoding="utf-8"))}
s = json.load(open(W / "dl/wh/npc/npcs_summary.json", encoding="utf-8"))
jobs, chars, roster = [], [], []
for nid, v in s.items():
    d = v["display"][0]
    r = cdi[d]
    slug = re.sub(r"[^a-z0-9]+", "-", v["name"].lower()).strip("-")
    m = cmd[r["ModelID"]]
    entry = {"npc": int(nid), "name": v["name"], "slug": slug, "display": int(d), "fdid": int(m["FileDataID"]),
             "tex": [int(r[f"TextureVariationFileDataID_{i}"]) for i in range(4) if int(r[f"TextureVariationFileDataID_{i}"] or 0) > 0],
             "scale": float(r["CreatureModelScale"]), "extra": int(r["ExtendedDisplayInfoID"])}
    roster.append(entry)
    (chars if entry["extra"] else jobs).append(entry)
json.dump(jobs, open(W / "creature_jobs.json", "w"), indent=1)
json.dump(chars, open(W / "creature_chars.json", "w"), indent=1)
json.dump(roster, open(W / "roster_seed.json", "w"), indent=1)
print(len(jobs), "model jobs;", len(chars), "character jobs:", [c["name"] for c in chars])
