# Battery Capsule Holder — Fusion Alternate

An **alternate design** for the same brief as the [OpenSCAD Battery Capsule Holder](battery-capsule-holder.md): a drawer rack that holds **6 battery capsules** upright, beaker-rack style, gripping the lower body of each asymmetric teardrop capsule in a blind socket so they stand vertical and drop in either end up.

> **Backend:** Fusion 360 (MCP). This build is a **clean-room independent redesign** — the agent that made every geometry decision was deliberately walled off from the OpenSCAD solution (it never saw the `.scad`, `spec.json`, or v1 renders) and worked only from the problem statement: calipered capsule dims, capacity, fit type, and drawer context. The two designs are meant to be compared side-by-side.

## Renders

![Top-three-quarter hero — a soft-filleted rounded-rectangle slab with six deep teardrop sockets in a staggered interlocked layout, alternate pockets flipped 180° so their pointed ends nest into the wedge gaps beside neighbouring fat ends](images/battery-capsule-holder/battery-capsule-holder-fusion-hero.png)
*Hero — six deep teardrop sockets (18 mm) with vertical walls and 45° lead-in chamfers, in a 3 mm-filleted slab; alternate pockets flipped 180° to interlock*

![Top-down — the six teardrop openings in a staggered brick: two outer columns of two plus an offset middle column of two flipped the other way](images/battery-capsule-holder/battery-capsule-holder-fusion-top.png)
*Top-down — staggered-brick layout: two outer columns + an offset, flipped middle column*

![Front-three-quarter — the 21 mm slab with softly filleted vertical and top edges and the recessed sockets](images/battery-capsule-holder/battery-capsule-holder-fusion-front.png)
*Front three-quarter — 21 mm slab, filleted edges, recessed teardrop sockets*

## Design Overview

The same calipered capsule (**27.8 × 23.7 mm** teardrop, **69 mm** tall) and the same functional rules (outer-grip only, never the bore; 18 mm blind socket; loose drop-in either end up; non-slip drawer base) — but a different form language. Where the OpenSCAD build leans organic (a curved superellipse dune-hull that tapers inward), this build leans **geometric and tidy**: a single low rounded-rectangle slab with soft-filleted edges that reads as one clean drawer tile.

```
       rounded-rectangle slab footprint (80.4 × 73.9 mm)
     ╭───────────────────────────────────────╮
     │   ◖      ◗      ◖     staggered brick  │   each socket 28.5 × 24.4 mm
     │       ◗      ◖      ◗  middle col 180° │   (0.35 mm/side loose drop-in)
     ╰───────────────────────────────────────╯
        3 mm filleted edges     1.0 × 45° rim lead-ins
        4 ⌀15 rubber-pad recesses underneath
```

## Geometry

| Dimension | Value | Notes |
|-----------|-------|-------|
| Bounding box | 80.4 × 73.9 × 21.0 mm | rounded-rect slab, 3 mm edge fillets |
| Capacity | 6 capsules | staggered brick (2 outer cols + offset middle col) |
| Socket profile | 28.5 × 24.4 mm | capsule 27.8 × 23.7 + 0.35 mm/side |
| Socket depth | 18.0 mm | blind; floor at z = 3.0 mm (ray-cast verified) |
| Thinnest inter-socket wall | 2.0 mm | ≥ 1.2 mm floor; verified over all 15 pocket pairs |
| Outer margin | 4.0 mm | wall around the socket cluster |
| Rim lead-in | 1.0 mm × 45° chamfer | each of 6 sockets |
| Edge fillet | 3.0 mm | vertical + top edges (bottom left sharp for flat print) |
| Floor | 3.0 mm | solid; nothing enters the capsule bore |
| Volume | 68.2 cm³ | watertight / manifold |

## Printability

Single orientation, sockets up, no supports. Pocket walls are vertical; the only
overhang features are the 45°-capped rim chamfers. Bottom edge is left sharp (no
bottom fillet) for a clean first layer.

| Check | Result | Notes |
|-------|--------|-------|
| Overhangs | PASS | vertical socket walls; chamfers ≤ 45° |
| Bridges | PASS | none — blind sockets, solid floor |
| Thin walls | PASS | thinnest inter-socket wall 2.0 mm (≥ 1.2) |
| Watertight | PASS | manifold, 6,348 triangles |

## vs the OpenSCAD build

| | [OpenSCAD v1](battery-capsule-holder.md) | Fusion (this page) |
|---|---|---|
| Outer body | superellipse n = 2.6 dune-hull, tapers inward | rounded-rect slab, 3 mm edge fillets |
| Footprint | 89 × 68 mm | 80.4 × 73.9 mm |
| Layout | nested 3 × 2 | 2 outer cols + offset middle col |
| Pocket depth / floor | 18 / 3 mm | 18 / 3 mm |
| Clearance | 0.35 mm/side | 0.35 mm/side *(converged)* |
| Min wall | 2.0 mm | 2.0 mm *(converged)* |
| Non-slip | 4× ⌀10 × 1 mm recesses | 4× ⌀15 × 1.2 mm pad recesses |
| Lead-in | 1.5 mm chamfer | 1.0 mm chamfer + 3 mm outer fillet |
| Volume | 46.4 cm³ | 68.2 cm³ (~47% heavier) |

Both converged independently on the fit-critical numbers (0.35 mm clearance, 2.0 mm
min wall); they diverge most on outer form and material efficiency — the dune-hull
tapers away ~22 cm³ that the slab keeps.

## Downloads

| File | Description |
|------|-------------|
| [`battery-capsule-holder-fusion.stl`](../designs/battery-capsule-holder/output/fusion/battery-capsule-holder-fusion.stl) | Print-ready mesh (watertight) |
| [`modeling-report.md`](../designs/battery-capsule-holder/output/fusion/modeling-report.md) | Clean-room rationale + validation |
| [`MEASUREMENTS.md`](../designs/battery-capsule-holder/MEASUREMENTS.md) | Caliper data (shared with v1) |

Built with the Fusion 360 MCP backend (clean-room dispatch).
