---
date: 2026-04-26
project: 3d-printing
type: session-log
---

# 2026-04-26 — ptouch-cradle tray v8 through v11

## Quick Reference
**Keywords:** ptouch-cradle, tray, S-curve sweep, 3D corner blend, r=wall_t cap, top-edge fillet, ID brief alignment, watertight CGAL, coincident planes, sub-mm slivers, soft-fade peaks, printer-corner-fit U-test → 2-sides-3-corners, hollow test prints, cap inset clamp, slab-stack discretization, lerp Y-stack, inflection point, ogee S-curve, tangent continuity, cap outer-edge top, modeler-notes-v8 v9 v10 v11, vault next-steps note

**Project:** 3d-printing

**Outcome:** Iterated four post-ship patches (v8 → v9 → v10 → v11) on the ptouch-cradle tray. v8 fixed corner-tab artifacts and sub-mm slivers. v9 introduced an S-curve sweep + 3D corner blend (sloped wall top from inner z=10 to outer arc(x)) eliminating the inside-the-bin "blade" the user flagged across multiple critique screenshots. v10 aligned the top-edge fillet with the cradle by proportion (r=wall_t for both parts) and resolved a watertight regression by pulling back_sides_mask y-extent back 0.05mm. v11 closed a 1.6mm height mismatch between the S-curve top (z=30) and the side-wall cap outer-edge top (z=28.4) by lowering the S-curve to z=28.4 — the corner now reads as one continuous surface. Also converted the printer-corner-fit test print from L-shape → U-shape → "two full sides + 3 corners" geometry that pins both pocket X and Y dimensions in 11 cm³.

## What Was Done

1. **printer-corner-fit test print iteration** (commits `cd1a88e`, `796620f`):
   1. L-shape (1 corner) → U-shape (3 walls, 2 back corners, full pocket length, half height) — but the open front left pocket Y dimension unconstrained.
   2. User pushed back: "fully open on that side… will not confirm a key dimension."
   3. Final geometry: two full sides (back wall + right long wall) + two stubs forming THREE inside corners (back-left, back-right, front-right). Front-left intentionally absent. Pins both X (80mm) and Y (154mm) interior dims; ~10.9 cm³ vs L's 13.3 cm³.
   4. Saved a memory entry on this lesson: spatial-awareness rule for test-piece design — count which dimensions are actually pinned by walls; an open side leaves that dimension unverified. Memory file: `feedback_test_print_dimension_capture.md`.

2. **Tray patch v8 — corner tabs + sub-mm slivers** (commit `4cece6e`):
   1. Issue: "awkward little tips" at upper corners of front-wall scoop. The single quarter-arc r=20 started at the side-wall INNER face (x=wall_t), leaving a 1.6×1.6mm corner column at full z=30 outside the arc — read as a sharp tab.
   2. Issue: 3 sub-mm slivers (0.09–0.11mm) at z=29.9 near the front corners — the back/sides cap stack inset (r=2 vs wall_t=1.6) was leaving a thin "hat" of unsupported material.
   3. Fix: extended the arc to start at the OUTER edge (x=0 / x=ext_w) — tangent at z=ext_h is horizontal, flush with side-wall top. Restricted `back_sides_mask` corner buffers to y ≤ ext_d-wall_t so the cap-carve doesn't operate in the front-wall slab corner column. Added a `clamp_inset` arg to `footprint_fillet_stack` capping inset at wall_t-1.0=0.6 to keep wall ≥ 1mm thick everywhere.

3. **Tray patch v9 — S-curve + 3D corner blend** (commit `3601789`, part 1):
   1. User submitted three reference screenshots in vault inbox: "weird feature angle" (triangular flat face inside bin at corner), "weird mating feature" (visible slab-step ridges + sharp boundary at y=92.6), and "bad fillet — lost design intent" (vertical-tangent kink at front-wall-top end).
   2. Issue A: single quarter-arc had horizontal tangent at z=30 (good) but VERTICAL tangent at z=10 — 90° kink against the flat front-wall top.
   3. Fix A — S-curve: replaced single r=20 arc with TWO tangent-continuous quarter-arcs r=10 each, joined at inflection point (10, 20) with vertical tangent. Both endpoints C¹: horizontal tangent at z=30 AND z=10.
   4. Issue B: the front-wall slab cutter was extruded along Y over the full 1.6mm wall depth, so for every Y the wall top followed arc(x). At corner zones (x near 0), arc(x) reaches z≈30 — front-wall slab back face (visible from inside) extended from z=10 (ramp top) up to arc(x), forming a tall vertical "blade" / triangle the user rejected.
   5. Fix B — 3D corner blend: rebuilt cutter as a 16-slab Y-stack interpolating between INNER profile (flat top at z=10 across full x range) and OUTER profile (the S-curve). Wall top now slopes from z=10 (inside) to z=arc(x) (outside) over the 1.6mm wall depth — slope is 12.5:1 ≈ 4.6° from horizontal, prints face-up cleanly.
   6. Fix C — bumped `top_fillet_steps` default 24 → 48 so cap step ridges (~0.04mm) are sub-FDM-resolution.

