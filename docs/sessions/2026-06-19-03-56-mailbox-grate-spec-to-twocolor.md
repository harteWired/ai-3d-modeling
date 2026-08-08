---
date: 2026-06-19
project: 3d-printing
type: session-log
---

# 2026-06-19 — Mailbox Standoff Grate: spec → 4-piece jigsaw → two-color hollow-letter

## Quick Reference
**Keywords:** mailbox-standoff-grate, drainage grate, Fusion 360 MCP, execute_code, subtractive plate, turbine holes, dovetail jigsaw, 2x2 assembly, U-channel groove, two-color, 3MF, hollow-outline letter, perforated field, trimesh boolean, shapely erode, M H H K, telegram plugin, leg setbacks
**Project:** 3d-printing
**Outcome:** Designed + built the mailbox drainage grate end-to-end in Fusion (live, via MCP execute_code). Iterated the top-surface art v1→v9, pivoted to a SUBTRACTIVE solid-plate-with-swirl-holes for robustness, added bold letters with a recessed U-channel outline, built the full 2x2 dovetail jigsaw (4 tiles M/H/H/K, validated 0 interference), passed print review, produced single- + two-color print files. Then per user: opened the field with a perforated grate + made each letter a hollow-outline ("negative") that stays legible, drains, and is ~64% lighter. ~30% lighter per tile. Locked the look; mid-build of the 4 final perforated tiles when session paused.

## What Was Done
- Spec + intake: mailbox leaks/pools water → raised drainage grate that floats mail on legs. Interior 349.25 x 247.65 mm, caulked corners, 1in front lip 1/4in off floor. Resolved all open questions; wrote requirements.md + spec.json; vault note.
- Conflict resolved: depth 349 > 256 bed AND door smaller than interior → forced **2x2 four-part jigsaw** (~119x170 mm tiles).
- Art iteration v1-v9 (live Fusion): spiral arms → mini-swirl field → kerf'd letter → SUBTRACTIVE solid plate with turbine-wedge holes (robust, full-width) → bold M + 1.5mm recessed U-channel outline groove (cut on top face via construction plane at z=DECK).
- Full 2x2 assembly: parametric build_tile() with dovetail teeth (neck 8/head 13/depth 8mm, re-entrant → in-plane lock) on the 2 interior seams, ownership alternating, neighbour notches +0.2mm clearance, on 10mm seam rails; teeth at +/-20mm from center reinforce the junction; leg setbacks (front legs >=30mm behind lip). Built M/H/H/K in real coords, validated: all watertight, **all 6 pairwise interference = 0**, assembly 237.6x339.2x19mm, each print tile 126.8x177.6mm (fits bed), ~386g PLA.
- Review: geometry-analyze.js FAIL was a FALSE POSITIVE (411 "overhangs" all 90deg = vertical walls); trimesh confirmed only ~60 real downward faces (groove ceiling, bridges <2mm). print-reviewer verdict **PASS WITH CONDITIONS** (brim outer frame, slicer-check, optional test prints).
- Two-color: built 4 letter glyphs, boolean-split each tile base=tile-glyph / letter=tile∩glyph (trimesh manifold). Per-tile -base.stl + -letter.stl, print-oriented; bundled into single -bicolor.3mf per tile.
- Leg fix: inner foot was at |y|=40 (asymmetric) → moved to |y|=30 for a clean rectangle. Front-row offset (135 vs 150) kept — functional (lip clearance).
- Material reduction (user wanted ~50% less): pivoted to **uniformly perforated deck** (holes everywhere) split by color — but that dissolved letter legibility. Switched to user's "hollow middle / negative letter": **shapely-eroded glyph → solid OUTLINE ring (3.5mm wall, hollow center)** = legible + drains + 64% less letter material (9.3 vs 26cc). Field perforated (~40% open). Tile ~57cc vs 79 = ~30% lighter. User: "Lock it, build all four."
- Sent renders to user's Telegram throughout (via telegram plugin, NOT belfry which is text-only).

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Subtractive solid-plate field (holes cut out) | Additive thin swirl arms were fragile at junctions; material between holes is full-width/robust by construction; letters can't float |
| U-channel recessed outline for letter | Keeps planar, prints clean, makes letter pop without raised features |
| Dovetail (re-entrant) jigsaw teeth | Lock pieces in-plane (drop-in), gravity holds down; rectangular tabs wouldn't lock |
| Two-color via base/letter bodies (3MF) | One bicolor print per tile (NOT modular inlays); slicer assigns 2 filaments |
| Hollow-outline letter (shapely erode) | User idea: legible negative letter, drains, ~64% lighter — fixes the legibility loss from uniform perforation |
| ~30% lighter not 50% | Big solid letter was the floor; hollowing it + perforating field gets ~30-40%; true 50% needs fragile ribs |

