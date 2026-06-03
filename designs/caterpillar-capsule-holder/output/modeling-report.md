# Caterpillar Capsule Holder — Modeling Report

**Backend:** Fusion 360 (MCP) · **Status:** built + validated · **Date:** 2026-06-02

## What this is

A drawer caddy that holds **6 battery capsules** upright, shaped as a **zig-zag
caterpillar**. The 6 teardrop sockets are strung into a single nose-to-tail nested
zig-zag chain; the body reads as a segmented caterpillar with a rounded head (two eye
dimples + two antenna nubs) and a tapered tail.

It grew out of the battery-capsule-holder studies (same calipered capsule, same fit
rules) but is its own model — a deliberately characterful take rather than a utility tile.

## Design

- **Zig-zag chain.** 6 sockets alternate ±10 mm in Y as they march along X (22.3 mm
  pitch → ~42° zig-zag spine). Each teardrop points nose-to-tail at the next socket, so
  consecutive capsules nest — the point of one tucks beside the fat lobe of the next.
- **Tight packing.** Pitch + amplitude were tuned by a boundary-distance optimizer to a
  thinnest inter-socket wall of **~1.45 mm** (≥ 1.2 mm FDM floor). The zig-zag also keeps
  the part compact (169 mm long vs the ~206 mm a straight chain of the same sockets needs).
- **Single segmented body.** All fat lobes (R 17.5 mm) + a zig-zag spine backstop are
  drawn in one sketch and the whole unioned profile set is extruded once → one watertight
  caterpillar body. Rounded **head** lobe (R 20.5 mm) with eyes + antenna nubs; tapered
  **tail** lobe (R 10.5 mm).
- **Pockets.** Teardrop 28.5 × 24.4 mm (capsule 27.8 × 23.7 + 0.35 mm/side clearance),
  18 mm deep, 3 mm solid floor (never touches the capsule bore), vertical walls, open top,
  1 mm × 45° lead-in chamfer. Capsules drop in either end up, gravity-retained.
- **Base.** Flat bottom for bed adhesion; prints flat sockets-up, support-free.

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

## Build provenance (honest)

Authored by a clean-room Fusion modeling agent that never saw the OpenSCAD capsule-holder
solution. That agent has no live Fusion access (subagent-MCP gap), so it wrote the
`execute_code` script and the main session ran every revision live, rendered, and fed real
results back. Two executor-level API fixes were applied (pure Fusion-API mechanics, no
geometry change): reverting a crashing `sketchControlPointSplines.add()` to the working
`sketchFittedSplines`, and extruding **all** sketch profiles (not just the largest) so the
body spans the whole chain. The zig-zag amplitude was tuned by the in-repo wall-distance
optimizer to satisfy the zig-zag intent at ≥ 1.2 mm walls.

## Files

- `output/caterpillar-capsule-holder.stl` — print-ready mesh (watertight)
- `build.py` — reproducible Fusion `execute_code` build script
- `MEASUREMENTS.md` — calipered capsule ground truth
