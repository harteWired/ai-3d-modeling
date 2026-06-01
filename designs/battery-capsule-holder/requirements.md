# Battery Capsule Holder Requirements

## Design Intent

A low-profile drawer rack that holds 6 battery capsules upright, beaker-rack style.
The user drops capsules in and lifts them out one-handed; the rack lives inside a
drawer and must stay put without fasteners. Each capsule is an asymmetric teardrop
/ D-shaped prism (clear + teal halves, batteries inside). The rack grips the outer
lower body only — it never contacts the inner bore, seam, or upper-half V feature.

The form is **organic and sculptural** — not a rectangular grid block. The outer body
is a smooth, blobby hull that closely envelopes the nested socket cluster, swells
wider at the base, and draws in toward the socket mouths at the top. Rounded
transitions everywhere; no hard-cornered outer walls.

## Print Orientation

Print flat on the bed, open sockets facing up. The socket walls are fully vertical
(no overhangs inside pockets). The bottom floor is the first layer; socket walls
grow straight up. The outer body tapers inward as it rises — the widest cross-section
is at the base. No supports required inside pockets. The outer surface overhang from
the inward taper must be kept within 45° (see Printability Pre-Screen).

## Dimensions & Sources

| Dimension | Value | Source |
|---|---|---|
| Capsule long axis (teardrop widest) | 27.8 mm | Calipered, clear half (max of both halves) |
| Capsule narrow axis (teardrop short) | 23.7 mm | Calipered, teal half (max of both halves) |
| Capsule height assembled | 69.0 mm | Calipered |
| Socket depth | 18.0 mm | User decision, locked 2026-05-31 |
| Pocket profile — long axis (with clearance) | 28.5 mm | 27.8 + 2 × 0.35 sliding fit |
| Pocket profile — narrow axis (with clearance) | 24.4 mm | 23.7 + 2 × 0.35 sliding fit |
| Min inter-socket wall (thinnest bridge) | 1.2 mm | Project 3-perimeter rule (hard floor) |
| Nominal inter-socket wall | 2.0 mm | Design target; modeler must verify tip-to-arc bridge ≥ 1.2 mm |
| Column pitch (narrow-axis, socket center-to-center) | 26.4 mm | 24.4 pocket + 2.0 wall (side-by-side) |
| Row pitch (long-axis, nested 180°) | 27.5 mm | 28.5 pocket − 3.0 mm tip-tuck + 2.0 mm wall |
| Cluster center span, width (2 × col pitch) | 52.8 mm | 2 × 26.4 mm |
| Cluster center span, depth (1 × row pitch) | 27.5 mm | Single row gap (3×2 arrangement) |
| Cluster bounding box (socket extents, 3×2) | ~77 × 56 mm | 52.8 + 24.4 wide; 27.5 + 28.5 deep |
| Organic envelope footprint (approx., with outset) | ~89 × 68 mm | Cluster bbox + ~6 mm organic outset |
| Floor thickness | 3.0 mm | 1.0 mm foot-recess + 2.0 mm structural floor |
| Total body height | 20.0 mm | 18.0 socket + 2.0 mm base ramp height at edge |
| Base-to-top taper | Wider at base, narrower at top | Organic hull loft; see Outer Shell feature |
| Max build volume (X1C) | 256 × 256 × 256 mm | Printer spec |

**Tip-tuck note:** The 3.0 mm tuck figure is an estimate for this teardrop aspect ratio
(28.5 L × 24.4 W ≈ 1.17:1). The modeler must compute the actual tip-to-arc bridge
distance from the real teardrop profile at the chosen row pitch and confirm ≥ 1.2 mm.
If the tuck geometry yields a tighter bridge, increase row pitch until the bridge reaches
2.0 mm nominal. Report the verified pitch and bridge measurement as a SCAD comment.

## Features

### Teardrop Socket Array (× 6)

- **Purpose**: Retains each capsule upright by cradling its lower 18 mm of outer body.
  The capsule rests on the socket floor and stands ~51 mm proud of the rack top.
- **Profile**: Teardrop / D-shape matching the capsule cross-section. Long axis = 28.5 mm,
  narrow axis = 24.4 mm. The teardrop has a rounded back arc and a blunter pointed front.
  Model the pocket profile as the actual capsule teardrop silhouette + uniform 0.35 mm
  outward offset (sliding-fit clearance). A simplified stand-in (two-tangent-circles or
  stadium shape approximation) is acceptable ONLY if it produces a wall-to-wall gap of
  ≥ 0.35 mm everywhere around the capsule; note in the SCAD if approximated.
- **Depth**: 18.0 mm blind pocket (closed bottom).
- **Critical dimension**: Pocket long axis 28.5 mm ± 0.1 mm; narrow axis 24.4 mm ± 0.1 mm.
  These control fit — they must be parameterized for easy reprint-tuning.
