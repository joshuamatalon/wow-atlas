"""Print each creature's Wowhead ability rows with the client's spell facts beside them, so a person can pick the real ones.
python -I ability_dump.py NPC_DIR WAGO_SPELL_DIR OUT_DIR
Writes OUT_DIR/spells.txt and OUT_DIR/spells.csv (through wowgold/tools/spell_dump.py) and OUT_DIR/abilities_by_npc.txt.
"""
import csv, json, subprocess, sys
from pathlib import Path

npc_dir, wago, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
ab = json.load(open(npc_dir / "abilities.json", encoding="utf-8"))
ids = sorted({s["id"] for v in ab.values() for s in v["spells"]})
r = subprocess.run([sys.executable, "-I", "C:/Users/joshu/wowgold/tools/spell_dump.py", wago, "ids", *map(str, ids), "--csv", str(out / "spells.csv")],
                   capture_output=True, text=True, encoding="utf-8")
(out / "spells.txt").write_text(r.stdout, encoding="utf-8")
if r.returncode:
    sys.exit(r.stderr[-2000:])
rows = {int(x["id"]): x for x in csv.DictReader(open(out / "spells.csv", encoding="utf-8"))}
lines = []
for nid, v in ab.items():
    lines.append(f"== {nid} {v['name']}")
    for s in v["spells"]:
        x = rows.get(s["id"])
        if not x:
            lines.append(f"   {s['id']} (not in client tables)")
            continue
        lines.append(f"   {x['id']} {x['name']} [{x['school']}] cast {x['cast_s']} dur {x['dur_s']} cd {x['cd_s']} rng {x['range']} "
                     f"dispel {x['dispel']} mech {x['mechanic']} | {x['effects']} | {x['text'][:150]} | aura: {x['aura_text'][:90]}")
(out / "abilities_by_npc.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(ids), "spells;", len(ab), "creatures")
