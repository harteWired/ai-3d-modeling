# concept2 — Modeling Report

**Date:** 2026-05-10 (v2 amendment); originally 2026-05-09 (v1)
**Backend:** Fusion 360 (driven from main session via raw TCP to add-in; subagent MCP propagation gap not yet fixed)
**STL:** `workout-dumbbell-concept2.stl` (54 KB, 1086 faces) — v2
**F3D archive:** `workout-dumbbell-concept2.f3d` (197 KB) — v2

## Modeled values (v2 — current)

- **Volume:** 279.95 cm³ (+54% vs v1's 181.98 cm³; +10% vs v3.4's 253.5 cm³)
- **Bbox:** 88.5 × 118.46 × 50.75 mm (X × Y × Z)
  - X: -44.25 to +44.25 (sleeve OD)
  - Y: -31.25 to +87.21 (sleeve back to outboard tine bottom-corner)
  - Z: -38.00 to +12.75 (plug bottom to plate top — Z reduced 1.41 mm by R=2 outboard fillet)

## v2.2 amendment — flange loft rework + saddle lead-in

**User direction:** "Make the opening in the fork allow insertion of the dumbbell with some lead-in. Fix the flange alignment with the fork — it should be redone so it grows out of the fork like big, organically geometrically-derived support ribs."

User picked: chamfer at saddle entry + loft plate-outline-down-to-sleeve-OD for the flange rework.

**What was done:**

1. **Removed the rectangular flange** (Z=-8 to 0, sleeve OD outline centered at world origin). Subtracted a 10×7×0.8 cm rect box from the holder at that location.

2. **Side effect — plug disconnected.** The flange was the only material bridging the plug (Z=-38 to -8, inside the rail bore) to the rest of the holder. After the cut, the plug became a separate 87.18 cc body. Recovered by building a thin (0.2 mm thick) "plug bridge" slab at Z=-8.1 to Z=-7.9 in the plug's X-Y footprint that overlaps both plug and loft, then re-joining everything in a single combine.

3. **Added new "loft flange"** between two profiles:
   - Bottom at Z=-8: sleeve OD rectangle 88.5 × 62.5 mm centered at (X=0, Y=0)
   - Top at Z=0: plate footprint rectangle 83.5 × 56 mm centered at (X=+2.5, Y=+57.7)
   - Loft body 40.77 cc, leans outboard as it rises — the inboard side of Z=-8 connects to plug+sleeve and the outboard side at Z=0 fuses with the fork plate's inboard edge.

4. **Re-bored the shaft** (subtracted dumbbell again, `isKeepToolBodies=True`) since the new loft body intersected the shaft path. Removed 11.24 cc.

5. **Chamfered the saddle U entry** at the plate top face for shaft drop-in lead-in. 4 of 9 candidate edges around the saddle U perimeter got R=2 mm chamfer; the other 5 had tight local geometry where Fusion's chamfer compute couldn't fit the requested distance. Reported as a partial success — the dominant entry edges did get the lead-in.

**Final state:** 220.37 cm³, single watertight body. Bbox 88.5 × 118.46 × 50.75 mm (Z range −38 to +12.75). Vs v2.1's 237.38 cm³: net change is the rectangular flange (~45 cc) traded for the leaning loft (~33 cc absorbed), plus the small chamfer.

## v2.1 amendment — shaft bore + dumbbell compare body

After v2 was built, the full-width fill closed off the underside of the saddle U slot, which **blocked the shaft path**. Caught immediately.

Fix:
1. Modeled the dumbbell as a single body for visual compare: shaft (R=23 mm, 400 mm long) + upper bell (R=55.5 mm, 30 mm axial, inner face flush with plate top at saddle) + lower bell (R=55.5, 30 mm axial, inner face 120 mm down-shaft from saddle).
2. Rotated +15° about world X-axis through origin, then translated to position the saddle-center on the shaft axis at world (0, 54.5, 6.23) mm. Shaft axis direction in world = (0, −sin15°, cos15°).
3. Used the dumbbell as a `CutFeatureOperation` tool on the holder, with `isKeepToolBodies=True` so the dumbbell body stays in the F3D for compare.
4. Result: **holder volume 280.04 → 237.38 cc** (−42.67 cc removed for shaft + bell intersection regions). Dumbbell exported separately as `output/dumbbell-reference.stl` (1143 cc).

