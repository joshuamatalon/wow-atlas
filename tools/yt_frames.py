"""Save still frames of a YouTube video by seeking the page's own player in a headless browser.
python -I yt_frames.py VIDEO_ID OUT_DIR START_S END_S STEP_S [QUALITY=hd1080]
Writes OUT_DIR/f_SSSSS.jpg at the video's own resolution (drawn from the video element to a canvas).
Skips frames that already exist, so a stopped run can be started again.
"""
import base64, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

vid, out = sys.argv[1], Path(sys.argv[2])
t0, t1, step = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
qual = sys.argv[6] if len(sys.argv) > 6 else "hd1080"
out.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
GRAB = """async (t) => {
  const p = document.getElementById('movie_player'); const v = document.querySelector('video');
  if (!p || !v) return {err: 'no player'};
  if (p.getAdState && p.getAdState() === 1) return {err: 'ad'};
  p.seekTo(t, true); p.playVideo();
  const end = Date.now() + 15000;
  while (Date.now() < end) { if (!v.seeking && v.readyState >= 3 && v.currentTime >= t && v.currentTime - t < 6) break; await new Promise(r => setTimeout(r, 80)); }
  await new Promise(r => setTimeout(r, 120));
  if (v.seeking || v.readyState < 2) return {err: 'not ready', rs: v.readyState};
  const c = document.createElement('canvas'); c.width = v.videoWidth; c.height = v.videoHeight;
  c.getContext('2d').drawImage(v, 0, 0);
  return {w: c.width, h: c.height, t: v.currentTime, q: p.getPlaybackQuality && p.getPlaybackQuality(), jpg: c.toDataURL('image/jpeg', 0.9).split(',')[1]};
}"""
with sync_playwright() as pw:
    try:
        b = pw.chromium.launch(headless=True, channel="chrome", args=["--autoplay-policy=no-user-gesture-required", "--mute-audio"])
    except Exception:
        b = pw.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required", "--mute-audio"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto(f"https://www.youtube.com/watch?v={vid}", wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    pg.evaluate(f"""() => {{ const p = document.getElementById('movie_player'); if (p) {{ p.mute && p.mute(); p.playVideo && p.playVideo();
        if ('{qual}' !== 'auto' && p.setPlaybackQualityRange) p.setPlaybackQualityRange('{qual}', '{qual}'); }} }}""")
    for _ in range(40):   # sit through an ad, if one plays
        ad = pg.evaluate("() => { const p = document.getElementById('movie_player'); return p && p.getAdState ? p.getAdState() : -1; }")
        if ad != 1:
            break
        try:
            pg.locator(".ytp-skip-ad-button, .ytp-ad-skip-button, .ytp-ad-skip-button-modern").first.click(timeout=1000)
        except Exception:
            pass
        pg.wait_for_timeout(2000)
    pg.wait_for_timeout(2500)
    n = bad = 0
    for t in range(t0, t1 + 1, step):
        f = out / f"f_{t:05d}.jpg"
        if f.exists():
            continue
        r = None
        for attempt in range(3):
            r = pg.evaluate(GRAB, t)
            if r.get("jpg"):
                break
            pg.wait_for_timeout(1500)
        if not r or not r.get("jpg"):
            bad += 1
            print("miss", t, {k: v for k, v in (r or {}).items() if k != "jpg"}, flush=True)
            continue
        f.write_bytes(base64.b64decode(r["jpg"]))
        n += 1
        if n <= 3 or n % 50 == 0:
            print(t, r["w"], r["h"], r.get("q"), round(r["t"], 1), flush=True)
    b.close()
print("saved", n, "missed", bad)
