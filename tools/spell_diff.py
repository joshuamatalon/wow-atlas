"""Print the live-client spell facts (tools/cmd/spells.js output) and flag any that differ from an older table dump.
python -I spell_diff.py SPELLS_LIVE.json [OLD_SPELLS.csv]
"""
import csv, json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
live = json.load(open(sys.argv[1], encoding="utf-8"))
old = {int(r["id"]): r for r in csv.DictReader(open(sys.argv[2], encoding="utf-8"))} if len(sys.argv) > 2 else {}
DISPEL = {0: "", 1: "Magic", 2: "Curse", 3: "Disease", 4: "Poison", 5: "Stealth", 9: "Enrage"}
diffs = 0
for sid, s in live.items():
    eff = "; ".join(f"e{e['eff']}/a{e['aura']}:{e['base']:g}" + (f" per {e['period']}ms" if e["period"] else "") + (f" r{e['radius']:g}yd" if e["radius"] else "")
                    + (f" ->{e['trigger']}" if e["trigger"] else "") + (f" misc {e['misc']}" if e["eff"] in (28, 41, 56) else "") + (f" chain {e['chain']}" if e.get("chain") else "")
                    for e in s["effects"])
    print(f"{sid} {s['name']} cast {s['cast_ms']/1000:g}s dur {s['dur_ms']/1000:g}s cd {s['cd_ms']/1000:g}s range {s['range']} dispel {DISPEL.get(s['dispel'], s['dispel'])} mech {s['mechanic']} icon {s['icon']}")
    print(f"     {eff}")
    print(f"     {(s['text'] or '').replace(chr(10), ' ')[:230]}")
    o = old.get(int(sid))
    if o:
        for k, a, b in [("name", s["name"], o["name"]), ("cast", s["cast_ms"] / 1000, float(o["cast_s"])), ("dur", s["dur_ms"] / 1000, float(o["dur_s"])),
                        ("cd", s["cd_ms"] / 1000, float(o["cd_s"])), ("dispel", DISPEL.get(s["dispel"], str(s["dispel"])), o["dispel"])]:
            if a != b:
                diffs += 1
                print(f"     DIFFERS from old dump: {k} live={a} old={b}")
print("differences from the old dump:", diffs)
