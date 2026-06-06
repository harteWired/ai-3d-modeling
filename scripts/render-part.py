"""Single-part hero render — gallery palette, parametric camera angle.

Adapted from render-assembly.py for one-STL recooks of the README's flat
OpenSCAD renders. Same gallery (warm-grey backdrop, soft 4-point lighting,
AgX) as the assembly script, just with one part and a selectable angle.

Usage:
    /home/node/blender/blender --background --python scripts/render-part.py -- \\
        --stl PATH                     (required)
        --out PATH                     (required)
        --angle {front-threequarter,top-threequarter,front,iso}
        --quality {draft,standard,hero}
        --rgb r,g,b                    (linear; default = mocha cradle tone)

Quality tiers:
    draft     - Eevee, 64 samples, 1280x960   (~30 s — composition check)
    standard  - Cycles, 192 samples, 1920x1440 (~3 min)  *default*
    hero      - Cycles, 768 samples, 2560x1920 (~12 min)

Color/SSS safety: SSS pinned at 0.015. Direct lights near-neutral
(no warm-amber tints) so warm hues stay beige instead of peach.
"""

import argparse
import os
import sys
from math import radians

import bpy
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _render_device import configure_cycles_device  # noqa: E402

# Linear RGB. Pushed darker than #1 (which read cream under bright lights).
# Deep warm-brown — should read mocha against the lighter floor.
DEFAULT_RGB = (0.150, 0.115, 0.070)  # ≈ sRGB #6f5b46 — deep mocha

ANGLE_PRESETS = {
    # location is (X, Y, Z) in NORMALIZED units (max_dim = 1.0).
    # target_z_factor multiplies subject.dimensions.z (normalized) for the look-at.
    # Pulled in ~30% from #1 for a tighter frame.
    "front-threequarter": ((1.0, 1.3, 0.7),  0.45),
    "rear-threequarter":  ((1.0, -1.3, 0.7), 0.45),
    "top-threequarter":   ((0.8, 1.1, 1.15), 0.30),
    "front":              ((0.0, 1.3, 0.15), 0.30),
    "iso":                ((1.2, 1.2, 1.1),  0.45),
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
    p.add_argument("--stl", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--angle", default="front-threequarter", choices=list(ANGLE_PRESETS))
    p.add_argument("--quality", default="standard", choices=list(QUALITY_PRESETS))
    p.add_argument("--rgb", default=None, help="Linear r,g,b override (e.g. '0.26,0.205,0.13')")
    p.add_argument("--transparent", action="store_true", help="Render with a transparent background (film_transparent)")
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
    """Two-piece sweep — cool-light floor + warm-dark vertical back wall.

    The horizon line gives the subject something to silhouette against, and the
    floor/back contrast adds depth (matches the gold-standard hero composition).
    """
    # Floor — cool-light grey, slight cool tint
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Backdrop_Floor"
    fmat = bpy.data.materials.new(name="BackdropFloor")
    fmat.use_nodes = True
    fbsdf = fmat.node_tree.nodes["Principled BSDF"]
    fbsdf.inputs["Base Color"].default_value = (0.42, 0.42, 0.43, 1.0)
    fbsdf.inputs["Roughness"].default_value = 0.85
    floor.data.materials.append(fmat)

    # Back wall — warm-dark, vertical, behind subject (-Y side from camera POV at +Y)
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, -2.0, 1.5),
                                     rotation=(radians(90), 0, 0))
    wall = bpy.context.active_object
    wall.name = "Backdrop_Wall"
    wmat = bpy.data.materials.new(name="BackdropWall")
    wmat.use_nodes = True
    wbsdf = wmat.node_tree.nodes["Principled BSDF"]
    wbsdf.inputs["Base Color"].default_value = (0.10, 0.085, 0.065, 1.0)  # warm dark taupe
    wbsdf.inputs["Roughness"].default_value = 0.90
    wall.data.materials.append(wmat)


def setup_lights():
    # Key — softened ~40% from #1 to keep mocha reading mocha (not cream)
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


def configure_render(quality_key, out_path, transparent=False):
    q = QUALITY_PRESETS[quality_key]
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = q["res"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = transparent

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
                    print(f"[part-render] Denoiser: {cand}")
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
    rgb = DEFAULT_RGB
    if args.rgb:
        rgb = tuple(float(x) for x in args.rgb.split(","))
    print(f"[part-render] stl={args.stl} angle={args.angle} quality={args.quality} rgb={rgb}")

    reset_scene()

    subject = import_stl(args.stl, "Subject")
    pla = make_pla_material("PartPLA", rgb)
    assign(subject, pla)

    bpy.context.view_layer.update()
    ws_corners = [subject.matrix_world @ mathutils.Vector(v) for v in subject.bound_box]
    minc = mathutils.Vector((min(c.x for c in ws_corners), min(c.y for c in ws_corners), min(c.z for c in ws_corners)))
    maxc = mathutils.Vector((max(c.x for c in ws_corners), max(c.y for c in ws_corners), max(c.z for c in ws_corners)))
    size = maxc - minc
    max_dim = max(size)
    print(f"[part-render] bbox {size.x:.1f}x{size.y:.1f}x{size.z:.1f} mm, max={max_dim:.1f}")

    # Move origin to geometry center, then place the part with bottom at z=0 centered on XY.
    # Order matters: set origin first so the subsequent location/scale pivot is correct.
    bpy.ops.object.select_all(action="DESELECT")
    subject.select_set(True)
    bpy.context.view_layer.objects.active = subject
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    norm = 1.0 / max_dim
    subject.scale = (norm, norm, norm)
    subject.location = (0.0, 0.0, (size.z * 0.5) * norm)
    bpy.context.view_layer.update()
    subject_z_norm = size.z * norm

    setup_world()
    if not args.transparent:
        setup_backdrop()
    setup_lights()
    setup_camera(args.angle, subject_z_norm)

    configure_render(args.quality, args.out, transparent=args.transparent)
    bpy.ops.render.render(write_still=True)
    print(f"[part-render] PNG -> {args.out}")


if __name__ == "__main__":
    main()
