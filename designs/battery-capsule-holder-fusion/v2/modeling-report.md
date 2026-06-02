# Battery Capsule Holder (Fusion) — v2 "Zig-Zag Caterpillar"

**Backend:** Fusion 360 (MCP) · **Status:** built + validated · **Date:** 2026-06-02

## What this is

A **refinement iteration** of the Fusion v1 (the one-shot filleted slab). Per user
direction: "a cooler base shape, more novel nesting of the capsules with tighter packing
density, and a zig-zag caterpillar shape." Still **clean-room w.r.t. the OpenSCAD build**
— the modeling agent only ever iterated on its own v1, never the OpenSCAD solution.

## Design

- **Zig-zag caterpillar chain.** The 6 teardrop sockets march along X while alternating
  ±10 mm in Y — a meandering spine. Each teardrop points nose-to-tail at the next socket,
  so consecutive capsules nest (the point of one tucks beside the fat lobe of the next).
  This interlock is the caterpillar crawl and is what allows the tight packing.
- **Pitch/amplitude tuned by a wall optimizer.** A boundary-distance sampler scanned
  pitch × amplitude; **PITCH = 22.3 mm, Y_AMP = 10 mm** lands a **~42° zig-zag spine** at
  a thinnest inter-socket wall of **~1.45 mm** (≥ 1.2 mm floor). The zig-zag also makes the
  part *more compact* than v1 (169 mm long vs the 206 mm a straight chain needs).
- **Single caterpillar body.** All fat lobes (R 17.5 mm) + a zig-zag spine backstop are
  drawn in one sketch and the entire unioned profile set is extruded once → one watertight
  body with a scalloped, segmented silhouette. Rounded **head** lobe (R 20.5 mm) with two
  **eye dimples** + two **antenna nubs**; tapered **tail** lobe (R 10.5 mm).
- **Pockets.** Teardrop 28.5 × 24.4 mm (capsule 27.8 × 23.7 + 0.35 mm/side), 18 mm deep,
  3 mm solid floor, vertical walls, open top, 1 mm × 45° lead-in chamfer. Either end up.
- **Base.** Flat bottom for bed adhesion / non-slip; prints flat sockets-up, support-free.

## Validation (mesh, trimesh)

| Check | Result |
|-------|--------|
| Bounding box | 169.1 × 61.5 × 24.5 mm (z incl. 3.5 mm antenna nubs) |
| Watertight | true |
| Volume | 77.7 cm³ |
| Pockets | 6 / 6, each floor z = 3.00 → **18.00 mm deep** (ray-cast verified) |
| Min inter-socket wall | ~1.45 mm (≥ 1.2 floor), sampler-tuned |
| Body count | 1 |
| Print | flat, sockets up, vertical walls, support-free |

## vs v1 (Fusion one-shot baseline)

| | v1 (slab) | v2 (caterpillar) |
|---|---|---|
| Silhouette | rounded-rectangle slab | segmented zig-zag caterpillar (head + tail) |
| Layout | 2 cols + offset middle col | single zig-zag chain, nose-to-tail nested |
| Min wall | 2.0 mm | ~1.45 mm (tighter) |
| Footprint | 80.4 × 73.9 mm | 169.1 × 61.5 mm |
| Volume | 68.2 cm³ | 77.7 cm³ |
| Character | utilitarian | a creature (eyes + antennae) |

## Build notes (honest provenance)

The agent that authored v2 has no live Fusion access (subagent-MCP gap), so it iterated
blind; the main session ran every revision live and fed back real results. Two fixes were
applied at the executor level (pure Fusion-API mechanics, no geometry change): reverting a
crashing `sketchControlPointSplines.add()` to the working `sketchFittedSplines`, and
extruding **all** sketch profiles (not just the largest) so the body spans the whole chain
rather than a single sub-lobe. The zig-zag amplitude (Y_AMP/PITCH) was tuned by the
in-repo wall-distance optimizer to satisfy the user's "zig-zag" ask at ≥ 1.2 mm walls.

## Files

- `output/battery-capsule-holder-fusion-v2.stl` — print-ready mesh (watertight)
- `build.py` — reproducible Fusion `execute_code` build script
