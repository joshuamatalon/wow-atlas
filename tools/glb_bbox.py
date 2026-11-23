"""Print the real bounding box of each mesh node of a GLB, from the vertices its indices use.
python -I glb_bbox.py FILE.glb     (rest pose, no skinning; finds a part that sits away from the body)
"""
import json, struct, sys

f = open(sys.argv[1], "rb")
f.read(12)
n, _ = struct.unpack("<II", f.read(8))
j = json.loads(f.read(n))
bl, _ = struct.unpack("<II", f.read(8))
bin_ = f.read(bl)
CT = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}
NC = {"SCALAR": 1, "VEC3": 3}


def acc(i):
    a = j["accessors"][i]
    v = j["bufferViews"][a["bufferView"]]
    fmt, nc = CT[a["componentType"]], NC[a["type"]]
    size = struct.calcsize(fmt) * nc
    stride = v.get("byteStride") or size
    off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
    return [struct.unpack_from("<" + fmt * nc, bin_, off + k * stride) for k in range(a["count"])]


cache = {}
for node in j["nodes"]:
    if "mesh" not in node:
        continue
    for p in j["meshes"][node["mesh"]]["primitives"]:
        pi = p["attributes"]["POSITION"]
        pos = cache.setdefault(pi, acc(pi))
        idx = sorted({i[0] for i in acc(p["indices"])})
        pts = [pos[i] for i in idx]
        lo = [round(min(q[c] for q in pts), 2) for c in range(3)]
        hi = [round(max(q[c] for q in pts), 2) for c in range(3)]
        print(f"{node['name']:40s} {j['materials'][p['material']]['name']:20s} verts {len(idx):4d} lo {lo} hi {hi}")
