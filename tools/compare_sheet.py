"""Download Wowhead's render of each creature (by display id) and lay it beside our thumbnail.  python -I compare_sheet.py"""
import json, io, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

R = Path("C:/Users/joshu/wow-atlas")
data = json.load(open(R / "site/data/ruins.json", encoding="utf-8"))
dl = R / "work/dl/whthumbs"; dl.mkdir(parents=True, exist_ok=True)
cells = []
for e in data["enemies"]:
    d = e["display"]; f = dl / f"{d}.webp"
    if not f.exists():
        url = f"https://wow.zamimg.com/modelviewer/classicplus/webthumbs/npc/{d % 256}/{d}.webp"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            f.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        except Exception as x:
            print("no wowhead thumb", e["slug"], d, x)
    ref = Image.open(f).convert("RGBA") if f.exists() else Image.new("RGBA", (200, 200), (60, 0, 0, 255))
    mine = Image.open(R / "site/thumbs" / f"{e['slug']}.webp").convert("RGBA")
    cells.append((e["name"], ref, mine))
cols = 4
cw, ch = 420, 230
sheet = Image.new("RGB", (cols * cw, ((len(cells) + cols - 1) // cols) * ch), (20, 24, 30))
dr = ImageDraw.Draw(sheet)
for i, (name, ref, mine) in enumerate(cells):
    x, y = (i % cols) * cw, (i // cols) * ch
    for j, im in enumerate((ref, mine)):
        im = im.copy(); im.thumbnail((200, 200))
        bg = Image.new("RGBA", (200, 200), (40, 46, 56, 255)); bg.alpha_composite(im, ((200 - im.width) // 2, (200 - im.height) // 2))
        sheet.paste(bg.convert("RGB"), (x + 5 + j * 205, y + 25))
    dr.text((x + 6, y + 6), f"{name}   (left: Wowhead, right: ours)", fill=(230, 230, 160))
sheet.save(R / "work/shots/compare.png")
print("sheet", sheet.size)
