# Battery Capsule Holder — Fusion 360 Clean-Room Build

**Backend:** Fusion 360 (MCP) · **Status:** built + validated · **Date:** 2026-06-02

## What this is

A **clean-room independent redesign** of the same brief as the OpenSCAD v1 holder,
built to compare two design approaches to one problem. The design decisions here were
made by an isolated agent that was **walled off from the OpenSCAD solution** — it never
saw `spec.json`, `battery-capsule-holder.scad`, or the v1 renders. It worked only from
the problem statement (calipered capsule dims, capacity, fit type, drawer context).

Every geometry decision — outer body form, socket layout, clearance, wall/floor
thicknesses, base treatment, chamfers — was reasoned from scratch. The main session
acted only as a "dumb pipe" executing the agent's Fusion script; the one human-side
intervention was a pure API-method fix (`ExtrudeFeatureInput.create` →
`extrudes.createInput`) that touched no geometry.

## Independent design decisions

- **Outer body:** a single low **rounded-rectangle slab** (80.4 × 73.9 × 21 mm) with
  3 mm fillets on the vertical and top edges — reads as one clean drawer tile, no tall
  thin walls. (The OpenSCAD build chose an organic superellipse dune-hull instead.)
- **6-pocket layout:** symmetric staggered brick — two outer columns of two pockets
  (apex +Y) and a middle column of two flipped 180° (apex −Y) shifted so the pointed
  ends nest into the wedge gaps beside the outer columns' fat ends. The requested
  teardrop interlock.
- **Teardrop pocket:** fat rounded end r = 11.85 mm (= narrow/2) blended to a point
  15.95 mm away → the 27.8 × 23.7 mm capsule section, offset +0.35 mm per side.
- **Clearance:** 0.35 mm/side (loose drop-in, gravity retention, either end up).
- **Walls / floor:** thinnest inter-socket wall **2.0 mm** (verified by dense
  point-to-point distance over all 15 pocket pairs), outer margin 4.0 mm, solid floor
  3.0 mm (nothing enters the capsule bore).
- **Non-slip base:** four ⌀15 × 1.2 mm recessed pockets near the corners for standard
  self-adhesive rubber bumper pads.
- **Lead-in:** 1.0 mm × 45° chamfer at each pocket mouth for one-handed drop-in.

## Validation (mesh, trimesh)

| Check | Result |
|-------|--------|
| Bounding box | 80.4 × 73.9 × 21.0 mm |
| Watertight | true |
| Volume | 68.16 cm³ |
| Pockets | 6 / 6, each floor at z = 3.00 → **18.00 mm deep** (ray-cast verified) |
| Min inter-socket wall | 2.0 mm (≥ 1.2 mm floor) |
| Print orientation | flat, sockets up, vertical walls, support-free |

## vs OpenSCAD v1 (independent comparison)

| | OpenSCAD v1 | Fusion (clean-room) |
|---|---|---|
| Outer body | superellipse n = 2.6 dune-hull, tapers inward | rounded-rect slab, 3 mm edge fillets |
| Footprint | 89 × 68 mm | 80.4 × 73.9 mm |
| Layout | nested 3 × 2 | 2 outer cols + offset middle col |
| Pocket depth / floor | 18 / 3 mm | 18 / 3 mm |
| Clearance | 0.35 mm/side | 0.35 mm/side *(converged)* |
| Min wall | 2.0 mm | 2.0 mm *(converged)* |
| Non-slip | 4× ⌀10 × 1 mm | 4× ⌀15 × 1.2 mm pad recesses |
| Lead-in | 1.5 mm chamfer | 1.0 mm chamfer + 3 mm outer fillet |
| Volume | 46.4 cm³ | 68.2 cm³ (~47% heavier) |

**Takeaways:** the two builds diverged most on *outer form* (organic taper vs filleted
slab) and *material efficiency* (the dune-hull tapers away ~22 cm³ the slab keeps), yet
**converged independently** on the fit-critical numbers — 0.35 mm clearance and 2.0 mm
min wall — a good signal both reads of the FDM constraints were sound.

## Files (in this design folder)

- `output/battery-capsule-holder-fusion.stl` — print-ready mesh (6,348 tris, watertight)
- `build.py` — the clean-room Fusion `execute_code` build script (reproducible)
- `MEASUREMENTS.md` — calipered ground truth (shared with the OpenSCAD build)
- proofs published at `docs/images/battery-capsule-holder/battery-capsule-holder-fusion-{hero,top,front}.png`
