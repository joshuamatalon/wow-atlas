"""Check the page's words: limits per card, one sentence per boss step, no em dash, no source marks, no damage numbers.
Writes work/copy.txt (all visible prose) for prose_check.py.  python -I check_copy.py
"""
import json, re, sys
from pathlib import Path

R = Path("C:/Users/joshu/wow-atlas")
d = json.load(open(R / "site/data/ruins.json", encoding="utf-8"))
fails, lines = [], []
words = lambda s: len(re.findall(r"[A-Za-z0-9']+", s or ""))

for e in d["enemies"]:
    parts = [e.get("where"), e.get("tank"), e.get("group"), e.get("say")] + [a["name"] + " " + a["line"] for a in e["abilities"]]
    n = sum(words(p) for p in parts)
    if not e["boss"] and n > 50:
        fails.append(f"card over 50 words: {e['name']} ({n})")
    lines += [p for p in parts if p]
for s in d["stops"]:
    n = sum(words(t) for t in s["text"]) + words(s.get("say"))
    if n > 50:
        fails.append(f"stop over 50 words: {s['title']} ({n})")
    lines += s["text"] + ([s["say"]] if s.get("say") else [])
for b in d["bosses"]:
    if len(b["steps"]) > 6:
        fails.append(f"boss over six steps: {b['name']}")
    for st in b["steps"]:
        if len(re.findall(r"[.!?](\s|$)", st)) != 1:
            fails.append(f"step not one sentence: {b['name']}: {st}")
    lines += [b["intro"]] + b["steps"] + ([b["say"]] if b.get("say") else [])

text = "\n\n".join(lines)
html = (R / "site/index.html").read_text(encoding="utf-8")
blob = text + html + (R / "site/app.js").read_text(encoding="utf-8")
if "\u2014" in blob:
    fails.append("em dash found")
for pat in [r"\bSUSPECTED\b", r"\bCONFIRMED\b", r"\bsource[sd]?\b", r"\bwowhead\b", r"\bguide says\b", r"\bunverified\b", r"\[\w+\]"]:
    for m in re.finditer(pat, text, re.I):
        fails.append(f"source mark: {m.group(0)}")
for m in re.finditer(r"\b\d[\d,]*\s*(damage|dps|health|hp|threat)\b", text, re.I):
    fails.append(f"damage-type number: {m.group(0)}")
(R / "work/copy.txt").write_text(text, encoding="utf-8")
print(f"{len(lines)} lines checked, {words(text)} words")
print("\n".join(fails) if fails else "no failures")
sys.exit(1 if fails else 0)
