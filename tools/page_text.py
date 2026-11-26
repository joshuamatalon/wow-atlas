"""Save the visible text of web pages with a headless browser, one text file each.
python -I page_text.py OUT_DIR NAME=URL [NAME=URL ...]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36")
    for a in sys.argv[2:]:
        name, url = a.split("=", 1)
        try:
            r = pg.goto(url, wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(3500)
            t = pg.inner_text("body")
            (out / f"{name}.txt").write_text(t, encoding="utf-8")
            print(name, r.status if r else None, len(t), flush=True)
        except Exception as e:
            print(name, "ERR", str(e)[:160], flush=True)
    b.close()
