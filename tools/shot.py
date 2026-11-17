"""Headless screenshots of the atlas. Never shows a window.
python -I shot.py BASE_URL OUT_DIR SPEC.json
SPEC: [{"name":..., "q":"?v=map&stop=3", "device":"iphone"|"desktop", "engine":"chromium"|"webkit",
        "wait":"__ready"|"__beastReady"|..., "drag":[x0,y0,x1,y1], "ms":1500, "dpr":1}]
"""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

base, out, spec = sys.argv[1], Path(sys.argv[2]), json.load(open(sys.argv[3], encoding="utf-8"))
out.mkdir(parents=True, exist_ok=True)
report = []
with sync_playwright() as p:
    browsers = {}
    for s in spec:
        eng = s.get("engine", "chromium")
        if eng not in browsers:
            args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] if eng == "chromium" else []
            browsers[eng] = getattr(p, eng).launch(headless=True, args=args)
        b = browsers[eng]
        if s.get("device", "iphone") == "iphone":
            ctx = b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=s.get("dpr", 1), is_mobile=eng != "firefox" and eng == "chromium", has_touch=True)
        else:
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=s.get("dpr", 1))
        pg = ctx.new_page()
        errs, reqs = [], {"bytes": 0, "n": 0, "big": []}
        pg.on("console", lambda m, e=errs: e.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda x, e=errs: e.append(f"pageerror: {x}"))
        def on_resp(r, reqs=reqs):
            try:
                n = len(r.body()); reqs["bytes"] += n; reqs["n"] += 1
                if n > 300000: reqs["big"].append([r.url.split("/")[-1], n])
            except Exception:
                pass
        pg.on("response", on_resp)
        t0 = time.time()
        pg.goto(base + s.get("q", ""), wait_until="load", timeout=120000)
        w = s.get("wait", "__ready")
        try:
            pg.wait_for_function(f"!!window.{w}", timeout=s.get("timeout", 90000))
        except Exception as e:
            errs.append(f"wait {w} failed: {e}")
        loaded = time.time() - t0
        pg.wait_for_timeout(s.get("ms", 1500))
        for act in s.get("eval", []):
            pg.evaluate(act); pg.wait_for_timeout(s.get("ms", 1500))
        if "drag" in s:
            pg.screenshot(path=str(out / f"{s['name']}_a.png"))
            x0, y0, x1, y1 = s["drag"]
            pg.mouse.move(x0, y0); pg.mouse.down()
            for i in range(1, 21):
                pg.mouse.move(x0 + (x1 - x0) * i / 20, y0 + (y1 - y0) * i / 20); pg.wait_for_timeout(16)
            pg.mouse.up(); pg.wait_for_timeout(1200)
        pg.screenshot(path=str(out / f"{s['name']}.png"))
        report.append({"name": s["name"], "engine": eng, "loaded_s": round(loaded, 1), "bytes": reqs["bytes"], "requests": reqs["n"], "big": reqs["big"], "errors": errs[:12]})
        ctx.close()
    for b in browsers.values():
        b.close()
print(json.dumps(report, indent=1))