- **Tip geometry**: The teardrop point is a narrow internal corner. At 18 mm depth with
  vertical walls this is printable. The tip angle follows the capsule silhouette; ensure
  tip radius ≥ 0.4 mm (one nozzle width) to avoid a single-extrusion line at the tip.
- **Alternating orientation (HARD REQUIREMENT)**: Even-indexed sockets (0, 2, 4) are 0°
  (pointed end in one direction); odd-indexed sockets (1, 3, 5) are rotated 180° (pointed
  end opposite). This tucks each pointed tip into the round-back gap of its neighbour for
  maximum packing density. Teardrop nesting is required — rectangular grid is not acceptable.
- **Either-end-up**: The pocket is symmetric along the capsule's height axis. No orientation
  cue needed; the user may drop the capsule in either end first.

### Top Lead-In Chamfer

- **Purpose**: Funnels a capsule into its socket one-handed without precise alignment.
- **Implementation**: Each socket mouth gets a chamfer (or fillet) around the full teardrop
  perimeter at the rim. Chamfer: 1.5 mm × 45° (removes 1.5 mm depth and 1.5 mm radially
  at the rim, producing a smooth funnel entry). A fillet of r = 1.5 mm is equally acceptable
  and preferred if the modeler can produce it cleanly; chamfer is the fallback.
- **Critical dimension**: Lead-in depth 1.5 mm ± 0.3 mm. Socket effective depth after
  chamfer: 18.0 − 1.5 = 16.5 mm gripping depth (still well above the minimum useful depth).
- **Printability**: The chamfer creates a 45° inward-sloping face at the top of each socket.
  At 45° this is at the printability limit — print without supports because the slope is
  exactly at the threshold and the socket walls below fully support it. Flag: if the modeler
  uses a fillet (convex curve) the overhang worsens past 45° at the fillet base; use a
  straight chamfer if fillet overhang cannot be kept ≤ 45°.

### Outer Shell — Organic Lofted Body

- **Purpose**: Structural body that spaces the sockets, provides rigidity, and gives the
  piece its sculptural form. Replaces the previous rectangular grid shell entirely.
- **Form language**: A smooth dune / mound hull. The body is widest and most rounded at the
  base, then draws in and conforms more tightly around the socket cluster as it rises to the
  top, where the socket mouths sit flush at the top surface.
- **Base footprint**: A smooth closed curve — a rounded, blobby/hull perimeter that outsets
  the nested socket cluster by approximately 6 mm uniformly (enough for ≥ 2.0 mm wall + a
  generous fillet radius). No straight edges. No sharp corners. The perimeter follows the
  organic envelope of the cluster.
- **Top cross-section**: Slightly tighter than the base, closely wrapping the socket mouths.
  The outset at the top is approximately 2.0–3.0 mm from the socket walls (enough for minimum
  wall thickness). The top face is flat, with socket mouths flush and the lead-in chamfers
  recessed just inside.
- **Transition**: The outer surface lofts fluidly from the broad base to the tighter top.
  This produces an inward-ramping outer wall — the angle of the ramp must stay ≤ 45° from
  vertical everywhere to avoid unsupported overhangs. With ~3–4 mm of inward taper over
  18 mm of height, the resulting wall angle ≈ 10–15° from vertical — well within threshold.
- **Modeling guidance (not prescriptive — leave method to modeler)**: The fluid ramp and
  curved envelope are well-suited to an OpenSCAD `hull()` of stacked 2D offset slices.
  Strategy: compute the rounded-offset envelope of the teardrop cluster at several Z heights
  (broad at Z=0, tight at Z=20), hull or linear_extrude between them, then subtract the 6
  teardrop socket bores and the lead-in chamfer cuts. Heavy `hull()` / offset operations
  raise render cost — use draft `$fn` (e.g., 32) during iteration, increase to 128+ for
  final delivery render (per project convention).
- **Wall spec**: Thinnest wall anywhere (inter-socket bridges, outer shell to nearest socket)
  ≥ 1.2 mm hard floor; 2.0 mm nominal target. The critical measurement is the thinnest
  solid bridge between two adjacent socket walls at the closest point in the nested layout.
  Modeler must verify and report this in a SCAD comment.
- **Height**: 20.0 mm total. The base is flat on the bed; socket walls reach the full height.
  The outer organic body also peaks at 20.0 mm (flush top surface).
- **Top surface**: Open at the top (sockets open upward). The top face is a single flat
  plane at Z = 20.0 mm with 6 teardrop openings and the 6 lead-in chamfers.
- **Bottom surface**: Flat, suitable for bed adhesion and the non-slip foot recesses.
- **Base edge fillets**: The transition from the bottom flat face to the organic side wall
  should be filleted or chamfered (r ≈ 1.5–2.0 mm) for a fully rounded, finished base
  appearance and to prevent sharp edges from scratching the drawer.

### Non-Slip Base

