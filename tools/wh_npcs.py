"""Fetch Wowhead Forever NPC pages (one browser), save HTML, extract displayId, abilities and listviews.
python -I wh_npcs.py ZONE_NPCS.json OUT_DIR
"""
import json, re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

rows = json.load(open(sys.argv[1], encoding="utf-8"))
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
skip = {2673, 3570, 264850}
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36")
    for r in rows:
        nid = r["id"]
        if nid in skip:
            continue
        f = out / f"npc_{nid}.html"
        if not f.exists():
            pg.goto(f"https://www.wowhead.com/forever/npc={nid}", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(2500)
            f.write_text(pg.content(), encoding="utf-8")
            time.sleep(1)
        h = f.read_text(encoding="utf-8")
        disp = re.findall(r"displayId\s*=\s*(\d+)", h)
        disp2 = re.findall(r'"displayId":(\d+)', h)
        lvs = re.findall(r"template: '(\w+)', id: '([\w-]+)'", h)
        lvl = re.findall(r"Level: ([^<\[]{1,20})", h)
        cls = re.findall(r"Classification: ([^<\[]{1,30})", h)
        react = re.findall(r"React: ([^\]]{1,80})", h)
        res[nid] = {"name": r["name"], "display": list(dict.fromkeys(disp + disp2)), "listviews": lvs,
                    "level": lvl[:2], "class": cls[:1]}
        print(nid, r["name"], res[nid]["display"], lvl[:1], [l[1] for l in lvs], flush=True)
    b.close()
json.dump(res, open(out / "npcs_summary.json", "w", encoding="utf-8"), indent=1)
