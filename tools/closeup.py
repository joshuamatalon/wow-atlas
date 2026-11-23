"""Large front and side views of chosen creatures through the page's viewer, beside Wowhead's render.
python -I closeup.py BASE_URL DUNGEON OUT.png SLUG [SLUG ...]
"""
import io, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

base, dn, outp, slugs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
R = Path("C:/Users/joshu/wow-atlas")
data = json.load(open(R / f"site/data/{dn}.json", encoding="utf-8"))
disp = {e["slug"]: e["display"] for e in data["enemies"]}
S = 440
sheet = Image.new("RGB", (S * 3, S * len(slugs)), (30, 34, 42))
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": S, "height": S}, device_scale_factor=1)
    for i, s in enumerate(slugs):
        pg.goto(f"{base}?thumb&d={dn}&v=beasts&beast={s}", wait_until="load")
        pg.wait_for_function(f"window.__beastReady === '{s}'", timeout=60000)
        pg.wait_for_timeout(700)
        sheet.paste(Image.open(io.BytesIO(pg.locator("#stage").screenshot())).convert("RGB").resize((S, S)), (S, i * S))
        box = pg.locator("#stage").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + 110, cy, steps=8); pg.mouse.up()
        pg.wait_for_timeout(500)
        sheet.paste(Image.open(io.BytesIO(pg.locator("#stage").screenshot())).convert("RGB").resize((S, S)), (2 * S, i * S))
        f = R / "work/dl/whthumbs" / f"{disp[s]}.webp"
        if f.exists():
            ref = Image.open(f).convert("RGBA").resize((S, S))
            bg = Image.new("RGBA", (S, S), (40, 46, 56, 255)); bg.alpha_composite(ref)
            sheet.paste(bg.convert("RGB"), (0, i * S))
    b.close()
sheet.save(outp)
print(sheet.size)
