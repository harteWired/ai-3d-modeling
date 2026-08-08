---
date: 2026-06-20
project: 3d-printing
type: session-log
---

# 2026-06-20 — Mailbox Stand-off Grate: finish, redesign to cross-hatch mesh, ship + print tweaks

## Quick Reference
**Keywords:** mailbox-standoff-grate, drainage grate, dovetail jigsaw, cross-hatch mesh, lattice, two-color 3MF, hollow-outline letters, Arial Black glyph, shapely, trimesh, manifold3d, trimesh to_2D reproject bug, perforated field, color cap, feet through deck, bridge layer, Bambu Studio object overlap, Fusion MCP, PR #6, PR #7, build_perf_tiles.py, bundle_bicolor.py
**Project:** 3d-printing
**Outcome:** Finished the mid-build mailbox grate, reverse-engineered + rebuilt a lost generator, then redesigned the look twice on user feedback (hollow-outline letters → continuous 45° cross-hatch mesh + mostly-solid two-color letters) and shipped to main (PR #6). Then two print tweaks (PR #7): full-height feet through the deck (kills the bridge layer) and a thin 1mm letter color cap (single filament change). User is printing one.

## What Was Done
- Resumed a paused build (4 perforated jigsaw tiles, only M done). The generator script that made the approved M was never saved — reverse-engineered the field/footprint/glyph from existing STLs (tile-*.stl in assembly coords, glyphM.stl, print2c/*-letter.stl) and rebuilt a clean parametric generator `build_perf_tiles.py` that inherits the validated dovetail/leg footprint from the Fusion `tile-*.stl` (so jigsaw mating is preserved by construction) and only adds the field + letters + two-color split via shapely/trimesh+manifold.
- Generated solid H and K glyphs in Arial Black via Fusion MCP execute_code (export_stl to the Windows-mapped output path) → glyph-H.stl, glyph-K.stl (M reuses glyphM.stl).
- User feedback round 1: hollow-outline "negative" letters were too open / snag-prone. Redesigned to a **continuous 45° cross-hatch mesh** field (1.8mm ribs, ~46% open) + **mostly-solid two-color letters** with small Ø3.2mm drain holes. User: "That is SO much better. Commit, go live."
- Shipped PR #6 (merged to main): docs/mailbox-standoff-grate.md + 3 hero renders, README newest-first row, spec.json + requirements.md updated, cleaned iteration cruft from output/.
- User feedback round 2 (print tweaks) → PR #7 (merged): (1) feet now run full-height floor→through the deck, flush with the show face — printed letter-face-down they anchor on the bed coplanar with the deck, removing the elevated bridge layer; (2) letter 2nd color is only the top 1mm (~5 layers) cap, printed first against the bed = single filament change (cap ~5cc vs ~20cc solid).
- Answered slicer question: the base/cap "overlap" Bambu flags is ~10µm float noise on the coincident z=3 face (benign, expected for stacked two-color); documented the Assemble-into-one-object tip + filament-assignment caution. Pushed doc tip directly to main (1abec53).

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Inherit footprint/legs from solid tile-*.stl, only add field+letters | Preserves the interference-validated dovetail mating by construction; avoids re-deriving teeth |
| Continuous 45° cross-hatch mesh (not discrete turbine holes) | User wanted a consistent continuous mesh; carries the open-area/weight target so letters can stay solid |
| Mostly-solid letters + small drain holes (not hollow outline) | Hollow-outline center was snag-prone (mail could catch); solid reads clean and won't snag |
| Feet full-height through the deck, print letter-face-down | Foot ends anchor on bed coplanar with deck → no elevated bridge layer; feet print as supported towers |
| Letter color only top 1mm cap | Color only needs to show on the top face; one filament change, ~75% less 2nd-color volume |
| Ship via PR then merge to main (Pages live) | Matches the repo's PR-per-design pattern (#2–#7) |

## Key Learnings
- trimesh `Path3D.section(...).to_2D()` reprojects into an auto best-fit plane frame that translates/rotates **per file** — deck (from tile-M.stl) and glyph (from glyphM.stl) silently landed in different frames (631mm² overlap) and the render hid it. Fix: pass an explicit `to_2D=translation_matrix([0,0,-z])` so planar coords stay world XY.
- The `tile-*.stl` and `glyphM.stl` are in ASSEMBLY coords (e.g. tile-M x[-118.8,8]), not origin-centered — must recenter by the tile center when building.
- Don't read a glyph source from the same file the script writes (self-corruption: it read its own ring output as the glyph on the 2nd run). Use a write-safe glyph namespace (glyph-<L>.stl).
- trimesh STL is binary float32 → complex welds (ring into deck void) reload non-watertight; build the single-color tile as one cut (fp − field − inner) instead of welding two bodies.
- manifold union/difference rejects pre-concatenated multi-shell meshes ("Not all meshes are volumes"); pass a flat list of individual volume meshes, or subtract cutters from one solid.
- Fusion MCP `execute_code` DOES return the last expression value (REPL-style) — usable for reading back bbox/measurements, contrary to the older "geometry deltas only" note.
- Bambu flags any two touching objects as overlapping; for stacked two-color parts this is expected — Assemble into one object to silence it.

## Solutions & Fixes
- Reverse-engineered the lost perforation generator from artifact STLs; later replaced the whole field with the cross-hatch lattice.
- Coordinate-frame misalignment (to_2D reproject) → explicit transform + recenter by tile center; verified base∩letter ≈ 0 and assembly bbox back to exactly 237.6×339.2.
- Non-watertight single-color tile → rebuilt as one extrude-minus-cutters; all 4 reload watertight.
- Bridge layer on print → full-height feet through deck, print letter-face-down (feet anchor on bed).

## Files Modified
- `designs/mailbox-standoff-grate/build_perf_tiles.py`: NEW parametric generator (cross-hatch lattice field, Arial Black glyphs, mostly-solid letters w/ drain holes, full-height feet, top-1mm color cap, two-color split). Inherits footprint/legs from tile-*.stl.
- `designs/mailbox-standoff-grate/bundle_bicolor.py`: NEW — print-orients (letter-face-down) + bundles each tile's two-object -bicolor.3mf.
- `designs/mailbox-standoff-grate/output/`: tileperf-{M,H,H2,K}.stl, print2c/{M,H,H2,K}-{base,letter}.stl + -bicolor.3mf, assembly-perf*.stl, glyph-H/glyph-K.stl; removed iteration cruft.
- `designs/mailbox-standoff-grate/spec.json`, `requirements.md`: updated to as-built (cross-hatch mesh, two-color letters, feet through deck, color cap).
- `docs/mailbox-standoff-grate.md`: NEW design page (3 hero renders, geometry, two-color/print guidance, slicer-overlap note).
- `docs/images/mailbox-standoff-grate/`: hero, iso, tile renders.
- `README.md`: newest-first Designs row.
- `scripts/render-part.py`: (from prior session) --overlay-stl/--overlay-rgb + top angle.

## Follow-ups
- [ ] User is printing one tile — watch for fit/print feedback (recommend brim on outer frame, 2 filaments per 3MF, cap = letter color).
- [ ] build_perf_tiles.py depends on output/tile-*.stl + glyph*.stl staying in place for a clean rebuild (noted in vault next-action).
