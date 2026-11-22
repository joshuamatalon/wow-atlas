"""Send one command to the hidden wow.export and print its result.
Usage: python -I we.py CMD_FILE.js [timeout_s] [ARGS_JSON]
The file body is an async function body with args fs, path, S. ARGS_JSON, when given, reaches it as the const ARGS.
"""
import json, os, sys, time, shutil
from pathlib import Path

ROOT = Path("C:/Users/joshu/wow-atlas/work")
src = Path(sys.argv[1])
timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 120
args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
name = f"{int(time.time()*1000)}_{src.stem}"
out = ROOT / "we-out" / f"{name}.json"
tmp = ROOT / "we-cmd" / f"{name}.tmp"
tmp.write_text(f"const ARGS = {json.dumps(args)};\n" + src.read_text(encoding="utf-8"), encoding="utf-8")
tmp.rename(tmp.with_suffix(".js"))
t0 = time.time()
while time.time() - t0 < timeout:
    if out.exists():
        time.sleep(0.2)
        d = json.loads(out.read_text(encoding="utf-8"))
        s = json.dumps(d, indent=1, ensure_ascii=True)
        print(s[:int(os.environ.get("WE_MAX", "6000"))])
        sys.exit(0 if d.get("ok") else 1)
    time.sleep(0.3)
print("TIMEOUT", name)
sys.exit(2)
