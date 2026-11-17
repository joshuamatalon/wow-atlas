"""Patch the downloaded wow.export copy: hidden window, CDP port, no cache upload, GLB exports."""
import json, re, sys
from pathlib import Path

app = Path(sys.argv[1])
pkg = json.loads((app / "package.json").read_text(encoding="utf-8"))
args = pkg["chromium-args"].replace("--disable-devtools", "").strip()
if "--remote-debugging-port" not in args:
    args += " --remote-debugging-port=9333"
pkg["chromium-args"] = args
pkg["window"]["show"] = False
pkg["window"]["focus"] = False
pkg["window"]["show_in_taskbar"] = False
(app / "package.json").write_text(json.dumps(pkg, indent=1), encoding="utf-8")

cfg = app / "src" / "default_config.jsonc"
t = cfg.read_text(encoding="utf-8")
out = Path(sys.argv[2]).as_posix()
subs = {
    "allowCacheCollection": "false",
    "exportCreatureFormat": '"GLB"',
    "exportModelFormat": '"GLB"',
    "modelsExportAnimations": "true",
    "exportDirectory": json.dumps(out),
}
for k, v in subs.items():
    t, n = re.subn(rf'("{k}":\s*)[^,\n]+', lambda m: m.group(1) + v, t)
    print(k, n)
cfg.write_text(t, encoding="utf-8")
print(pkg["chromium-args"])