4. **Tray patch v10 — r=wall_t cap aligned with cradle** (commit `3601789`, part 2):
   1. User: "make sure the top fillet is aligned with what's going on with the cradle, too. These should be two parts of a whole, the ID agent specified them together."
   2. Brief inspection: cradle uses `fillet_utility_r = 3.0` on `wall_thickness = 3.0` — i.e., r = wall_t exactly. Cap rolls cleanly from outer face to inner-face apex with no clamp.
   3. Tray was using r=2 with a clamp at wall_t-1.0=0.6 → small flat plateau at cap top, breaking the "rolls to a point" cradle signature.
   4. Aligned by proportion: tray r=2 → r=1.6 (= wall_t). Same design proportion across the assembly, different absolute radii because walls differ. Front-wall flat-top fillet stayed at r=0.8 per brief's thin-wall exception framing.
   5. Watertight regression discovered: r=wall_t cap created coincident planes between back_sides_mask (clip at y=92.6) and the front-wall cutter's inner-slop slab (also at y=92.6). CGAL produced 42-46 broken faces.
   6. First attempt (Option B — clamp at wall_t-0.05=1.55) didn't work because the mask boundary was the actual coincident plane, not the cap inset.
   7. Resolution (Option C): pulled `back_sides_mask` y-extent from `ext_d-wall_t=92.6` to `ext_d-wall_t-0.05=92.55`. The 0.05mm gap is inside the cavity (no visible material) but decouples the planes. Watertight restored.
   8. Brief updated: `fillet_schedule.tray_top_edge: 2.0 → 1.6` with cradle-alignment prose.

