"""Assembly hero render: ptouch-cradle + tray, lofted three-quarter view.

Composes cradle.stl + tray.stl into a single Blender scene with per-part PLA
materials in a complementary-beige palette (khaki putty cradle / oat linen
tray). Lofted three-quarter camera (~38 deg elevation) reads the tray's low
front wall + r=20 side fillet sweeps without occlusion. Four-point lighting
on a warm-grey backdrop — gallery-like, not the moody dark studio of the
single-part heroes in scad-lib/blender-presets/studio.py.

NOT a 1:1 reproducer of the shipped hero. The canonical README hero
(docs/images/ptouch-cradle/assembly-hero.png) came from a separate render
session that landed on a warmer mocha cradle with a cream tray pulled forward
into the catch position. This script converged on a different valid solution
during scripted iteration. Treat as a starting point for re-rendering when
the geometry changes; if a future renderer needs to MATCH the shipped hero
exactly, the palette + camera here will need to be re-tuned.

Currently hard-coded for the ptouch-cradle assembly (palette + camera + tray
offset). To generalize, parametrize:
  - STL list with per-STL material RGB + role label
  - Tray-equivalent target offset for the camera bias
  - Backdrop / world tint

Usage (from project root, Blender 4.2+ at /home/node/blender):
    /home/node/blender/blender --background --python scripts/render-assembly.py -- \\
        --out designs/ptouch-cradle/output/assembly-hero-script.png \\
        --quality {draft,standard,hero}

Quality tiers:
    draft     - 64  samples Cycles 1280x960   (~80 s)
    standard  - 192 samples Cycles 1920x1440  (~3 min)  *default*
    hero      - 768 samples Cycles 2560x1920  (~12 min)

Color/SSS lessons captured in vault/projects/3d-printing/blender-integration.md
"Proof - Multi-Part Assembly Render". Short version: keep SSS < 0.025 and avoid
warm-amber direct lights on R-dominant beiges, or the assembly reads as peach.
"""

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
TRAY_STL   = os.path.join(PROJECT, "designs/ptouch-cradle/output/tray.stl")

# Tray placement relative to cradle origin, from .combined-bare.scad / .combined-use.scad
TRAY_OFFSET_MM = (3.4, 160.35, 4.0)

# Complementary beige palette — both PLA-family hues, deep value contrast.
# Linear values (Blender Principled BSDF expects linear input). AgX tone-mapping
# preserves these much better than Filmic, which would desaturate.
# Cradle: toasted walnut/amber (structural frame — anchors the composition)
# Tray:   wheat cream (the dynamic removable part, lifts visually against cradle)
# True beiges — pull green/yellow up vs red so neither reads as flesh/peach.
# Cradle: putty / khaki (deep, olive-leaning, not amber)
# Tray:   oat / linen (light, slightly cool-leaning, not cream-peach)
CRADLE_RGB = (0.190, 0.165, 0.105)   # khaki putty, ≈sRGB #7c6e5a
TRAY_RGB   = (0.700, 0.680, 0.540)   # oat linen, ≈sRGB #d8d2bb

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


def make_pla_material(name, rgb, roughness=0.55, sss=0.04):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Subsurface Weight" in bsdf.inputs:        # Blender 4.x
        bsdf.inputs["Subsurface Weight"].default_value = sss
        # Tint the subsurface slightly lighter than base — matches PLA filament look
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = (0.5, 0.4, 0.3)
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    # Smooth edges <30°, flat for sharper transitions — fillets read as smooth.
    for poly in obj.data.polygons:
        poly.use_smooth = True


def setup_world():
    """Soft warm-neutral environment — gallery / showroom feel, well lit."""
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    bg = nodes["Background"]
    # Soft warm grey — gentle GI fill so beiges keep saturation under direct lights
    bg.inputs["Color"].default_value = (0.42, 0.40, 0.36, 1.0)
    bg.inputs["Strength"].default_value = 0.30


