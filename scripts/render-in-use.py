"""In-use render — cradle.stl + printer proxy box, gallery palette.

Adds a 78×152×143mm cube at the printer's installed position to give the
README in-use renders an actual subject. Reuses the same gallery scene
(warm-grey backdrop, soft 4-point lighting, AgX) as render-part.py.

Printer proxy placement matches host_object_proxy() in cradle.scad:
    x0 = side_step + (cradle_w_printer - pocket_w) / 2 + 1mm = 16
    y0 = wall_thickness + 1mm = 4
    z0 = base_thickness = 4
    size = 78 × 152 × 143

Usage:
    /home/node/blender/blender --background --python scripts/render-in-use.py -- \\
        --out PATH --angle {front-threequarter,front} --quality {draft,standard,hero}
"""

# ⛔ DOES NOT RUN ON THIS HOST (measured 2026-09-06). Blender is NOT installed on this host —
# not on PATH, no binary found. The /home/node/blender paths below are Jinn-container remnants.
# Deliberately NOT repointed: aiming them at a Blender that does not exist converts a loud
# ENOENT into a confusing one, and nothing here could be proved without the binary.
# Also dead: PROJECT below is "/workspace/projects/3d-printing" ("/workspace" does not
# exist here). Correct value is self-locating:
#     PROJECT = str(pathlib.Path(__file__).resolve().parents[1])
# Left unapplied because it cannot be verified without Blender — apply and prove together.
# To revive: install Blender, invoke as `blender --background --python <this script>`.


import argparse
import os
import sys
from math import radians

import bpy
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _render_device import configure_cycles_device  # noqa: E402

PROJECT = "/workspace/projects/3d-printing"
CRADLE_STL = os.path.join(PROJECT, "designs/ptouch-cradle/output/cradle.stl")

# Printer proxy — mm coords, matches host_object_proxy() in cradle.scad.
PRINTER_ORIGIN_MM = (16.0, 4.0, 4.0)
PRINTER_SIZE_MM = (78.0, 152.0, 143.0)

CRADLE_RGB = (0.150, 0.115, 0.070)   # ≈ sRGB #6f5b46 — deep mocha (matches greenlit comp #1 v2)
PRINTER_RGB = (0.020, 0.020, 0.022)  # near-black with a touch of cool — Brother PT-P750W is dark grey

ANGLE_PRESETS = {
    "front-threequarter": ((1.0, 1.3, 0.7),  0.45),
    "front":              ((0.0, 1.3, 0.4),  0.30),
}

QUALITY_PRESETS = {
    "draft":    {"engine": "BLENDER_EEVEE_NEXT", "samples": 64,  "res": (1280, 960),  "denoiser": False},
    "standard": {"engine": "CYCLES",             "samples": 192, "res": (1920, 1440), "denoiser": True},
    "hero":     {"engine": "CYCLES",             "samples": 768, "res": (2560, 1920), "denoiser": True},
}


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--angle", default="front-threequarter", choices=list(ANGLE_PRESETS))
    p.add_argument("--quality", default="standard", choices=list(QUALITY_PRESETS))
    return p.parse_args(argv)


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.objects):
        for item in list(c):
            c.remove(item)


def import_stl(path, name):
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj


def make_pla_material(name, rgb, roughness=0.60, sss=0.015):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = (0.5, 0.4, 0.3)
    return mat


def make_printer_material():
    """Brother printer body — dark satin plastic. Slightly higher roughness."""
    mat = bpy.data.materials.new(name="PrinterPlastic")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*PRINTER_RGB, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True


def setup_world():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.42, 0.40, 0.36, 1.0)
    bg.inputs["Strength"].default_value = 0.30


def setup_backdrop():
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Backdrop_Floor"
    fmat = bpy.data.materials.new(name="BackdropFloor")
    fmat.use_nodes = True
    fbsdf = fmat.node_tree.nodes["Principled BSDF"]
    fbsdf.inputs["Base Color"].default_value = (0.42, 0.42, 0.43, 1.0)
    fbsdf.inputs["Roughness"].default_value = 0.85
    floor.data.materials.append(fmat)

    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, -2.0, 1.5),
                                     rotation=(radians(90), 0, 0))
    wall = bpy.context.active_object
    wall.name = "Backdrop_Wall"
    wmat = bpy.data.materials.new(name="BackdropWall")
    wmat.use_nodes = True
    wbsdf = wmat.node_tree.nodes["Principled BSDF"]
    wbsdf.inputs["Base Color"].default_value = (0.10, 0.085, 0.065, 1.0)
    wbsdf.inputs["Roughness"].default_value = 0.90
    wall.data.materials.append(wmat)