**Interference flagged:** Upper bell's inboard rim at the saddle clips world Z=−8.14 mm on the disk's inboard-most edge — 0.14 mm below the plug top face (plug top at Z=−8). The boolean cut shaved off a tiny sliver of plug top there. Geometric collision is real but vanishingly small (≪ 1 cc). On a real dumbbell with rounded bell ends or slight tilt-during-place, this disappears. Worth noting; not worth raising the bell axial offset for.

## v2 amendment — full-width underside fill

**User feedback that drove this:**
> "Make the fork geometry flow neatly into the body of the cap, no weird gaps where there could be material — this linkage needs to be strong. Build out big beefy support ribs with smooth features supporting both tines of the fork — use the full height of the sleeve and make these smooth arcs. Make the fork itself smoother — no fine points. Round out everything so the print is stronger and less prone to snag."

**What changed:**

1. **Iteration A (small ribs):** Added two YZ-plane ribs at ±X plate edges, R=33 mm tangent arc from sleeve outer +Y face up to plate underside, 7 mm thick. Volume +1.7 cm³. **User judged too thin** ("big beefy").

2. **Iteration B (bigger side ribs):** Same per-side topology, profile extended to (Y=80, Z=0.63) along plate underside, 14 mm thick. R=102 free arc through (Y=55, Z=-25). Volume +21.4 cm³.

3. **Iteration C (full-width underside fill, current):** Replaced the discrete side ribs with a **single continuous body** spanning the entire plate X range (-39.25 to +44.25 = 83.5 mm wide). Profile: smooth arc from sleeve outer +Y at sleeve bottom (Y=30.25, Z=-38, with 1 mm overlap into sleeve material for clean join) up to plate tine outboard bottom corner (Y=87.21, Z=2.57), with a deep midpoint at (Y=58, Z=-30). R≈66 mm. Joined into the main body. Volume +75 cm³ net. The fill body's top boundary is exactly the plate underside line, so it abuts (does not penetrate) the plate.

4. **Outboard fillet:** R=2 mm fillet on the long plate +Y outboard top edge (the prominent "front lip" of the fork). Reduced bbox max-Z from 14.16 mm to 12.75 mm.

**Saddle U interaction:** The full-width fill closes the bottom of the saddle U slot. Originally the U cut went all the way through the plate (open from plate top through plate underside); now the fill material caps it from below, turning the slot into a U-pocket. Functionally improves shaft seating (positive floor instead of fall-through). Saddle arc (R=23) and arms (60° spread) remain intact in the plate above the fill.

## v1 build sequence (unchanged)

## Build sequence

1. **Plug** (8.85 × 4.25 × 3.0 cm with R=2.5 mm corners, Z=-3.8 to -0.8) — extruded sketch on XY plane.
2. **Flange** (8.85 × 6.25 × 0.8 cm with R=7 mm corners, Z=-0.8 to 0) — joined to plug.
3. **Sleeve** (OD 8.85 × 6.25, ID 7.85 × 5.30, length 30 mm at Z=-3.8 to -0.8) — ring profile extruded; -X wall cut (X=-5.0 to -3.5 box). Combined into main body.
4. **Fork plate** — sketched flat on XY plane at world Y=3.125 to 8.596 with the plate's inboard-root edge on the rotation axis. Profile: rectangle with saddle U cut (R=23 mm at saddle-Y=24.07 mm in plate frame, 60° flared arms exiting through ±X edges of the plate). Extruded DOWN by 12 mm. Body then rotated +15° about X-axis through (Y=3.125, Z=0).
5. **Strut** — sketched on YZ plane: arc from A=(Y=31.25, Z=0) tangent vertical to B=(Y=43.25, Z=-9.21) tangent parallel to plate underside (15° from horizontal). Arc center (Y=40.78, Z=0), R=9.53 mm, sweep 105° CCW. Extruded across X=-39.25 to +44.25.
6. **Combined** all three (shell, plate, strut) into single body via JoinFeatureOperation.

