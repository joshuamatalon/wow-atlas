"""Render a transparent thumbnail of every creature through the page's own viewer.  python -I thumbs.py BASE_URL"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io

base = sys.argv[1]
R = Path("C:/Users/joshu/wow-atlas")
data = json.load(open(R / "site/data/ruins.json", encoding="utf-8"))
out = R / "site/thumbs"; out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 320, "height": 320}, device_scale_factor=1)
    for e in data["enemies"]:
        pg.goto(f"{base}?thumb&v=beasts&beast={e['slug']}", wait_until="load")
        pg.wait_for_function(f"window.__beastReady === '{e['slug']}'", timeout=60000)
        pg.wait_for_timeout(600)
        png = pg.locator("#stage").screenshot(omit_background=True)
        Image.open(io.BytesIO(png)).convert("RGBA").resize((200, 200), Image.LANCZOS).save(out / f"{e['slug']}.webp", quality=82)
        print(e["slug"], flush=True)
    b.close()
