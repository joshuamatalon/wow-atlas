"""Loot per boss from the ForeverDB dungeon record, with slot, armor type and stats; marks warrior-tank picks."""
import json, sys
from collections import defaultdict

d = json.load(open(sys.argv[1], encoding="utf-8"))
items = d["items"]
INV = {1: "head", 2: "neck", 3: "shoulder", 5: "chest", 6: "waist", 7: "legs", 8: "feet", 9: "wrist", 10: "hands",
       11: "finger", 12: "trinket", 13: "one-hand", 14: "shield", 15: "ranged", 16: "back", 17: "two-hand", 20: "chest",
       21: "main hand", 22: "off hand", 23: "held in off hand", 26: "ranged"}
SUB = {(4, 1): "cloth", (4, 2): "leather", (4, 3): "mail", (4, 4): "plate", (4, 6): "shield", (2, 7): "sword",
       (2, 8): "two-hand sword", (2, 0): "axe", (2, 4): "mace", (2, 15): "dagger", (2, 10): "staff", (2, 2): "bow",
       (2, 3): "gun", (2, 5): "two-hand mace", (2, 1): "two-hand axe", (2, 6): "polearm", (2, 19): "wand", (2, 18): "crossbow"}
STAT = {3: "Agi", 4: "Str", 5: "Int", 6: "Spi", 7: "Sta", 12: "Def", 13: "Dodge", 14: "Parry", 15: "Block", 31: "Hit", 32: "Crit"}
by = defaultdict(list)
for r in d["loot"]:
    it = items.get(str(r["id"]), {})
    tank = any(p["spec"] == "Protection Warrior" for p in r.get("picks", []))
    stats = ", ".join(f"+{a} {STAT.get(s, s)}" for s, a in it.get("st", []) or [])
    by[r.get("boss") or "?"].append((r.get("pct", 0), it.get("n", r["id"]), it.get("q"), SUB.get((it.get("c"), it.get("sc")), f"{it.get('c')}/{it.get('sc')}"),
                                    INV.get(it.get("inv"), it.get("inv")), stats, tank, r["id"], it.get("ar")))
for boss, rows in by.items():
    print("==", boss)
    for row in sorted(rows, reverse=True):
        if row[2] is not None and row[2] < 2:
            continue
        print("  %5.1f%% %-32s q%s %-14s %-10s %-28s ar%s %s" % (row[0], row[1], row[2], row[3], row[4], row[5], row[8], "TANK" if row[6] else ""))
