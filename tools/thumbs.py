"""Render a transparent thumbnail of every creature through the page's own viewer.
python -I thumbs.py BASE_URL [DUNGEON]     (DUNGEON is the data file name, default ruins)
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io

base = sys.argv[1]
dn = sys.argv[2] if len(sys.argv) > 2 else "ruins"
R = Path("C:/Users/joshu/wow-atlas")
data = json.load(open(R / f"site/data/{dn}.json", encoding="utf-8"))
out = R / "site/thumbs" / data.get("assets", ""); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 320, "height": 320}, device_scale_factor=1)
    for e in data["enemies"]:
        pg.goto(f"{base}?thumb&d={dn}&v=beasts&beast={e['slug']}", wait_until="load")
        pg.wait_for_function(f"window.__beastReady === '{e['slug']}'", timeout=60000)
        pg.wait_for_timeout(600)
        png = pg.locator("#stage").screenshot(omit_background=True)
        im = Image.open(io.BytesIO(png)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox() or (0, 0, im.width, im.height)
        cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        half = max(bb[2] - bb[0], bb[3] - bb[1]) / 2 * 1.12 + 4
        im = im.crop((int(cx - half), int(cy - half), int(cx + half), int(cy + half)))
        im.resize((200, 200), Image.LANCZOS).save(out / f"{e['slug']}.webp", quality=82)
        print(e["slug"], flush=True)
    b.close()
