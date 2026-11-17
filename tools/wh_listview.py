"""Pull the data array of one Wowhead Listview (by id) out of a saved page. Prints JSON.
python -I wh_listview.py PAGE.html LISTVIEW_ID OUT.json
"""
import json, re, sys

h = open(sys.argv[1], encoding="utf-8").read()
lid = sys.argv[2]
m = re.search(r"new Listview\(\{[^{}]{0,400}?id: '" + re.escape(lid) + r"'", h)
if not m:
    sys.exit("listview not found")
i = h.index("data:", m.start())
i = h.index("[", i)
depth, j, instr, esc = 0, i, False, False
while True:
    c = h[j]
    if instr:
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == "[": depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
    j += 1
data = json.loads(h[i:j + 1])
json.dump(data, open(sys.argv[3], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(data), "rows; keys:", sorted({k for r in data for k in r})[:40])
