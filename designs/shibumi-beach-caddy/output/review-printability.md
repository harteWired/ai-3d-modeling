# Printability Review: shibumi-beach-caddy (v3-rugged-cantilever)

## Data Sources
- Geometry report: **NO** — `output/geometry-report.json` does not exist for this design yet.
- Slicer report: **NO** — `output/slicer-report.json` does not exist for this design yet.
- Fallback to SCAD source: **YES** — this review is based on direct CSG/arithmetic analysis of
  `shibumi-beach-caddy.scad` (v3-rugged-cantilever), cross-checked against `spec.json`,
  `output/strain-report.json`, `output/review-strain.md`, and the v3 renders
  (`v3-iso.png`, `v3-gussets-front3q.png`, `v3-mount-junction3q.png`). The `-front/-right/-top`
  and `caddy-draft-*` renders in `output/` are **stale v1 images** (no gussets visible) and were
  NOT used as evidence for this review.

**Recommendation:** run `node bin/geometry-analyze.js designs/shibumi-beach-caddy` before final
print commitment. This review's overhang/bridge conclusions are derived from hand-traced CSG
geometry (module-by-module transform algebra), which is reliable for the shapes analyzed below,
but a mesh-based pass would give exact overhang-face and bridge-span numbers and is cheap
insurance given none has been run on this v3 geometry yet.

