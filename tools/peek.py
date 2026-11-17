import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
def show(x, depth=0, key="root"):
    pad = "  " * depth
    if isinstance(x, dict):
        print(f"{pad}{key}: dict({len(x)}) keys={list(x)[:15]}")
        if depth < 3:
            for k, v in list(x.items())[:12]:
                show(v, depth + 1, k)
    elif isinstance(x, list):
        print(f"{pad}{key}: list({len(x)})")
        if x and depth < 3:
            show(x[0], depth + 1, "[0]")
    else:
        s = str(x)
        print(f"{pad}{key}: {s[:200]}")
show(d)