def setup_lights():
    bpy.ops.object.light_add(type="AREA", location=(1.6, 2.0, 1.6))
    key = bpy.context.active_object
    key.data.energy = 200
    key.data.size = 1.4
    key.data.color = (1.00, 0.98, 0.96)
    key.rotation_euler = mathutils.Euler((radians(120), 0, radians(150)))

    bpy.ops.object.light_add(type="AREA", location=(-1.6, 1.4, 0.7))
    fill = bpy.context.active_object
    fill.data.energy = 80
    fill.data.size = 2.0
    fill.data.color = (0.97, 0.96, 0.94)
    fill.rotation_euler = mathutils.Euler((radians(95), 0, radians(-130)))

    bpy.ops.object.light_add(type="AREA", location=(1.4, -1.8, 0.6))
    rim = bpy.context.active_object
    rim.data.energy = 120
    rim.data.size = 1.0
    rim.data.color = (1.00, 0.96, 0.88)
    rim.rotation_euler = mathutils.Euler((radians(80), 0, radians(30)))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.2, 2.4))
    top = bpy.context.active_object
    top.data.energy = 55
    top.data.size = 2.4
    top.data.color = (1.00, 0.98, 0.95)


def setup_camera(angle, subject_z_norm):
    cam_loc, target_z_factor = ANGLE_PRESETS[angle]
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.active_object
    cam.data.lens = 50
    cam.data.sensor_width = 36
    target_z = subject_z_norm * target_z_factor
    target = mathutils.Vector((0, 0, target_z))
    look_dir = target - mathutils.Vector(cam.location)
    cam.rotation_euler = look_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


def configure_render(quality_key, out_path):
    q = QUALITY_PRESETS[quality_key]
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = q["res"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False

    engine = q["engine"]
    if engine == "BLENDER_EEVEE_NEXT":
        try:
            scene.render.engine = "BLENDER_EEVEE_NEXT"
        except TypeError:
            scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = engine

    if scene.render.engine == "CYCLES":
        scene.cycles.samples = q["samples"]
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.005 if quality_key == "hero" else 0.01
        configure_cycles_device(scene)
        if q["denoiser"]:
            scene.cycles.use_denoising = True
            for cand in ("OPENIMAGEDENOISE", "OPTIX", "NLM"):
                try:
                    scene.cycles.denoiser = cand
                    print(f"[in-use] Denoiser: {cand}")
                    break
                except (TypeError, RuntimeError):
                    continue
        else:
            scene.cycles.use_denoising = False

    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Base Contrast"
    except (TypeError, RuntimeError):
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    scene.render.filepath = os.path.abspath(out_path)


def main():
    args = parse_args()
    print(f"[in-use] angle={args.angle} quality={args.quality}")

    reset_scene()

    cradle = import_stl(CRADLE_STL, "Cradle")
    cradle_mat = make_pla_material("CradlePLA", CRADLE_RGB)
    assign(cradle, cradle_mat)

    # Printer proxy — cube primitive sized + positioned in mm coords
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    printer = bpy.context.active_object
    printer.name = "PrinterProxy"
    printer.scale = PRINTER_SIZE_MM
    px, py, pz = PRINTER_ORIGIN_MM
    pw, pd, ph = PRINTER_SIZE_MM
    printer.location = (px + pw / 2, py + pd / 2, pz + ph / 2)
    printer_mat = make_printer_material()
    assign(printer, printer_mat)

    bpy.context.view_layer.update()

    # Combined bbox (mm) BEFORE normalize — covers cradle + printer
    all_corners = []
    for obj in (cradle, printer):
        m = obj.matrix_world
        for v in obj.bound_box:
            all_corners.append(m @ mathutils.Vector(v))
    minc = mathutils.Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    maxc = mathutils.Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    size = maxc - minc
    center = (minc + maxc) * 0.5
    max_dim = max(size)
    print(f"[in-use] combined bbox {size.x:.1f}x{size.y:.1f}x{size.z:.1f} mm, max={max_dim:.1f}")

    # Group under empty pivot. Pivot at bbox center (mm), children parented with inverse.
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=center)
    pivot = bpy.context.active_object
    pivot.name = "InUsePivot"
    cradle.parent = pivot
    printer.parent = pivot
    cradle.matrix_parent_inverse = pivot.matrix_world.inverted()
    printer.matrix_parent_inverse = pivot.matrix_world.inverted()

    # Move pivot so combined bottom sits on z=0, centered XY at origin
    norm = 1.0 / max_dim
    pivot.location = (0, 0, (size.z * 0.5))   # mm
    pivot.scale = (norm, norm, norm)
    bpy.context.view_layer.update()
    pivot.location = (0, 0, (size.z * 0.5) * norm)

    subject_z_norm = size.z * norm

    setup_world()
    setup_backdrop()
    setup_lights()
    setup_camera(args.angle, subject_z_norm)

    configure_render(args.quality, args.out)
    bpy.ops.render.render(write_still=True)
    print(f"[in-use] PNG -> {args.out}")


if __name__ == "__main__":
    main()