## Print Orientation
**Base-down, as-used** — matches the design directive (WM#1104) and the installed orientation
(no reorientation for print vs. use). All body modules are built as solids from `z=0` upward and
then the whole assembly is trimmed by a global `z<0` cut (`caddy()` assembly, difference against
`translate([0, caddy_depth/2, -500]) cube(...)`), which guarantees a flat, fully-supported first
layer even for the 5°-tilted device channels (see Channel Tilt below).

- Bed contact: `base_plate()` (140 × 170 mm full footprint), `back_spine()` foot, `bottle_cradle()`
  foot, both `side_gusset()` feet, both `back_haunches()` feet, and each channel's flattened base —
  all coplanar at z=0. Good first-layer bed contact area for the main body.
- Z grows: base_plate (0→5.5) → haunches/cradle/channels/gussets (0→their own heights) → spine
  (0→110, tallest feature) → nothing above.
- Installed vs. print orientation: **same.** This was the entire point of the v3 directive — the
  peak tensile fiber at the root runs in-plane with the layers either way, so there's no
  orientation trade-off to make here (confirmed independently below; not re-litigating the
  strain call, only the printability of executing it this way).

## Feature Stack (bed → top)
1. `base_plate` — box 140 × 170 × 5.5 mm (z: 0–5.5), one Ø40 drain hole at bottle centerline
2. `back_haunches` — two 20×20 mm 45° ramp fillets outboard of the cradle (z: 0–20)
3. `bottle_cradle` — Ø111 OD / Ø102 ID cylinder, open front "C", Ø30 cup drain, rim lead-in
   chamfer (z: 0–88)
4. `channel(phone)` — 87×~24 mm outer footprint, 5° back-tilt, lead-in funnel, 2×Ø6 drains
   (z: 0–~92, y: 146–170)
5. `channel(kindle)` — 140×~23 mm outer footprint, 5° back-tilt, lead-in funnel, 2×Ø6 drains
   (z: 0–~100, y: 121–144)
6. `side_gusset` ×2 — 4.5 mm-thick right-triangle fins, 74 mm tall at y=0 tapering linearly to
   0 at y=170, positioned just outboard of the main body (x: ±70 to ±74.5)
7. `back_spine` — 140 × 8 × 110 mm block, top edges chamfered 45° (z: 0–110, tallest feature)
8. `mount_placeholder` — 28.2 × 14.5 × 40.1 mm gray block, **z: 30.5–70.6** (does NOT start at
   the bed — see Transition Checks, flagged)

Cross-reference note (no `modeling-report.json` exists to check against, so this is a
source-level observation instead): `base_plate()` cuts a Ø40 "bottle drain" hole, but
`bottle_cradle()`'s own solid disc (Ø111, z 0–5.5 before its bore starts) sits directly on top of
and unions with that same footprint, and the cradle then cuts its own, smaller Ø30 "cup drain" at
the same center. Net effect: **the functional drain under the bottle is Ø30, not Ø40** — the
base_plate's Ø40 cut is fully backfilled by the cradle's solid disc wherever the cradle sits (it
does nothing at that location). Not a printability problem either way (both are straight
through-holes from the bed, not bridges — see Horizontal Spans), but worth a design-intent note
since the task brief names the 40 mm figure specifically.

## Transition Checks

### Base plate → back spine / bottle cradle
Both features are grounded at z=0 alongside the base plate (union of co-planar solids, not a
stacked transition). **PASS** — no overhang, nothing to support.

### Base/spine → back-corner haunches
45° right-triangle ramp (20×20 mm), solid region shrinks in Y as Z increases (footprint at z=0
spans y 0–20; at z=20 it's reduced to a line at y=0). This is the "easy" self-supporting direction
(like a chamfer/pyramid — each new layer sits fully within the layer below), so the ramp is
printable regardless of the exact angle; 45° here is a comfortable, not marginal, case.
**PASS.**

### Back spine → side buttress gussets (y = 0–8 mm)
Gusset's full inner face (x=±70 plane) is coincident with the spine's side face for this 8 mm
depth, and gusset height there is ~70.5–74 mm — i.e. the gusset is fully face-backed by the
110 mm-tall spine for its entire height in this zone. Robust. **PASS.**

### Side buttress gussets — free span (y = 8–~120 mm) — FLAGGED, see Tips & Extremities
Once past the spine (y > 8), the gusset has **no lateral backing at all** — the bottle cradle
wall sits 14.5 mm away (Ø111 cradle edge at x=±55.5 vs. gusset inner face at x=±70, constant gap,
never touching) and nothing else spans that width until the kindle channel begins at y=121. Over
this ~112 mm run the gusset is a free-standing 4.5 mm-thick fin, tapering roughly linearly from
~70 mm tall (y=8) to ~22 mm tall (y=119), attached to the rest of the model **only along its
bottom edge** where it rests on the 5.5 mm base plate. The gusset's own top-surface slope is not
an overhang problem (same receding-shape argument as the haunches — confirmed by CSG: at any Z,
the valid Y-range only shrinks going up). The issue is a different one: an isolated, tall, thin,
unbraced standing wall. Detailed in Tips & Extremities below. **CONDITIONAL PASS** (will print;
flagged for print-quality mitigation, not a slicer-breaking overhang).

### Buttress gusset → kindle channel (y = 121–144 mm)
Kindle channel's OUTER wall spans the full caddy width (`outer_w = kn_W + 2*wall = 140`, matching
`caddy_w`), so it does touch the gusset's inner face here — but the gusset itself has already
tapered to only ~11–21 mm tall in this Y range, so this is just a short, well-backed rib next to
a much taller wall. **PASS.**

### Phone channel (y = 146–170 mm)
Phone channel's outer wall is only 87 mm wide (`ph_W=81` interior, ±43.5 mm), well short of the
gusset at x=±70 — no contact, but the gusset has tapered to ~0–11 mm tall here anyway, so nothing
of consequence to check. **PASS.**

### Device channel 5° back-tilt (both channels)
Verified by rotation algebra: `rotate([tilt,0,0])` about the channel's own back-bottom pivot
line means the whole channel cross-section shifts by only `layer_height × sin(5°) ≈ 0.0175 mm`
per 0.2 mm layer — both the front and back walls lean at a trivial 5° from vertical, nowhere
close to the 45° limit. Confirms the v2 design note that this tilt is printability-safe.
**PASS** (5° ≪ 45°, ample margin).

### Insertion lead-in funnels (both channels)
`hull()` of a 1.4 mm-chamfer taper over a ~4.4 mm height → slope ≈ atan(1.4/4.4) ≈ 18° from
vertical. This is a *void* that expands going up (thins the wall from nominal 3.0 mm down to a
local minimum of **1.6 mm** right at the rim) — receding-shape direction, self-supporting, and
1.6 mm still clears the 1.2 mm minimum-wall spec, though with less margin than the rest of the
part. **PASS** (note the local 1.6 mm minimum for awareness).

### Bottle cradle rim lead-in chamfer
Same receding-void geometry: wall thins from 4.5 mm nominal down to **3.1 mm** at the very top
rim over a 1.4 mm height (exactly 45°, easy/self-supporting direction as established). **PASS.**

### Bottle cradle front "C" opening
Traced via CSG: the cut is a rectangular notch (flat back wall + two flat side walls), not a
tangent chord across the tube — the box's side planes (x=±39.78) fall well inside the tube's
inner bore radius (51 mm) at the cut's starting Y, so the notch does not create a feathering
knife-edge at the two front "horns." The horns should retain the full 4.5 mm nominal wall
thickness up to ordinary corner edges. **PASS**, with the caveat that this is inferred from
source geometry, not a mesh; worth a quick slicer-preview glance to confirm before printing given
no `geometry-report.json` exists to verify it directly.

### Mount placeholder — FAIL (as currently drafted, not printable in place)
`mount_placeholder()` places a 28.2 × 14.5 × 40.1 mm block at **z = 30.5–70.6 mm**, y = −13 to
+1.5 mm. Only the small sliver from y=0 to +1.5 mm overlaps the spine's footprint (fusing to it);
the remaining ~13 mm of depth (behind the spine, y<0) is a solid block floating **30.5 mm above
the bed with nothing underneath it** — confirmed visually in `v3-mount-junction3q.png` (the gray
block clearly stands off the back face, not touching the plate). As currently modeled, this
geometry would force the slicer to either generate support material under it or fail to bridge
it cleanly (this is a one-sided cantilever with zero starting support, not a bridge with two
supported ends — worse case than a bridge). This is explicitly flagged in the source and
`ARCHITECTURE.md` as a parametric TBD (pending the Phase-1 A/B/C `rail_height` result), so it is
**not a regression to fix in this pass**, but it must be resolved with print-awareness (touch the
bed, or connect continuously to bed-supported material, or be designed for organic/tree support)
before this design is sliced for a real print. **Do not print with `mount_tbd=true` as-is.**

## Tips & Extremities

**Side buttress gussets — the main printability finding of this review.** Height:thickness ratio
at the root (y≈8–40, height 70→62 mm, thickness 4.5 mm) is **~14–16:1**, well past the ~10:1
rule-of-thumb where isolated, unsupported FDM ribs start to show:
- Print-time ringing/ghosting (vertical fine artifacts) on the fin and possibly nearby geometry
  from gantry/cooling-fan-induced vibration, since the fin has no lateral bracing for ~112 mm of
  its 170 mm run.
- Adhesion risk: the fin's only connection to the rest of the body along that run is a thin
  4.5 mm-wide line of contact against the 5.5 mm base plate — a small footprint to carry a tall,
  thermally-isolated feature. This is more of a concern in the **final PETG/ASA material** than
  in PLA prototypes: ASA in particular has higher shrinkage/warp tendency, and an isolated thin
  tall rib (less thermal mass, more exposed surface area than the bulky spine/cradle) is a classic
  warp/corner-lift site — risk of the gusset's back-top corner curling off the bed independent of
  the rest of the part.
- Not a structural risk (`review-strain.md` already shows SF 208 at the worst gusset section,
  treating the gusset as fully disconnected from everything else) — this is purely a
  print-quality/reliability flag, not a strength flag.

Recommended mitigations (none of these change the structural intent — they only add material,
so no functional conflict to flag):
1. Add 2–3 thin (~2–3 mm) connecting webs between the gusset's inner face and the bottle cradle's
   outer wall across the 14.5 mm gap, spaced along the free span — turns an isolated fin into a
   braced rib.
2. Add a small fillet at the gusset-to-base-plate foot (currently a sharp line contact) to widen
   the adhesion footprint from an edge to a proper fillet.
3. Print with a brim specifically catching the gusset feet; if slicing in ASA, expect to need the
   enclosure/chamber heat (X1C has this) plus reduced cooling in that region to control warp.
4. See Test Print Recommendations below for validating this before the full-size print.

**Mount placeholder** is also an extremity concern (see Transition Checks — FAIL) but is
explicitly non-final geometry, not a regression.

No `thin_walls[]` data available (no geometry report) to cross-check further; the two local wall
minima found by hand (1.6 mm at channel funnels, 3.1 mm at cradle rim) both clear the 1.2 mm floor
with reasonable but not generous margin.

## Horizontal Spans
No true two-sided bridge spans were found in this geometry. All apparently-flat surfaces are
either (a) directly backed by solid material below at every point (cradle floor, channel floors),
or (b) straight vertical through-holes from the bed (Ø40/Ø30 bottle drains, 2×Ø6 channel drains) —
which require no bridging since there's no ceiling above the void, just an absent column of
material all the way to the print bed.

| Span | Length (traced) | Slicer bridge? | Result |
|---|---|---|---|
| Bottle-cradle drain (Ø30, effectively supersedes the base plate's Ø40 cut) | straight through-hole, 0 mm bridge | N/A — no slicer report | PASS (no ceiling to bridge) |
| Channel floor drains (2× Ø6, both channels) | straight through-hole, 0 mm bridge | N/A | PASS |
| Mount placeholder underside (y<0 portion) | ~13 mm one-sided cantilever, 30.5 mm off the bed | N/A | **FAIL — not a bridge, an unsupported cantilever; flagged above** |

## Mating Clearances
No real mating geometry exists yet to check. The only mating interface is the Phase-1 capture
socket, and `mount_placeholder()` is an explicit parametric stand-in (`mount_tbd = true`), not
final geometry — clearance analysis is deferred until the Phase-1 A/B/C fit-test sets
`rail_height` and the actual socket geometry replaces the placeholder block. For reference, the
target mount interface per `spec.json` is **28.2 × 40.1 mm, r3.0** (socket backing face) — carry
this forward for the clearance check once real geometry lands.

| Feature | OD/ID | Mate OD/ID | Gap | Role | Result |
|---|---|---|---|---|---|
| Capture socket (placeholder) | N/A — not modeled | 28.2×40.1, r3.0 (Phase-1 backing face) | N/A | mount | **DEFERRED — pending Phase-1 rail_height** |

## Slicer Validation
Not available — `output/slicer-report.json` does not exist for this design. No slicer-derived
support/bridge data to cross-check against the mesh-level findings above. Recommend running
`node bin/geometry-analyze.js designs/shibumi-beach-caddy` (which also drives a PrusaSlicer pass)
before committing to a final print, particularly to get quantitative confirmation on the buttress
gusset free-span behavior and the bottle-cradle "C" opening horn thickness.

## Conflicts
None requiring a function-vs-printability trade-off decision. Both flagged issues (mount
placeholder, gusset free span) have fixes that either are already planned (mount: pending Phase-1
data) or purely additive (gusset bracing webs add material/rigidity without touching the
structural design or the functional envelope of any receptacle). **0 conflicts.**

## Summary
- Data quality: fallback (SCAD source + strain report + renders); no geometry-report.json or
  slicer-report.json exist yet for this design
- Total transitions checked: 11
- PASS: 9
- CONDITIONAL PASS (print-quality flag, not a hard fail): 1 — side buttress gusset free span
- FAIL: 1 — mount placeholder (known non-final geometry, must not be printed/sliced as-is)
- Slicer agreement: N/A (no slicer report run)
- Conflicts requiring user decision: 0

## Test Print Recommendations
- **Side buttress gusset free span**: near the ~10:1 unsupported-thin-wall guidance limit
  (measured ~14–16:1) and first-of-kind in this project (no prior design has an external
  freestanding tapering fin this tall/thin). Test a ~50 mm-deep slice covering the spine root +
  one full gusset cross-section (y = 0–50 mm) before committing the full 170 mm-long part —
  mitigates ringing/warp/adhesion risk cheaply.
- **Bottle cradle front "C" opening / horn thickness**: geometry reports aren't available to
  confirm the traced 4.5 mm horn wall thickness directly. Suggest a quick slicer-preview check
  (or a short top-slice test print of just the cradle rim, z = 60–88 mm) to confirm no feather
  edges before committing the full print.
- **Mount placeholder**: no test print needed yet — this geometry is explicitly non-final;
  re-run this full printability review once the real capture-socket geometry replaces the
  placeholder block (`mount_tbd` → real geometry), since its bed-contact and support strategy is
  entirely unresolved right now.
- Channel tilt/funnel geometry: comfortably within margins (5° tilt, ~18° funnel slope) — no test
  print needed on these specifically.
