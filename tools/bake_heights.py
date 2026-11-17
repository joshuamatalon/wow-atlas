"""Run the page once headless, read the ground heights it probed, save work/heights.json, rebuild the data."""
import json, subprocess, sys
from playwright.sync_api import sync_playwright
R = "C:/Users/joshu/wow-atlas"
subprocess.run([sys.executable, "-I", R + "/tools/make_data.py"], check=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 400, "height": 400})
    pg.goto(sys.argv[1] + "?v=map", wait_until="load"); pg.wait_for_function("!!window.__ready", timeout=120000)
    h = pg.evaluate("window.__heights"); b.close()
old = {}
try: old = json.load(open(R + "/work/heights.json"))
except Exception: pass
old.update(h)
json.dump(old, open(R + "/work/heights.json", "w"), indent=0)
print("probed", len(h))
subprocess.run([sys.executable, "-I", R + "/tools/make_data.py"], check=True)
