"""Blender: crop the assembled dungeon to the Undercity footprint, simplify, export GLB + top render.
blender -b BASE.blend --python bl_crop.py -- OUT_DIR MARGIN TERRAIN_RATIO WMO_RATIO
"""
import sys, json, math, bpy, bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out_dir, margin, t_ratio, w_ratio = argv[0], float(argv[1]), float(argv[2]), float(argv[3])

def wbb(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
uc = [o for o in meshes if o.name.startswith("undercity")][0]
lo, hi = wbb(uc)
info = {"undercity_bbox": [lo, hi], "undercity_matrix": [list(r) for r in uc.matrix_world],
        "undercity_parent_loc": list(uc.parent.matrix_world.translation) if uc.parent else None}
x0, y0, x1, y1 = lo[0] - margin, lo[1] - margin, hi[0] + margin, hi[1] + margin
info["crop"] = [x0, y0, x1, y1]

keep = []
for o in meshes:
    a, b = wbb(o)
    if b[0] < x0 or a[0] > x1 or b[1] < y0 or a[1] > y1:
        bpy.data.objects.remove(o, do_unlink=True)
        continue
    keep.append(o)

info["kept"] = []
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.data = o.data.copy()
    o.select_set(True)
bpy.context.view_layer.objects.active = keep[0]
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()
for o in keep:
    info.setdefault("applied", []).append([o.name, [list(v) for v in wbb(o)]])
    bm = bmesh.new(); bm.from_mesh(o.data)
    if o.name.startswith("adt_"):
        dead = [f for f in bm.faces if not (x0 <= f.calc_center_median().x <= x1 and y0 <= f.calc_center_median().y <= y1)]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bm.to_mesh(o.data); bm.free()
    o.data.materials.clear()
    if len(o.data.polygons) == 0:
        bpy.data.objects.remove(o, do_unlink=True); continue
    before = len(o.data.polygons)
    ratio = t_ratio if o.name.startswith("adt_") else w_ratio
    if ratio < 1:
        m = o.modifiers.new("dec", "DECIMATE"); m.ratio = ratio
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier="dec")
    info["kept"].append([o.name, before, len(o.data.polygons)])

# join into three named meshes
groups = {"terrain": [], "undercity": [], "ruins": []}
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    k = "terrain" if o.name.startswith("adt_") else "undercity" if o.name.startswith("undercity") else "ruins"
    groups[k].append(o)
for k, objs in groups.items():
    if not objs: continue
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    objs[0].name = k; objs[0].data.name = k
for o in list(bpy.data.objects):
    if o.type != "MESH": bpy.data.objects.remove(o, do_unlink=True)

info["tris"] = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects}
bpy.ops.export_scene.gltf(filepath=out_dir + "/map_raw.glb", export_format="GLB", export_materials="NONE",
                          export_yup=True, export_normals=True, export_texcoords=False)

# top-down orthographic render for checking against the floor maps
scn = bpy.context.scene
scn.render.engine = "BLENDER_WORKBENCH"
scn.display.shading.light = "MATCAP" if False else "STUDIO"
scn.display.shading.color_type = "OBJECT"
colors = {"terrain": (0.25, 0.35, 0.25, 1), "undercity": (0.4, 0.8, 1, 1), "ruins": (1, 0.7, 0.3, 1)}
for o in bpy.data.objects: o.color = colors.get(o.name, (1, 1, 1, 1))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scn.collection.objects.link(cam)
cam.data.type = "ORTHO"
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
cam.data.ortho_scale = max(x1 - x0, y1 - y0)
cam.location = (cx, cy, 2000); cam.rotation_euler = (0, 0, 0)
cam.data.clip_end = 5000
scn.camera = cam
scn.render.resolution_x = scn.render.resolution_y = 1400
scn.render.filepath = out_dir + "/top.png"
bpy.ops.render.render(write_still=True)
json.dump(info, open(out_dir + "/crop.json", "w"), indent=1)
print("[crop] done", json.dumps(info["tris"]))