## Key Learnings
- Fusion MCP `execute_code` returns ONLY geometry deltas (no stdout/return). Read data back via the vault bind-mount side-channel, or export STL + measure in trimesh.
- `/workspace` ↔ Windows `C:\Users\aes\Documents\AI\Claude Code in Container` (host daedalus). Export STLs to that Windows path → appear in-container.
- Fusion Combine-Join keeps DISJOINT tool bodies separate (doesn't weld non-touching). Letter glyphs + severed slivers stay separate.
- 30s per-call limit; build each tile in a FRESH doc (documents.add) to avoid stale-sketch slowdown/timeouts.
- Cutting a letter VOID after dense holes severs thin field slivers (loose bits) — avoid by margin, or perforate uniformly then split by color.
- trimesh manifold boolean rejects concatenated multi-body meshes ("not all volumes") — boolean per single watertight body.
- Renamed Fusion bodies' order != creation order — map glyphs to tiles by centroid, not index (mis-pairing left H/H2 letters empty once).
- telegram plugin reply needs chat_id=8471234222 (from ~/.claude/channels/telegram/access.json); belfry reply is text-only.
- Added reusable `--overlay-stl`/`--overlay-rgb` + `top` angle to scripts/render-part.py for two-color previews.

## Files Modified
- `designs/mailbox-standoff-grate/requirements.md`, `spec.json` — created (describe original additive-vortex concept; NOT yet updated to final subtractive+jigsaw+two-color+perforated design)
- `designs/mailbox-standoff-grate/build_assembly.py` — parametric 2x2 builder (supersedes build_quadrant.py, deleted)
- `designs/mailbox-standoff-grate/output/` — tile STLs, print/ (single-color), print2c/ (two-color -base/-letter STLs + -bicolor.3mf), assembly + many iteration renders, print-review.md, tileperf-M.stl, glyphM.stl, pf-base/pf-letter-outline.stl, pf-outline-iso.png
- `scripts/render-part.py` — added --overlay-stl/--overlay-rgb + `top` angle preset
- vault note `2026-06-16-mailbox-standoff-plate.md` — extensive design log

## Follow-ups
- [ ] Finish the 4 FINAL perforated+hollow-outline tiles: H perf tile built in Fusion (not exported); still need H2, K perf tiles + 4 glyphs, then container split (base = tile-glyph; letter = shapely hollow-outline ring), per-tile -bicolor.3mf, re-verify jigsaw interference, assembly render.
- [ ] Update spec.json + requirements.md to match FINAL design (subtractive perforated plate, dovetail jigsaw, hollow-outline two-color letters).
- [ ] README newest-first row + design doc; commit/push (NOT yet committed — user hasn't asked).
- [ ] Print conditions: brim outer frame (not jigsaw edge), Bambu Studio slicer-check 0 supports, optional test prints (jigsaw mating pair, leg-root, letter sample).

## Solutions & Fixes
- geometry FAIL false-positive: verified real overhangs in trimesh (normal_z < -cos45, above bed) — only groove ceilings (<2mm bridges). Part prints support-free deck-down.
- Letter legibility vs material: uniform perforation killed the letter → hollow-outline (shapely buffer(-3.5) difference) keeps it readable.
- Field fragmenting at big holes (r1=16.5 → 17 bodies) → backed off to r1=11 (one connected body, ~40% open).
