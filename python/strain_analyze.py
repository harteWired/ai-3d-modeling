#!/usr/bin/env python3
"""Strain analyzer — closed-form beam-theory stress + safety factor.

Reads a design's spec.json `loadCase` block + materials.json and computes,
for each declared critical section:

  - Bending moment at the section from applied forces (M = F × r)
  - Section properties (I, c) for the declared cross-section shape
  - Bending stress σ = M·c / I
  - Allowable stress = yield × interlayer_derate (if stress crosses layers)
  - Safety factor = allowable / σ
  - Tip deflection from cantilever beam theory (δ = F·L³ / 3·E·I)
  - FEA recommendation flag (margin tight, or shape not in closed-form set)

Usage:
  python3 strain_analyze.py <design-dir> [--output report.json]

Expects:
  <design-dir>/spec.json — declares requiresStrainAnalysis + loadCase
  scad-lib/materials.json (resolved relative to repo root)

The loadCase schema (see also scad-lib/materials.json for material IDs):

  "loadCase": {
    "description": "...",
    "material": "PLA-CF",                // ID into materials.json
    "minSafetyFactor": 2.0,              // default 2.0
    "forces": [
      {
        "magnitude_N": 13.3,
        "direction": [0, 0, -1],         // unit vector, design-coord
        "applicationPoint_mm": [x, y, z], // design-coord
        "comment": "..."
      }
    ],
    "criticalSections": [
      {
        "name": "plug-root",
        "location_mm": [0, 0, 0],
        "shape": "hollow_rect" | "solid_rect" | "hollow_circle" | "solid_circle",
        // hollow_rect / solid_rect:
        "width_mm": 68.5,      // dimension perpendicular to bending load
        "height_mm": 42.5,     // dimension parallel to bending load (h in bh^3/12)
        "wall_thickness_mm": 3.0,   // hollow only
        // hollow_circle / solid_circle:
        "diameter_mm": 50,
        "inner_diameter_mm": 44,    // hollow only
        // length from this section to the load (for deflection calc, optional)
        "cantilever_length_mm": 98,
        // does bending stress at this section cross layer interfaces?
        "layerOrientation": "interlayer" | "in-plane",
        "comment": "..."
      }
    ]
  }
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def section_properties(section: dict) -> dict:
    """Compute area moment of inertia I and extreme-fiber distance c for the cross-section.

    Returns dict with keys: I_mm4, c_mm, area_mm2, shape_label.
    Bending axis is implicit: bending about the axis perpendicular to the load direction,
    in the cross-section plane. For rectangles, `height_mm` is the dimension parallel to
    the load (the one cubed in bh³/12).
    """
    shape = section["shape"]

    if shape == "solid_rect":
        b = section["width_mm"]
        h = section["height_mm"]
        I = (b * h ** 3) / 12.0
        c = h / 2.0
        area = b * h
        label = f"solid rectangle {b:.1f} × {h:.1f} mm"
    elif shape == "hollow_rect":
        b = section["width_mm"]
        h = section["height_mm"]
        t = section["wall_thickness_mm"]
        if 2 * t >= min(b, h):
            raise ValueError(f"Wall thickness {t} mm too large for {b}×{h} section")
        b_i = b - 2 * t
        h_i = h - 2 * t
        I = (b * h ** 3 - b_i * h_i ** 3) / 12.0
        c = h / 2.0
        area = b * h - b_i * h_i
        label = f"hollow rectangle {b:.1f} × {h:.1f} mm (wall {t:.1f} mm)"
    elif shape == "solid_circle":
        d = section["diameter_mm"]
        I = math.pi * d ** 4 / 64.0
        c = d / 2.0
        area = math.pi * d ** 2 / 4.0
        label = f"solid circle Ø{d:.1f} mm"
    elif shape == "hollow_circle":
        d_o = section["diameter_mm"]
        d_i = section["inner_diameter_mm"]
        if d_i >= d_o:
            raise ValueError(f"Inner diameter {d_i} >= outer {d_o}")
        I = math.pi * (d_o ** 4 - d_i ** 4) / 64.0
        c = d_o / 2.0
        area = math.pi * (d_o ** 2 - d_i ** 2) / 4.0
        label = f"hollow circle Ø{d_o:.1f} / Ø{d_i:.1f} mm"
    else:
        raise ValueError(f"Unsupported cross-section shape: {shape!r}")

    return {"I_mm4": I, "c_mm": c, "area_mm2": area, "shape_label": label}


def moment_at_section(forces: list[dict], section_location: list[float]) -> dict:
    """Resolve applied forces into a bending moment magnitude at the given section.

    For v1 we treat the section as a rigid point and compute |M| = Σ |F × r|
    using the cross product (F_vec, r_vec). r_vec = application_point − section_location.

    Returns dict with total_moment_Nmm + per-force contributions.
    """
    sx, sy, sz = section_location
    total_mx = total_my = total_mz = 0.0
    contributions = []
    for f in forces:
        F = f["magnitude_N"]
        dx, dy, dz = f["direction"]
        # normalize direction
        dmag = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dmag == 0:
            raise ValueError(f"Zero-magnitude direction vector in force: {f}")
        dx, dy, dz = dx / dmag, dy / dmag, dz / dmag
        Fx, Fy, Fz = F * dx, F * dy, F * dz
        ax, ay, az = f["applicationPoint_mm"]
        rx, ry, rz = ax - sx, ay - sy, az - sz
        # M = r × F
        mx = ry * Fz - rz * Fy
        my = rz * Fx - rx * Fz
        mz = rx * Fy - ry * Fx
        total_mx += mx
        total_my += my
        total_mz += mz
        contributions.append({
            "force_N": F,
            "lever_arm_mm": math.sqrt(rx * rx + ry * ry + rz * rz),
            "moment_components_Nmm": [mx, my, mz],
            "moment_magnitude_Nmm": math.sqrt(mx * mx + my * my + mz * mz),
        })
    total = math.sqrt(total_mx ** 2 + total_my ** 2 + total_mz ** 2)
    return {
        "total_moment_Nmm": total,
        "moment_vector_Nmm": [total_mx, total_my, total_mz],
        "contributions": contributions,
    }


def analyze_section(section: dict, forces: list[dict], material: dict, min_sf: float) -> dict:
    """Compute stress and safety factor at one critical section."""
    props = section_properties(section)
    moment = moment_at_section(forces, section["location_mm"])
    M = moment["total_moment_Nmm"]
    I = props["I_mm4"]
    c = props["c_mm"]
    sigma_MPa = M * c / I if I > 0 else float("inf")  # N·mm × mm / mm⁴ = N/mm² = MPa

    layer = section.get("layerOrientation", "in-plane")
    if layer == "interlayer":
        derate = material["interlayer_derate"]
        sigma_allow = material["yield_MPa"] * derate
        derate_label = f"yield × interlayer_derate ({derate})"
    elif layer == "in-plane":
        sigma_allow = material["yield_MPa"]
        derate_label = "in-plane yield (no derate)"
    else:
        raise ValueError(f"Unknown layerOrientation: {layer!r}")

    safety_factor = sigma_allow / sigma_MPa if sigma_MPa > 0 else float("inf")

    # Deflection at load point (cantilever beam, single point load at tip).
    # δ = F·L³ / (3·E·I). Use resultant force magnitude and the longest lever arm
    # as conservative L; works as a sanity check, not a precision number.
    L = section.get("cantilever_length_mm")
    deflection_mm = None
    if L is not None and forces:
        F_total = sum(f["magnitude_N"] for f in forces)
        E = material["youngs_modulus_MPa"]  # MPa = N/mm²
        deflection_mm = F_total * L ** 3 / (3.0 * E * I)

    fea_recommended = False
    fea_reasons = []
    if safety_factor < 3.0:
        fea_recommended = True
        fea_reasons.append(f"safety factor {safety_factor:.1f} < 3.0 — closed-form is conservative; FEA may recover margin")
    if section["shape"] not in ("solid_rect", "hollow_rect", "solid_circle", "hollow_circle"):
        fea_recommended = True
        fea_reasons.append(f"shape {section['shape']!r} not modeled by closed-form")

    return {
        "name": section["name"],
        "location_mm": section["location_mm"],
        "shape_label": props["shape_label"],
        "I_mm4": props["I_mm4"],
        "c_mm": props["c_mm"],
        "area_mm2": props["area_mm2"],
        "moment_Nmm": M,
        "moment_vector_Nmm": moment["moment_vector_Nmm"],
        "moment_breakdown": moment["contributions"],
        "sigma_MPa": sigma_MPa,
        "sigma_allow_MPa": sigma_allow,
        "allowable_basis": derate_label,
        "layer_orientation": layer,
        "safety_factor": safety_factor,
        "min_safety_factor": min_sf,
        "pass": safety_factor >= min_sf,
        "cantilever_length_mm": L,
        "deflection_mm": deflection_mm,
        "fea_recommended": fea_recommended,
        "fea_reasons": fea_reasons,
        "comment": section.get("comment", ""),
    }


def load_materials(repo_root: Path) -> dict:
    path = repo_root / "scad-lib" / "materials.json"
    with open(path) as f:
        return json.load(f)


def find_repo_root(start: Path) -> Path:
    """Walk up from start until we find a directory with scad-lib/materials.json."""
    p = start.resolve()
    for candidate in [p, *p.parents]:
        if (candidate / "scad-lib" / "materials.json").exists():
            return candidate
    raise FileNotFoundError(f"Could not locate scad-lib/materials.json from {start}")


def analyze_design(design_dir: Path) -> dict:
    spec_path = design_dir / "spec.json"
    with open(spec_path) as f:
        spec = json.load(f)

    if not spec.get("requiresStrainAnalysis"):
        return {
            "skipped": True,
            "reason": "spec.json has no requiresStrainAnalysis: true",
        }

    load_case = spec.get("loadCase")
    if not load_case:
        raise ValueError("requiresStrainAnalysis: true but spec.json has no loadCase block")

    repo_root = find_repo_root(design_dir)
    materials_db = load_materials(repo_root)["materials"]

    material_id = load_case.get("material")
    if material_id not in materials_db:
        raise ValueError(
            f"Unknown material {material_id!r}; available: {sorted(materials_db.keys())}"
        )
    material = dict(materials_db[material_id])
    # Apply per-design overrides if present.
    override = load_case.get("materialOverride", {})
    material.update(override)
    material["_id"] = material_id

    min_sf = float(load_case.get("minSafetyFactor", 2.0))
    forces = load_case["forces"]
    sections = load_case["criticalSections"]
    if not forces:
        raise ValueError("loadCase.forces is empty")
    if not sections:
        raise ValueError("loadCase.criticalSections is empty")

    section_reports = [analyze_section(s, forces, material, min_sf) for s in sections]
    overall_pass = all(r["pass"] for r in section_reports)
    worst = min(section_reports, key=lambda r: r["safety_factor"])

    return {
        "skipped": False,
        "design_name": spec.get("name"),
        "design_version": spec.get("version"),
        "description": load_case.get("description", ""),
        "material": material,
        "min_safety_factor": min_sf,
        "forces": forces,
        "sections": section_reports,
        "overall_pass": overall_pass,
        "worst_section": worst["name"],
        "worst_safety_factor": worst["safety_factor"],
        "fea_recommended": any(r["fea_recommended"] for r in section_reports),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("design_dir", help="designs/<name>")
    parser.add_argument("--output", help="Write JSON report to this path (else stdout)")
    args = parser.parse_args()

    design_dir = Path(args.design_dir)
    if not design_dir.is_dir():
        print(f"Not a directory: {design_dir}", file=sys.stderr)
        sys.exit(2)

    try:
        report = analyze_design(design_dir)
    except (ValueError, FileNotFoundError, KeyError) as e:
        print(f"strain_analyze: {e}", file=sys.stderr)
        sys.exit(1)

    out = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
