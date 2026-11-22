"""Print what a GLB holds: meshes, materials, textures, images, skins, clips.  python -I glb_peek.py FILE.glb [...]"""
import json, struct, sys

for f in sys.argv[1:]:
    b = open(f, "rb")
    magic, ver, total = struct.unpack("<III", b.read(12))
    n, kind = struct.unpack("<II", b.read(8))
    j = json.loads(b.read(n))
    mats = j.get("materials", [])
    print(f"{f}\n  bytes {total} meshes {len(j.get('meshes', []))} prims {sum(len(m['primitives']) for m in j.get('meshes', []))} "
          f"materials {len(mats)} textures {len(j.get('textures', []))} images {len(j.get('images', []))} skins {len(j.get('skins', []))} "
          f"anims {len(j.get('animations', []))} ext {j.get('extensionsUsed')}")
    for i, m in enumerate(mats[:12]):
        pbr = m.get("pbrMetallicRoughness", {})
        print(f"    mat {i} {m.get('name')} tex {pbr.get('baseColorTexture')} color {pbr.get('baseColorFactor')} alpha {m.get('alphaMode')}")
    for i, im in enumerate(j.get("images", [])[:12]):
        print(f"    img {i} {im.get('name')} {im.get('mimeType')} uri {str(im.get('uri'))[:60]} view {im.get('bufferView')}")
    used = {p.get("material") for m in j.get("meshes", []) for p in m["primitives"]}
    print("    materials used by prims:", sorted(x for x in used if x is not None), "prims without material:", sum(1 for m in j.get("meshes", []) for p in m["primitives"] if p.get("material") is None))
