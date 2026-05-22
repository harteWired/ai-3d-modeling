"""One-off hero render of the ptouch-cradle assembly (cradle + tray).

Usage:
    blender --background --python scripts/render-ptouch-assembly.py -- \
        --out PATH [--quality {standard,hero}] [--samples N]

Loads both STLs, positions the tray at the offset from .combined-bare.scad,
applies tan/sand to the tray and a deeper warm grey to the cradle, lights
for fillet/chamfer visibility, renders.
"""

import argparse
import os
import sys
from math import radians

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _render_device import configure_cycles_device  # noqa: E402

# Tray translation from designs/ptouch-cradle/.combined-bare.scad:
#     translate([3.4, 160.35, 4]) tray();
TRAY_OFFSET_MM = (3.4, 160.35, 4.0)


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--cradle-stl", default="designs/ptouch-cradle/output/cradle.stl")
    p.add_argument("--tray-stl",   default="designs/ptouch-cradle/output/tray.stl")
    p.add_argument("--quality", choices=["draft", "standard", "hero"], default="standard")
    p.add_argument("--samples", type=int, default=None)
    p.add_argument("--resolution", default=None)
    return p.parse_args(argv)


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in [bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.objects]:
        for item in list(col):
            col.remove(item)


def import_stl(path, name):
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj


def make_material(name, base_color, roughness, metallic=0.0, sss=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in bsdf.inputs:    # Blender 4.x
        bsdf.inputs["Subsurface Weight"].default_value = sss
    elif "Subsurface" in bsdf.inputs:          # Blender 3.x
        bsdf.inputs["Subsurface"].default_value = sss
    return mat


def apply_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)

    # Limited Dissolve collapses coplanar triangle pairs (the right-triangle
    # splits on flat or near-flat surfaces in STLs) into ngons. Without this,
    # diagonal hypotenuse edges show as faint creases under glancing light
    # because adjacent triangles' normals differ by tiny floating-point amounts.
    # 5° threshold is conservative — preserves true edges (printer-pocket
    # corners, fillet boundaries) while flattening the triangulation noise.
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.dissolve_limited(angle_limit=radians(5))
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.shade_smooth()
    if hasattr(bpy.ops.object, "shade_auto_smooth"):
        bpy.ops.object.shade_auto_smooth(angle=radians(60))

    # Subdivision Surface (Catmull-Clark, level 1) — smooths slab-stack
    # boundaries (e.g. the tray's 16-slab corner blend) and softens triangulation
    # discontinuities in one pass. Combined with auto-smooth, gives clean
    # product-render geometry without false creases.
    if "Subsurf" not in obj.modifiers:
        sub = obj.modifiers.new(name="Subsurf", type="SUBSURF")
        sub.subdivision_type = "CATMULL_CLARK"
        sub.levels = 1
        sub.render_levels = 1


