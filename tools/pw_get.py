"""Headless fetch with Playwright Chromium. Prints final URL, title and page text (or saves HTML).
python -I pw_get.py URL [OUT_HTML] [wait_ms]
"""
import sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
wait = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36")
    r = pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(wait)
    print("STATUS", r.status if r else None, "URL", pg.url)
    print("TITLE", pg.title())
    html = pg.content()
    if out:
        open(out, "w", encoding="utf-8").write(html)
        print("saved", len(html))
    else:
        t = pg.inner_text("body")
        sys.stdout.buffer.write(t[:6000].encode("utf-8", "replace"))
    b.close()