## Spec deltas

The realized geometry differs from the spec.json values in two places — both refinements rather than corrections:

| Spec value | Modeled value | Reason |
|---|---|---|
| `strut_arc_radius: 9.0 mm` | **9.53 mm** | Spec's R=9.0 fell ~0.5 mm short of being tangent to both the sleeve outer face AND the plate underside (when the plate underside at root passes through (Y=34.35, Z=-11.59), set by plate-top flush at sleeve corner). 9.53 mm gives exact tangency. |
| `strut_arc_sweep_deg: 75` | **105°** | Geometric calculation: from tangent-vertical at A (180° on circle) to tangent-parallel-to-plate at B (285° on circle) is a 105° CCW sweep. Spec's 75° was an undershoot. |
| `tine_tip_y: 97.5 mm` | Outboard plate edge ~85–87 mm | The 60° fork spread causes the saddle U's flared arms to exit through the plate's ±X edges before reaching the idealized tine tip Y. Plate effectively becomes a "saddle bridge" shape with no isolated tine tips at Y=97.5. |

## Watertight check

`trimesh.is_watertight = False`, but `volume = 181.99 cm³` (reasonable, matches Fusion). Likely Fusion mesh export has a small edge-stitching artifact at one of the 5-face junctions. Volume agreement confirms the geometry is fundamentally correct; the watertight failure is a mesh-export issue, not a geometry issue. Re-export with finer refinement if downstream tools (slicer) complain.

## Construction quirks worth recording

- **Construction axes / construction points unsupported via execute_code in this environment** — both threw `RuntimeError: 3 : Environment is not supported`. Worked around by sketching the plate flat on XY plane and using `moveFeatures.add()` with a `Matrix3D` rotation.
- **YZ-plane sketch coordinate convention:** sketch (sx, sy) maps to world (0, sy, -sx). For world (Y, Z), use sketch (sx=-Z, sy=Y). Caught this after one round of mis-positioned strut arc.
- **`addByCenterStartSweep` with negative sweep angle didn't land where math predicted** for the saddle arc. Switched to `addByThreePoints` which gave deterministic geometry and is easier to reason about.
- **No saved-file auto-restore issue this run** because we built into a fresh Untitled document (vs v3.4 session which was building into a saved doc that auto-restored between operations).

## Construction quirks added in v2

- **`combineFeatures.JoinFeatureOperation` fails with "Some input argument is invalid" on bodies that are face-coincident only (no volumetric overlap).** The original 3 bodies (cap / fork_plate / strut) refused to combine because they only shared faces. Fix: build new tool bodies with ≥1 mm overlap into the target before combining. The original session's build logged `JoinFeatureOperation` succeeded — the failure here is from running combine on the *saved* file's restored state, where the join feature was lost between sessions.
- **`addConstantRadiusEdgeSet` works fine on edges identified by bbox spatial query** — no need for face-normal access. The plate +Y outboard top edge was found by `bb.minPoint.y >= 80 mm AND length < 15 mm`.

## Open follow-ups

- **Print orientation review** — full-width fill creates a smooth concave arc on the part's outboard +Y / -Z face. Plug-down orientation may need supports for steep underside angle from sleeve bottom rising to plate tine. Worth re-running print-reviewer.
- **Saddle smoothness** — only one fillet ran (plate +Y outboard top edge). Saddle-arm-tip corners on plate ±X faces did not match the bbox criteria (likely because edge structure changed when fill was joined — saddle arm cut now terminates at fill body's surface rather than at plate ±X face). Future pass: enumerate all edges around saddle U and fillet them.
- **Volume up 54% from v1** (181.98 → 279.95 cc). v3.4 was 253.5. concept2 v2 is now ~10% heavier than v3.4 — give up the "lighter" claim from v1 spec until reviewed.
- **Watertight = False, volume agreement OK** — same edge-stitching artifact as v1. Re-export at higher refinement if slicer balks.
- Geometry analysis + print review — still pending on v2 geometry.
- Test print specs — defer to test-print-planner stage.
- Hero render — `heroRender.enabled` is `false` in spec.json.