def main():
    args = parse_args()

    quality_map = {
        "draft":    {"engine": "BLENDER_EEVEE_NEXT", "samples": 64,  "resolution": "1280x960"},
        "standard": {"engine": "CYCLES",             "samples": 128, "resolution": "1920x1440"},
        "hero":     {"engine": "CYCLES",             "samples": 512, "resolution": "2560x1920"},
    }
    q = quality_map[args.quality]
    if args.samples is not None:
        q["samples"] = args.samples
    if args.resolution:
        q["resolution"] = args.resolution

    reset_scene()

    # ---- Import both parts ----
    cradle = import_stl(os.path.abspath(args.cradle_stl), "Cradle")
    tray = import_stl(os.path.abspath(args.tray_stl), "Tray")

    # ---- Position tray relative to cradle (from .combined-bare.scad) ----
    tray.location = TRAY_OFFSET_MM

    # ---- Compute combined bbox and normalize the WHOLE assembly to max-dim=1.0 ----
    all_verts = []
    for obj in (cradle, tray):
        for v in obj.data.vertices:
            all_verts.append(obj.matrix_world @ v.co)
    xs = [v.x for v in all_verts]; ys = [v.y for v in all_verts]; zs = [v.z for v in all_verts]
    bb_min = (min(xs), min(ys), min(zs))
    bb_max = (max(xs), max(ys), max(zs))
    raw_max = max(bb_max[0]-bb_min[0], bb_max[1]-bb_min[1], bb_max[2]-bb_min[2])
    cx, cy = (bb_max[0]+bb_min[0])/2, (bb_max[1]+bb_min[1])/2
    z_min = bb_min[2]

    # Center on XY origin, sit on z=0, scale so max dim = 1.0
    norm = 1.0 / raw_max
    for obj in (cradle, tray):
        obj.location = (
            (obj.location.x - cx) * norm,
            (obj.location.y - cy) * norm,
            (obj.location.z - z_min) * norm,
        )
        obj.scale = (norm, norm, norm)
    bpy.ops.object.select_all(action="DESELECT")
    cradle.select_set(True); tray.select_set(True)
    bpy.context.view_layer.objects.active = cradle
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

    # ---- Materials: two shades of beige/brown, both matte ----
    # Tuned for a bright catalog-style scene: saturated enough that the colors
    # read clearly against a near-white backdrop without going pale.
    tray_mat = make_material("TrayPLA",
                             base_color=(0.74, 0.60, 0.40),
                             roughness=0.65,
                             sss=0.03)
    cradle_mat = make_material("CradlePLA",
                               base_color=(0.36, 0.26, 0.17),
                               roughness=0.65,
                               sss=0.02)
    apply_material(tray, tray_mat)
    apply_material(cradle, cradle_mat)

    # ---- World: gentle neutral ambient (catalog-cyc feel) ----
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.95, 0.95, 0.96, 1.0)
    bg.inputs["Strength"].default_value = 0.5

    # ---- Backdrop: large light-grey sweep ----
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Backdrop"
    floor_mat = make_material("Backdrop", base_color=(0.82, 0.82, 0.83), roughness=0.85)
    apply_material(floor, floor_mat)

    # ---- Lighting tuned for fillet/chamfer visibility ----
    # Key light: lower angle and warmer — long sweeping highlights along curved transitions
    # Tray is now at +Y (front of camera). Lights placed accordingly: key from
    # camera-right, fill from camera-left, rim from behind-and-above (-Y/back).
    # ID-style softbox lighting — broad, diffuse, near-even from key and fill,
    # no dramatic rim. The bright world contributes most of the ambient; lights
    # add gentle directional shaping, not contrast.
    # Two large soft lights — minimal contrast, gentle directional shaping.
    # No rim, no top fill — the bright world handles ambient.
    bpy.ops.object.light_add(type="AREA", location=(1.6, 0.8, 2.0))
    key = bpy.context.active_object
    key.name = "Key"
    key.data.energy = 60
    key.data.size = 3.5
    key.data.color = (1.0, 0.98, 0.95)
    key.rotation_euler = (radians(120), 0, radians(35))

    bpy.ops.object.light_add(type="AREA", location=(-1.4, 0.4, 1.6))
    fill = bpy.context.active_object
    fill.name = "Fill"
    fill.data.energy = 40
    fill.data.size = 4.5
    fill.data.color = (0.97, 0.98, 1.0)
    fill.rotation_euler = (radians(110), 0, radians(-30))

    # ---- Camera: tray-front three-quarter, raised for a more top-down read ----
    # Tray is at +Y (the user-front of the assembly). Camera sits on +Y looking
    # back at -Y (toward the printer-pocket end of the cradle).
    z_top = max(v.z for o in (cradle, tray) for v in (o.matrix_world @ vv.co for vv in o.data.vertices))
    # Higher angle, looking down into the tray and along the cradle. Less of the
    # inside walls visible from this angle, so the interior reads cleaner.
    cam_loc = (0.85, 1.25, z_top * 0.5 + 1.45)

    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    cam.name = "HeroCam"
    cam.data.lens = 70   # slight telephoto — flatters the form, less perspective distortion at close range
    cam.data.sensor_width = 36

    # Aim slightly toward the tray (+Y) so it fills the foreground.
    target = bpy.data.objects.new("CamTarget", None)
    target.location = (0, 0.20, z_top * 0.4)
    bpy.context.collection.objects.link(target)
    constraint = cam.constraints.new(type="TRACK_TO")
    constraint.target = target
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    scene = bpy.context.scene
    scene.camera = cam

    # ---- Render config ----
    width, _, height = q["resolution"].partition("x")
    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.engine = q["engine"] if q["engine"] != "BLENDER_EEVEE_NEXT" else (
        "BLENDER_EEVEE_NEXT" if hasattr(scene, "eevee") else "BLENDER_EEVEE"
    )
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = q["samples"]
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.005
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        configure_cycles_device(scene)
    # Filmic with normal contrast — softer falloff than "Medium High", lifts
    # shadow detail so the warm beige palette reads without going muddy.
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium Contrast"
    scene.view_settings.exposure = 0.0  # bright world + light backdrop don't need lift

    print(f"[ptouch-assembly] cradle: {cradle.dimensions}  tray: {tray.dimensions}")
    print(f"[ptouch-assembly] z_top normalized: {z_top:.3f}")
    print(f"[ptouch-assembly] camera: {cam_loc}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    scene.render.filepath = os.path.abspath(args.out)
    bpy.ops.render.render(write_still=True)
    print(f"[ptouch-assembly] DONE -> {args.out}")


if __name__ == "__main__":
    main()