- **Purpose**: Prevents the rack from sliding in the drawer without fasteners.
- **Implementation**: Four circular recesses (dia 10 mm, depth 1.0 mm) on the underside,
  positioned near the cluster corners of the organic footprint, for self-adhesive silicone feet.
  Positions should follow the shape of the organic base — place feet near the four outermost
  extent points of the footprint (roughly ±X, ±Y extremes), not at rectangular corners.
- **Constraint**: Total floor thickness = 3.0 mm; foot recesses are 1.0 mm deep, leaving
  2.0 mm structural floor. Recess must not encroach on any socket floor.
- **Printability**: The 10 mm diameter × 1.0 mm deep recesses on the underside are
  printed face-down on the bed — they form small raised rings (the walls around the recesses
  are positive geometry from the bed perspective). No bridge concern.

### Layout — 3 × 2 Nested Teardrop Cluster

Six sockets in 3 columns × 2 rows with alternating 180° rotation:

```
Col:    0         1         2
Row 0: [0° ]    [180°]    [0° ]
Row 1: [180°]   [0° ]    [180°]
```

Center-to-center pitches (nominal):
- Column pitch (narrow-axis direction): 26.4 mm
- Row pitch (long-axis direction, nested): 27.5 mm

Cluster center extents: 2 × 26.4 mm = 52.8 mm wide; 1 × 27.5 mm = 27.5 mm deep.
Socket bounding box over the cluster: ~77 mm wide × ~56 mm deep.
Organic envelope footprint (approximate): ~89 mm × ~68 mm (blob, not rectangle).

**Orientation open item (non-blocking):** Which way the cluster's long axis runs relative
to the drawer (wide dimension front-to-back vs left-right) is the user's call once they
see the nested footprint. This is a post-model confirmation, not a spec blocker. The SCAD
should parameterize a global rotation so the user can reorient with one variable change.

## Material & Tolerances

- **Material**: PLA
- **Fit type**: Sliding fit — pocket = capsule body + 0.35 mm per side (0.70 mm diametric).
  Capsules drop in and lift out one-handed with no force required.
- **Default tolerance**: ±0.2 mm on non-critical dimensions.
- **Critical pocket dimensions**: ±0.1 mm (parameterized; easy to reprint at +0.15 mm
  if first print is too snug).
- **No press fits**: This is a drop-in holder. Nothing should be interference-fit.

## Constraints

- Build volume: 256 × 256 × 256 mm (Bambu X1C). Organic envelope (~89 × 68 × 20 mm) fits
  with large margin.
- Min wall: 1.2 mm (3 perimeters at 0.4 mm nozzle). Nominal walls are 2.0 mm.
  The critical constraint is the thinnest bridge between adjacent socket walls at the
  nested tip-to-arc interface — modeler must verify ≥ 1.2 mm and report the value.
- Min floor: 0.8 mm (4 layers at 0.2 mm). Nominal structural floor is 2.0 mm (3.0 mm total
  with foot recesses).
- Total height cap: 25 mm (drawer-friendly; 20 mm nominal).
- No fastener holes needed.
- Model must be manifold. Open sockets at the top are simply the top face of the model with
  teardrop cutouts — the mesh is closed at all exterior surfaces.

## Printability Pre-Screen

| Feature | Check | Status |
|---|---|---|
| Socket walls (interior) | Vertical — 0° overhang | PASS — no overhang inside pockets |
| Socket depth 18 mm | Wall height fully supported from floor | PASS |
| Teardrop tip (internal corner at pocket) | Narrow angle, vertical wall, 0.4 mm nozzle | FLAG (minor) — ensure tip radius ≥ 0.4 mm; not a print-failure risk |
| Top lead-in chamfer | 45° inward slope at socket rim | FLAG — exactly at overhang threshold; chamfer preferred over fillet (fillet exceeds 45° at base). No support needed if ≤ 45°. Modeler must verify angle. |
| Organic outer wall (inward taper) | ~3–4 mm inward over 18 mm height | PASS (estimated ~10–15° from vertical, well within 45° threshold). Modeler must verify the steepest point of the outer surface does not exceed 45° from vertical. |
| Thinnest inter-socket bridge | ≥ 1.2 mm required | FLAG — compute from actual teardrop profile at chosen row pitch and confirm. Nominal target 2.0 mm; hard floor 1.2 mm. |
| Base edge fillet | r ≈ 1.5–2.0 mm | PASS — fully supported; no overhang concern |
| Floor 3.0 mm | ≥ 0.8 mm (4 layers) | PASS |
| Foot recesses (underside) | 10 mm dia, 1.0 mm deep, printed face-down | PASS — no bridge; recesses form raised rings at bed layer |
| Overall footprint | ~89 × 68 mm organic blob | PASS — well within 256 × 256 mm plate |

No supports required inside sockets. Outer wall overhang requires verification by modeler
but is expected to be well within threshold. Single-orientation print (sockets up).
