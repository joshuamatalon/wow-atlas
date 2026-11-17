"""Blender (background) script: import wow.export ADT OBJ tiles with placements, export one GLB.
blender -b --factory-startup --python bl_assemble.py -- MAP_DIR OUT.glb [textures 0|1] [m2 0|1]
"""
import sys, os, glob, json, types
import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
map_dir, out_glb = argv[0], argv[1]
tex = len(argv) > 2 and argv[2] == "1"
m2 = len(argv) <= 3 or argv[3] == "1"

sys.path.insert(0, "C:/Users/joshu/wow-atlas/work/dl/wowexport/app/addon")
from io_scene_wowobj import import_wowobj as W

bpy.ops.wm.read_factory_settings(use_empty=True)
settings = types.SimpleNamespace(
    allowDuplicates=False, createDoodadSetCollections=False, createEmissiveMaterials=False,
    createVertexGroups=False, importGOBJ=True, importLiquid=False, importM2=m2, importTextures=tex,
    importUVAnimations=False, importWMO=True, importWMOSets=False, name="", useAlpha=tex,
    useTerrainBlending=False,
)
tiles = sorted(glob.glob(os.path.join(map_dir, "adt_*.obj")))
for t in tiles:
    print("[assemble] tile", t, flush=True)
    W.importWoWOBJAddon(t, settings)

objs = [o for o in bpy.data.objects if o.type == "MESH"]
tris = 0
for o in objs:
    tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
bb = [float("inf")] * 3 + [float("-inf")] * 3
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ __import__("mathutils").Vector(c)
        for i in range(3):
            bb[i] = min(bb[i], w[i]); bb[3 + i] = max(bb[3 + i], w[i])
info = {"objects": len(objs), "tris": tris, "bbox": bb,
        "names": sorted({o.name.split(".")[0] for o in objs})[:400]}
with open(out_glb + ".info.json", "w") as f:
    json.dump(info, f, indent=1)
print("[assemble] objects", len(objs), "tris", tris, "bbox", bb, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=out_glb.replace(".glb", ".blend"))
bpy.ops.export_scene.gltf(filepath=out_glb, export_format="GLB", export_materials="EXPORT" if tex else "NONE",
                          export_apply=True, export_extras=False, export_yup=True)
print("[assemble] done", flush=True)
