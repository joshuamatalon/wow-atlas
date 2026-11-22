"""List every mesh node of a GLB with its material and triangle count.  python -I glb_meshes.py FILE.glb"""
import json, struct, sys

b = open(sys.argv[1], "rb")
b.read(12)
n, kind = struct.unpack("<II", b.read(8))
j = json.loads(b.read(n))
mats = [m.get("name") for m in j.get("materials", [])]
for node in j.get("nodes", []):
    if "mesh" not in node:
        continue
    m = j["meshes"][node["mesh"]]
    for p in m["primitives"]:
        tris = j["accessors"][p["indices"]]["count"] // 3 if "indices" in p else 0
        print(f"{node.get('name'):55s} mat {mats[p['material']] if p.get('material') is not None else None!s:38s} tris {tris:5d} skin {node.get('skin')}")