def setup_backdrop():
    """Large curved sweep — soft warm taupe. Floor + back blend seamlessly."""
    # Floor plane (large, catches contact shadows)
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Backdrop"
    mat = bpy.data.materials.new(name="BackdropMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.38, 0.34, 0.30, 1.0)  # warm dark taupe
    bsdf.inputs["Roughness"].default_value = 0.85
    floor.data.materials.append(mat)


def setup_lights(subject_max_dim):
    """Three-point + soft top fill. Tuned so beige stays beige (not white blowouts).

    User-frame: tray sits at +Y end. Key from +Y side hits the tray front + side
    sweep. Rim from -Y back-edges the cradle's tall back wall.
    """
    # Key — user-front-right, raised. Slight warm tint (less aggressive than 0.90).
    bpy.ops.object.light_add(type="AREA", location=(1.6, 2.0, 1.6))
    key = bpy.context.active_object
    key.data.energy = 320
    key.data.size = 1.4
    key.data.color = (1.00, 0.98, 0.96)  # near-neutral, prevents pushing beiges into peach
    key.rotation_euler = mathutils.Euler((radians(120), radians(0), radians(150)))

    # Fill — user-front-left, low, cooler. Lifts shadow detail under tray side fillet.
    bpy.ops.object.light_add(type="AREA", location=(-1.6, 1.4, 0.7))
    fill = bpy.context.active_object
    fill.data.energy = 130
    fill.data.size = 2.0
    fill.data.color = (0.97, 0.96, 0.94)  # nearly neutral, very slight warm
    fill.rotation_euler = mathutils.Euler((radians(95), radians(0), radians(-130)))

    # Rim — user-back-right, low. Warm. Edges fillets on cradle silhouette.
    bpy.ops.object.light_add(type="AREA", location=(1.4, -1.8, 0.6))
    rim = bpy.context.active_object
    rim.data.energy = 200
    rim.data.size = 1.0
    rim.data.color = (1.00, 0.96, 0.88)  # was 0.78 in B channel — too orange, pushed peach
    rim.rotation_euler = mathutils.Euler((radians(80), radians(0), radians(30)))

    # Top — gentle overhead wash; softens contact shadow without flattening material.
    bpy.ops.object.light_add(type="AREA", location=(0.0, 0.2, 2.4))
    top = bpy.context.active_object
    top.data.energy = 90
    top.data.size = 2.4
    top.data.color = (1.00, 0.98, 0.95)


def setup_camera(tray_center_norm):
    """Lofted three-quarter from user-front, biased toward tray.

    Assembly is normalized so max_dim=1.0. Y is the long axis (cradle depth).
    The tray sits at +Y (user-front) end. Camera is in +Y, +X quadrant,
    elevated so the tray's low 10mm front wall + r=20 side fillet sweeps
    are clearly visible (not hidden behind the back wall).
    """
    bpy.ops.object.camera_add(location=(0.7, 1.05, 0.55))
    cam = bpy.context.active_object
    cam.data.lens = 50  # natural — close to human-eye perspective
    cam.data.sensor_width = 36

    # Aim at the tray center (it's the focal subject)
    target = mathutils.Vector(tray_center_norm)
    look_dir = target - mathutils.Vector(cam.location)
    cam.rotation_euler = look_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam


def configure_render(quality_key, out_path):
    quality = QUALITY_PRESETS[quality_key]
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = quality["res"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False

    engine = quality["engine"]
    if engine == "BLENDER_EEVEE_NEXT":
        try:
            scene.render.engine = "BLENDER_EEVEE_NEXT"
        except TypeError:
            scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = engine

    if scene.render.engine == "CYCLES":
        scene.cycles.samples = quality["samples"]
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.005 if quality_key == "hero" else 0.01
        configure_cycles_device(scene)
        if quality["denoiser"]:
            scene.cycles.use_denoising = True
            for cand in ("OPENIMAGEDENOISE", "OPTIX", "NLM"):
                try:
                    scene.cycles.denoiser = cand
                    print(f"[assembly-render] Denoiser: {cand}")
                    break
                except (TypeError, RuntimeError):
                    continue
        else:
            scene.cycles.use_denoising = False

    # AgX renders product colors more truthfully than Filmic (which desaturates).
    # Falls back to Standard if AgX isn't available (Blender < 4.0).
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
    print(f"[assembly-render] Quality: {args.quality}, out: {args.out}")

    reset_scene()

    # Import both parts at original mm scale
    cradle = import_stl(CRADLE_STL, "Cradle")
    tray = import_stl(TRAY_STL, "Tray")

    # Position tray relative to cradle (matches .combined-*.scad)
    tray.location = TRAY_OFFSET_MM

    # Materials
    # Lower SSS — at 0.05+ surfaces start reading as skin under direct light.
    # 0.015 keeps PLA's subtle translucency without the flesh tone.
    cradle_mat = make_pla_material("CradlePLA", CRADLE_RGB, roughness=0.62, sss=0.015)
    tray_mat = make_pla_material("TrayPLA", TRAY_RGB, roughness=0.55, sss=0.020)
    assign(cradle, cradle_mat)
    assign(tray, tray_mat)

    # Compute combined bbox (in mm) BEFORE normalizing
    bpy.context.view_layer.update()
    all_corners = []
    for obj in (cradle, tray):
        m = obj.matrix_world
        for v in obj.bound_box:
            all_corners.append(m @ mathutils.Vector(v))
    minc = mathutils.Vector((min(c.x for c in all_corners), min(c.y for c in all_corners), min(c.z for c in all_corners)))
    maxc = mathutils.Vector((max(c.x for c in all_corners), max(c.y for c in all_corners), max(c.z for c in all_corners)))
    size = maxc - minc
    center = (minc + maxc) * 0.5
    max_dim = max(size)
    print(f"[assembly-render] Combined bbox {size.x:.1f} x {size.y:.1f} x {size.z:.1f} mm, max={max_dim:.1f}")

    # Group both into an Empty so we can move the whole assembly
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=center)
    pivot = bpy.context.active_object
    pivot.name = "AssemblyPivot"
    cradle.parent = pivot
    tray.parent = pivot
    cradle.matrix_parent_inverse = pivot.matrix_world.inverted()
    tray.matrix_parent_inverse = pivot.matrix_world.inverted()

    # Move pivot so assembly bottom sits on z=0, centered XY at origin
    pivot.location = (0, 0, size.z / 2)

    # Now scale the pivot so max_dim = 1.0 in world units
    norm = 1.0 / max_dim
    pivot.scale = (norm, norm, norm)
    pivot.location = (0, 0, (size.z / 2) * norm)
    bpy.context.view_layer.update()

    # Tray center in normalized world coords (for camera target)
    # Tray bbox center mm = (55, 207.45, 19). Re-centered = (0, 80, 19). Normalized = ×norm.
    tray_center_norm = (0.0, 80.0 * norm, 19.0 * norm)

    setup_world()
    setup_backdrop()
    setup_lights(1.0)
    setup_camera(tray_center_norm=tray_center_norm)

    configure_render(args.quality, args.out)
    bpy.ops.render.render(write_still=True)
    print(f"[assembly-render] PNG -> {args.out}")


if __name__ == "__main__":
    main()
