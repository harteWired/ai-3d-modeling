# Caterpillar 18650 Holder — Modeling Report

**Backend:** Fusion 360 (MCP) · **Status:** built + validated · **Date:** 2026-06-03

## What this is

A **derivative of the [Caterpillar Capsule Holder](../../caterpillar-capsule-holder/)**,
retargeted for **bare 18650 cells** (button-top). Same zig-zag caterpillar body and
character (segmented lobes, head with eyes + antenna nubs, tapered tail) — but the sockets
are round 18650 bores, and each socket floor has a **nipple indent** so cells can be
inserted **positive-side-down**.

## Design

- **6 round bores** Ø19.2 mm (cell ~18.4 mm + ~0.4 mm/side, loose drop-in), 18 mm deep,
  vertical walls, open top, 1 mm × 45° lead-in chamfer.
- **Zig-zag chain.** Bores alternate ±7 mm in Y at 15.25 mm pitch → ~42° zig-zag spine;
  thinnest inter-bore wall **~1.50 mm** (≥ 1.2 mm FDM floor). Re-proportioned from the
  capsule version for the smaller cell.
- **Nipple indent.** A central Ø7 mm × 1.8 mm-deep recess in each socket floor clears the
  positive button. Inserted positive-down, the cell body rests on the 18 mm floor ring
  (z = 3.0 mm) while the nub nestles into the recess (floor z = 1.2 mm); negative flat end
  faces up.
- **Single segmented body** (all body profiles extruded once); rounded head lobe with eye
  dimples + antenna nubs, tapered tail. Flat bottom; prints flat sockets-up, support-free.

## Validation (mesh, trimesh — ground truth)

| Check | Result |
|-------|--------|
| Bounding box | 119.5 × 45.9 × 24.5 mm (z incl. 3.5 mm antenna nubs) |
| Watertight | true |
| Body count | 1 |
| Volume | 36.95 cm³ |
| Bores | 6 / 6, Ø19.2 mm, **18.00 mm deep** (off-centre ray-cast floor z = 3.00) |
| Nipple indents | 6 / 6, **floor z = 1.20 mm** at each centre (1.8 mm recess) |
| Min inter-bore wall | ~1.50 mm (≥ 1.2 floor) |
| Print | flat, sockets up, vertical walls, support-free |

## Build notes

Built directly (not via the modeling subagent) as a parametric derivative of the capsule
caterpillar — teardrop pockets swapped for round bores + the floor nipple indent added.
One coordinate gotcha worth recording: sketching the bores/indents on **offset construction
planes** with absolute-Z points double-stacks the Z (features floated up to ~2× height);
the fix (and the convention in `build.py`) is to sketch every sub-feature on the **XY
plane** with the target Z baked into the point coordinates, exactly like the capsule build.
Verified with a trimesh ray-cast (center hit = indent floor 1.2 mm, off-center = bore floor
3.0 mm) rather than trusting the Fusion summary.

## Files

- `output/caterpillar-18650-holder.stl` — print-ready mesh (watertight)
- `build.py` — reproducible Fusion build script
- `MEASUREMENTS.md` — 18650 reference dims + user-confirmed fit choices
