import sys
from playwright.sync_api import sync_playwright
base = sys.argv[1]
with sync_playwright() as p:
    for eng in ("chromium", "webkit"):
        b = getattr(p, eng).launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] if eng == "chromium" else [])
        pg = b.new_page(viewport={"width": 393, "height": 852}, has_touch=True)
        errs = []; pg.on("pageerror", lambda x: errs.append(str(x)))
        pg.goto(base + "?v=map&stop=5", wait_until="load"); pg.wait_for_function("!!window.__ready"); pg.wait_for_timeout(1500)
        card = lambda: pg.eval_on_selector("#stopcard", "e => !e.classList.contains('hidden')")
        r = {"start": card()}
        pg.mouse.move(200, 250); pg.mouse.down()
        for i in range(12): pg.mouse.move(200 + i * 12, 250); pg.wait_for_timeout(16)
        pg.mouse.up(); pg.wait_for_timeout(300); r["after_drag"] = card()
        pg.screenshot(path=f"work/shots/tap_{eng}_before.png")
        pg.mouse.click(40, 330); pg.wait_for_timeout(1300); r["after_tap"] = card()
        r["label"] = pg.inner_text("#walkmeta").replace("\n", " / ")
        pg.screenshot(path=f"work/shots/tap_{eng}_after.png")
        pg.click("#next"); pg.wait_for_timeout(1200); r["next_opens"] = card(); r["next_label"] = pg.inner_text("#stopname")
        print(eng, r, errs); b.close()
