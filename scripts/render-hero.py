"""Hero render of an STL via headless Blender.

Invoked by the bin/render-hero.js harness — not directly. The harness picks the
Blender binary (prefers /home/node/blender/blender static build with OIDN) and
passes args after `--`.

Args (after `--`):
    --stl PATH              STL to render (required)
    --out PATH              Output PNG path (required)
    --preset PATH           Python file exposing setup(scene, subject, args)
                            (default: scad-lib/blender-presets/studio.py)
    --quality {draft,standard,hero}
                            Tier mapping samples + engine + denoiser
    --samples N             Override sample count
    --resolution WxH        Override resolution
    --engine {CYCLES,BLENDER_EEVEE,BLENDER_EEVEE_NEXT}
    --angle NAME            Camera-angle preset name (e.g. iso, front,
                            front-threequarter, top-threequarter, back)
    --glb PATH              Also export glTF binary to this path
"""

# ⛔ DOES NOT RUN ON THIS HOST (measured 2026-09-06). Blender is NOT installed on this host —
# not on PATH, no binary found. The /home/node/blender paths below are Jinn-container remnants.
# Deliberately NOT repointed: aiming them at a Blender that does not exist converts a loud
# ENOENT into a confusing one, and nothing here could be proved without the binary.
# To revive: install Blender, invoke as `blender --background --python <this script>`.


import argparse
import importlib.util
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _render_device import configure_cycles_device  # noqa: E402

QUALITY_PRESETS = {
    # Quick iteration — Eevee, low samples, no denoiser
    "draft": {
        "engine": "BLENDER_EEVEE_NEXT",
        "samples": 64,
        "resolution": "1280x960",
        "use_denoiser": False,
    },
    # Default for in-pipeline ship renders — Cycles + denoiser, balanced
    "standard": {
        "engine": "CYCLES",
        "samples": 128,
        "resolution": "1920x1440",
        "use_denoiser": True,
    },
    # README/docs hero renders — high samples, denoiser, big res
    "hero": {
        "engine": "CYCLES",
        "samples": 512,
        "resolution": "2560x1920",
        "use_denoiser": True,
    },
}


def parse_args():
    """Parse args after the `--` separator that Blender passes through."""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser(description="Hero render an STL via Blender")
    p.add_argument("--stl", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--preset", default=None)
    p.add_argument("--quality", choices=list(QUALITY_PRESETS.keys()), default="standard")
    p.add_argument("--samples", type=int, default=None)
    p.add_argument("--resolution", default=None)
    p.add_argument("--engine", default=None)
    p.add_argument("--angle", default="threequarter")
    p.add_argument("--glb", default=None)
    return p.parse_args(argv)


def resolve_quality(args):
    """Merge quality preset defaults with explicit overrides."""
    base = dict(QUALITY_PRESETS[args.quality])
    if args.engine:
        base["engine"] = args.engine
    if args.samples is not None:
        base["samples"] = args.samples
    if args.resolution:
        base["resolution"] = args.resolution
    return base


def reset_scene():
    """Wipe the default scene clean."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in [bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.objects]:
        for item in list(collection):
            collection.remove(item)


def import_stl(path):
    """Import STL, normalize to max-dim=1.0, sit on z=0, centered on origin.

    STL imports as raw values (a 100mm part = 100 Blender units = 100m subject).
    Normalizing puts the part at consistent meter-scale so preset lighting and
    camera distances work the same regardless of true subject size.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"STL not found: {path}")
    # Blender 4.x changed the STL importer namespace
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=path)
    else:
        bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.selected_objects[0]
    obj.name = "Subject"

    # 1. Origin to bbox center, then move object to world origin.
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (0, 0, 0)

    # 2. Normalize: max bbox dimension = 1.0 unit.
    raw_max = max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    raw_dims = tuple(obj.dimensions)
    if raw_max > 0:
        norm = 1.0 / raw_max
        obj.scale = (norm, norm, norm)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 3. Lift so the bottom of the bbox sits on z=0.
    obj.location.z = obj.dimensions.z / 2

    # Stash the original dimensions so the preset can adapt to subject shape.
    obj["raw_dims_mm"] = raw_dims
    obj["max_dim_mm"] = raw_max
    return obj


def load_preset(path):
    """Load a Python preset module by path. Must expose setup(scene, subject, args)."""
    spec = importlib.util.spec_from_file_location("hero_preset", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load preset: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "setup"):
        raise AttributeError(f"Preset {path} must define setup(scene, subject, args)")
    return mod


def configure_render(scene, quality, args):
    """Common render settings — engine, samples, denoiser, resolution, color mgmt."""
    width, _, height = quality["resolution"].partition("x")
    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False

    engine = quality["engine"]
    # Blender 4.2 uses BLENDER_EEVEE_NEXT; older versions use BLENDER_EEVEE
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
        scene.cycles.adaptive_threshold = 0.005 if args.quality == "hero" else 0.01
        configure_cycles_device(scene)
        if quality["use_denoiser"]:
            scene.cycles.use_denoising = True
            for candidate in ("OPENIMAGEDENOISE", "OPTIX", "NLM"):
                try:
                    scene.cycles.denoiser = candidate
                    print(f"[render-hero] Denoiser: {candidate}")
                    break
                except (TypeError, RuntimeError):
                    continue
            else:
                scene.cycles.use_denoising = False
                print("[render-hero] No denoiser available — disabling")
        else:
            scene.cycles.use_denoising = False
    else:
        scene.eevee.taa_render_samples = max(64, quality["samples"])

    # Filmic color mgmt — natural product-photography look
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium Contrast"


def export_glb(out_path, subject):
    """Export the subject (with its materials) as glTF binary for web embedding.

    Excludes scene lights/cameras — they're for rendering only. The viewer
    embeds its own lighting environment.
    """
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    # Select only the subject; export with use_selection=True
    bpy.ops.object.select_all(action="DESELECT")
    subject.select_set(True)
    bpy.context.view_layer.objects.active = subject
    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(out_path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_lights=False,
        export_cameras=False,
    )
    print(f"[render-hero] GLB -> {out_path}")


def main():
    args = parse_args()
    quality = resolve_quality(args)
    preset_path = args.preset or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "scad-lib",
        "blender-presets",
        "studio.py",
    )
    preset_path = os.path.abspath(preset_path)

    print(f"[render-hero] STL: {args.stl}")
    print(f"[render-hero] Out: {args.out}")
    print(f"[render-hero] Preset: {preset_path}")
    print(f"[render-hero] Quality: {args.quality} -> engine={quality['engine']}, "
          f"samples={quality['samples']}, res={quality['resolution']}, "
          f"denoiser={quality['use_denoiser']}")
    print(f"[render-hero] Angle: {args.angle}")

    reset_scene()
    subject = import_stl(args.stl)
    print(f"[render-hero] Imported {len(subject.data.vertices)} verts, "
          f"original bbox {subject['raw_dims_mm'][0]:.1f} x {subject['raw_dims_mm'][1]:.1f} x "
          f"{subject['raw_dims_mm'][2]:.1f} mm (normalized to max-dim=1.0)")

    preset = load_preset(preset_path)
    scene = bpy.context.scene
    preset.setup(scene, subject, vars(args))

    configure_render(scene, quality, args)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    scene.render.filepath = os.path.abspath(args.out)
    bpy.ops.render.render(write_still=True)
    print(f"[render-hero] PNG -> {args.out}")

    if args.glb:
        export_glb(args.glb, subject)


if __name__ == "__main__":
    main()