5. **Tray patch v11 — S-curve top flush with cap outer-edge** (commit `ce60bc0`):
   1. Two new inbox screenshots: "odd gap between front of tray adornments and sidewall" (slicer view showing gap between S-curve and cap surfaces) and "Discontinuous thin front face on front wall" (1.6mm vertical step at y=92.55).
   2. Root cause: S-curve cutter started at `(0, ext_h) = (0, 30)`, but side-wall cap rolls to outer-face top at `z = ext_h - r = 28.4`. The 1.6mm mismatch produced (a) the gap (S-curve face starts higher than cap face at the corner) and (b) the thin step at y=92.55 (cap-mask boundary).
   3. Wrote vault next-steps note `vault/projects/3d-printing/ptouch-cradle-v11-next-steps.md` capturing root cause + Option A fix recipe, then user said go execute.
   4. Fix (Option A): lowered S-curve top to `z = s_curve_top_z = ext_h - top_edge_fillet_r = 28.4`. Re-derived S-curve: arcs now r=9.2 each (was r=10), horizontal extent 18.4mm (was 20), inflection point (9.2, 19.2). Front-wall flat middle slightly wider: x ∈ [20.0, 83.2] (was [21.6, 81.6]).
   5. Cutter polygon updated with vertical drop edges at outer corners (ext_w, ext_h) → (ext_w, s_curve_top_z) and (0, s_curve_top_z) → (0, ext_h) so the corner column outer edge gets carved from z=30 down to z=28.4.
   6. Watertight preserved (v10's Option-C decoupling at 92.55 still holds). Volume 38242 → 38196 mm³ (-46 mm³, exactly the predicted corner-column carve). Thin walls 26 → 24.
   7. Visually confirmed in renders: S-curve sweep flows continuously into rolled cap, no V-wedge gap, no thin step.

6. **Doc + brief updates** (commits `87783a1`, `ce60bc0`):
   1. `docs/ptouch-cradle.md` rewritten end-to-end across the four patches: captions, ASCII diagram, spec table, Features section, Printability table (sub-mm slivers reframed as accepted "soft fade" tradeoff), Design Log entries for v8/v9/v10/v11, Downloads list with v9-v11 modeler-notes links, Pipeline row updated to "7 rounds + 4 patches".
   2. `id/brief.md` updated: fillet schedule + S-curve prose for v10 alignment and v11 cap continuity.
   3. README cradle row updated: mentions S-curve sweeps + r=wall_t fillet alignment + 2 test prints.
   4. All tray PNG renders refreshed in `docs/images/ptouch-cradle/` (force-add since `designs/*/output/*.png` is gitignored).

## Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| printer-corner-fit: two full sides + 3 corners (final shape) | Pins both X and Y interior dims of the pocket — open side leaves that side unverified. Less filament than U with full-length long sides (~10.9 vs 14.8 cm³); validates 3 of 4 corners (4th covered transitively because corner geometry is identical). |
| Test prints hollowed by default (codified in test-print-planner agent) | Solid blocks larger than ~2cm³ that aren't validating bulk-material behavior should be hollow shells. Avoids the round-1 wasted-filament pattern. |
| S-curve over single quarter-arc | Tangent continuity at BOTH endpoints is geometrically impossible with a single circular arc when the two surfaces it joins have parallel (horizontal) tangents and a non-zero offset. Two quarter-arcs joined at an inflection point is the simplest tangent-continuous solution. |
| 3D corner blend via 16-slab Y-stack lerp (vs minkowski hull or polyhedron) | Cleanest in OpenSCAD: each slab is a thin linear_extrude of a polygon, and the per-slab polygon is computed by lerping vertex-wise between INNER and OUTER profiles. Both polygons must have the same vertex count and walk order. The hull alternative would have produced the same surface but is harder to reason about and slower in CGAL. |
| Soft-fade corner peaks accepted (vs increasing wall_t to 3mm) | The user explicitly chose "soft fades instead of sharp peaks." Slicer truncates unprintable sub-mm slivers as a 1-2mm vertical taper — cosmetic only, no structural impact. Bumping wall_t would require re-spec of the slot fit and tray fit-pair test print. |
| r=wall_t alignment principle (cradle r=3, tray r=1.6) | Same design proportion, different absolute radii, because the parts have different wall thicknesses. Reads as a unified family. The user's framing: "these should be two parts of a whole, the ID agent specified them together." |
| Option C (mask y-pullback) over Option B (cap inset clamp) for watertight resolution | The clamp value didn't matter — the mask boundary was the coincident plane, not the cap inset. Pulling the mask back 0.05mm decouples the planes for clean CGAL while preserving the r=wall_t cap proportion. |
| v11 Option A (lower S-curve top) over Option B (extend cap into corner column) or C (cutter follows cap profile) | Cleanest geometric fix. B would re-introduce the v10 watertight regression. C would require encoding the rolled cap curve as a 2D XZ shape — much more cutter polygon machinery for the same visual result. |
| Vault next-steps note before executing v11 | User asked for a pause-point ("don't execute, I need to reboot"). Captured root cause + 3 fix options + recommendation in `vault/projects/3d-printing/ptouch-cradle-v11-next-steps.md` so the next session has full context. Pattern worth keeping. |

## Solutions & Fixes

1. **Watertight regression after r=wall_t cap (v10):** the "obvious" fix (clamp the cap inset to slightly less than wall_t to leave a plateau) doesn't work because the mask y-boundary at `ext_d-wall_t` is coincident with the front-wall cutter's inner-slop slab, regardless of where the cap material itself ends. The actual fix is decoupling the mask y-boundary by ε. Took two failed attempts to land this insight.

2. **Front-corner S-curve / cap mismatch (v11):** the v9 S-curve was specified to start at the same z as the side-wall TOP (z=ext_h=30), but the side-wall TOP is the cap APEX (inner face), not the cap's outer-face top (which is at z=ext_h-r=28.4). Mismatched the wrong reference surface. Fix: explicitly tie S-curve top to `ext_h - top_edge_fillet_r`, not `ext_h`.

3. **3D corner blend prints face-up cleanly:** worried briefly about the 4.6° wall-top slope being an overhang, but it's well below the 45° max and prints face-up with no support. The 16 Y-slabs in the lerp stack discretize cleanly at 0.1mm Y-thickness each — slicer handles them as fine vertical walls.

4. **Slab-stack cap step ridges:** at draft `top_fillet_steps=24`, slab z-thickness was ~0.083mm — visible as ridges in close-up renders. Doubled to 48 → ~0.04mm steps, sub-FDM-resolution and invisible at any zoom.

5. **printer-corner-fit "fully open side" lesson:** when designing simplified test pieces, walk through each parent dimension and confirm it's actually pinned by walls in the test piece. An open side does NOT verify the dimension across that side. Saved as memory `feedback_test_print_dimension_capture.md`.

6. **Brief drift detection during v10:** the brief said "tray_top_edge: 2.0 (back/sides), 0.8 (front, thin-wall exception)" but ALSO said "fillet schedule has just two values: r=3 utility, r=10 hero." Internal contradiction. The user's instinct ("align with cradle") was correct — the brief had drifted from the unifying r=wall_t principle. Resolved in v10 by replacing r=2 with r=1.6 (= wall_t).

## Key Learnings

1. **Tangent continuity matters more than radius equality.** A single arc with the right radius can still produce a visible kink if it doesn't tangent-match the surface on the other side. The S-curve fix was about tangent continuity, not radius.

2. **For 3D corner fillets between two surfaces of different heights, a Y-stack lerp between inner and outer profile polygons is a clean OpenSCAD pattern.** Both polygons must have identical vertex order. If you need to pin certain vertices to the same z on both profiles (e.g., outer-corner vertices to keep the cutter's outer side faces vertical), use flags like `keep_first_z`/`keep_last_z` on the lerp.

3. **CGAL's coincident-plane sensitivity is real.** When two CSG operations operate on the same plane to within ε, the output mesh can be non-manifold even if the geometry is logically clean. Decouple boundaries by ≥0.05mm. The 0.05mm offset is invisible in print (sub-FDM-layer) and at any realistic render zoom.

4. **r=wall_t is the natural cap proportion.** It rolls the entire wall thickness into the fillet, terminating at a point at the inner face. Anything larger requires clamping (and produces a flat plateau); anything smaller leaves an angular outer corner. Use this as the default for any wall-cap fillet, scaled to the part's wall thickness.

5. **Reference S-curves and ogees from classical molding profiles.** Two tangent-continuous quarter-arcs joined at an inflection point ("cyma recta") give parallel-tangent continuity at both endpoints. The math is simple: r_each = (z_drop) / 2, total horizontal extent = 2 × r_each. If you're trying to blend two horizontal surfaces with a vertical offset, this is the right primitive.

6. **A "vault next-steps note before executing" pause-point is high-value when the user is interrupted mid-iteration.** The user reboots, comes back, and the next session has full root-cause + recommended fix already written. Beats trying to reconstruct context from chat scrollback. Worth a skill or convention.

7. **Inbox screenshots with red-arrow annotations are the highest-bandwidth bug report format we have for visual issues.** The user's three v9 critique images and two v11 critique images precisely communicated what to look at — way more efficient than text descriptions. Pipeline should encourage this format.

8. **Slicer-view screenshots reveal real-printer issues that renders hide.** The v11 issue (gap between S-curve and cap, thin front face) was visible in slicer view but barely visible in OpenSCAD renders — because the slicer's perimeter visualization makes thin steps obvious that surface-shaded renders smooth over. Worth recommending the user view tricky geometry in the slicer before approving a ship.

## Files Modified

**SCAD source:**
1. `designs/ptouch-cradle/tray.scad` — major rework across patches v8–v11. New params: `s_curve_top_z`, `front_wall_side_fillet_r_each`, `front_wall_side_extent`, `front_wall_y_slabs`. New helpers: `_front_wall_top_cutter_pts`, `_front_wall_top_cutter_pts_inner`, `_flatten_arc_to_flat_top`, `_lerp_pts`. New cutter module emits 16-slab Y-stack lerp between INNER and OUTER profiles.

**Test prints:**
2. `designs/ptouch-cradle/test-prints/printer-corner-fit/printer-corner-fit.scad` — L → U → 2-sides-3-corners.
3. `designs/ptouch-cradle/test-prints/printer-corner-fit/spec.json` — dimensions, params, volume range.
4. `designs/ptouch-cradle/test-prints/printer-corner-fit/requirements.md` — purpose, verification method, geometry.
5. `designs/ptouch-cradle/test-prints/test-prints.json` — entry rewritten 3 times across the iterations.

**ID brief + modeler notes:**
6. `designs/ptouch-cradle/id/brief.md` — fillet schedule (v10 r=wall_t alignment), S-curve description (v9 + v11 cap continuity), feature prose updates.
7. `designs/ptouch-cradle/id/modeler-notes-v9.md` (new) — v9 patch detail with geometric math.
8. `designs/ptouch-cradle/id/modeler-notes-v10.md` (new) — v10 alignment + watertight Option-A/B/C resolution.
9. `designs/ptouch-cradle/id/modeler-notes-v11.md` (new) — v11 S-curve top flush with cap.

**Public docs:**
10. `docs/ptouch-cradle.md` — captions, ASCII diagram, spec table row, Features section, Printability table, Geometry Analysis paragraph, Slicer checklist, Print Settings supports row, Design Log v3-patch-v8/v9/v10/v11 entries, Downloads modeler-notes links, Pipeline row.
11. `README.md` — cradle row description (S-curve sweeps + r=wall_t alignment + 2 test prints).

**Doc images (force-added since designs/*/output/*.png is gitignored):**
12. `docs/images/ptouch-cradle/tray-front.png`
13. `docs/images/ptouch-cradle/tray-iso.png`
14. `docs/images/ptouch-cradle/tray-right.png`
15. `docs/images/ptouch-cradle/tray-top.png`
16. `docs/images/ptouch-cradle/tray-user-front.png`
17. `docs/images/ptouch-cradle/tray-user-front-threequarter.png`
18. `docs/images/ptouch-cradle/tray-cap-detail.png` (new)

**Generated outputs:**
19. `designs/ptouch-cradle/output/tray.stl` — re-rendered four times (v8, v9, v10, v11).
20. `designs/ptouch-cradle/output/tray-geometry-report.json` — refreshed each patch.
21. `designs/ptouch-cradle/output/modeling-report.json` — patchV9 section added.
22. `designs/ptouch-cradle/test-prints/printer-corner-fit/printer-corner-fit.stl` — re-rendered twice.

**Vault notes:**
23. `vault/projects/3d-printing/ptouch-cradle-v11-next-steps.md` (new) — captured root cause + 3 fix options + recommendation between v10 and v11 ship.
24. `vault/projects/3d-printing.md` — bridge note next-action updated twice.

**Memory:**
25. `home/node/.claude/projects/-workspace-projects-3d-printing/memory/feedback_test_print_dimension_capture.md` (new) — spatial-awareness rule.
26. `home/node/.claude/projects/-workspace-projects-3d-printing/memory/MEMORY.md` — index entry added.

**Commits this session:**
1. `cd1a88e` — printer-corner-fit L → U
2. `796620f` — printer-corner-fit U → 2-sides-3-corners
3. `4cece6e` — tray v8 (corner tabs + slivers)
4. `3601789` — tray v9 + v10 (S-curve + 3D corner blend + r=wall_t cap)
5. `87783a1` — docs v9+v10
6. `ce60bc0` — tray v11 (S-curve top flush with cap)

## Follow-ups

- [ ] Print both test pieces on one bed run (~25 cm³ / ~30 min): tray-slot-fit-pair + printer-corner-fit (2-sides-3-corners). Verify tray-to-slot 0.35mm/side sliding fit AND printer-to-pocket 1mm/side corner fit.
- [ ] If both PASS: print full cradle (~136 cm³) + tray (~38 cm³). Apply silicone feet to cradle base aftermarket.
- [ ] Inspect printed tray corners — confirm soft-fade truncation reads cleanly (vs the sharp peaks in renders). User accepted this tradeoff but it's untested in PLA.
- [ ] If corner fade is unsatisfying after print: revisit Option C from v10 modeler notes (bump wall_t to 3mm, re-spec slot fit). Clean principled fix.
- [ ] Consider extracting the "vault next-steps note before executing" pause-point pattern into a skill or workflow note. Was high-value this session.
- [ ] Consider a slicer-view diagnostic step in the pipeline for designs with thin-wall / sub-mm features. Slicer perimeter rendering catches issues that surface-shaded renders smooth over (the v11 gap was barely visible in OpenSCAD renders, glaring in slicer view).
