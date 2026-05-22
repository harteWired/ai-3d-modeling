# Workout Dumbbell Concept 2 Requirements

## Design Intent

A clip-on cradle that mounts one rubber-coated dumbbell vertically on a treadmill's rectangular aluminum frame extrusion. Two units are printed (one per dumbbell); the design is a single symmetric part.

This is a structural redesign of the v3.4 dumbbell holder (`designs/workout-dumbbell-holder/`). v3.4 cantilevered the dumbbell 90 mm outboard of the rail face, imposing a sustained bending moment on the plug root — the dominant failure risk for CF-reinforced filaments, which have lower inter-layer toughness than unfilled materials. v4 eliminates this bending moment by moving the fork plate above the flange and tilting it 15°. The tilt converts the load path from cantilever-bending into compression: upper bell weight pushes down through the tilted plate, down through a curved strut, down through the flange top face, down into the rail cap. The plug still provides lateral restraint (shear only) but is no longer the structural fuse.

The 15° tilt also provides anti-walk retention: with the plate outboard edge higher, the shaft is held 15° from vertical with its top leaning inboard. The upper bell is preloaded against the inboard arc wall by gravity (horizontal component ≈ W × sin15° ≈ 0.26 × W). The dumbbell cannot vibrate or walk off the saddle without being physically lifted — matching the gravity-only retention philosophy of all previous versions.

## Print Orientation

Plug-vertical orientation is the baseline: plug axis = Z (printing direction), sleeve walls vertical, fork plate and strut above the flange. This keeps the cantilever-bending axis perpendicular to the now-eliminated bending moment direction. With v4's compression load path the print orientation is less critical than in v3.4, but plug-vertical is still recommended because the strut geometry (concave-up arc in the Y-Z plane) has no overhangs in this orientation.

Alternative cradle-flat orientation: fork plate face-down on bed, plug pointing up. The sleeve becomes tall vertical walls; the strut arc faces down and may need support depending on the arc angle at the outboard tangent. Print-reviewer to evaluate both orientations against the modeled geometry.

## Dimensions & Sources

| Dimension | Value | Source |
|---|---|---|
| Extrusion inner width (narrow) | 44.5 mm | User-measured |
| Extrusion inner width (wide) | 70.5 mm | User-measured |
| Extrusion outer width (narrow) | 51.0 mm | User-measured |
| Extrusion outer width (wide) | 76.5 mm | User-measured |
| Extrusion wall thickness | ~3.7 mm | User-measured |
| Extrusion outer corner radius | 6.0 mm | User-measured |
| Extrusion inner corner radius | < 3 mm (design uses 2.5 mm) | User-measured bound; 2.5 mm chosen conservatively |
| Plug clearance per side | 1.0 mm/side | User-stated; intentionally generous for CF dimensional variation |
| Plug outer dim — narrow axis | 42.5 mm | Derived: 44.5 − 2×1.0 |
| Plug outer dim — wide axis | 68.5 mm | Derived: 70.5 − 2×1.0 |
| Plug engagement depth | 30 mm | Retained from v3.4, user-confirmed |
| Flange thickness | 8 mm | Retained from v3.4, user-confirmed |
| Flange radial overhang past plug face | 10 mm all sides | Retained from v3.4, user-confirmed |
| Flange outer dim — narrow axis | 62.5 mm | Derived: 42.5 + 2×10 |
| Flange outer dim — wide axis | 88.5 mm | Derived: 68.5 + 2×10 |
| Sleeve clearance per side | 1.0 mm/side | Retained from v3.4 |
| Sleeve ID — wide axis | 78.5 mm | Derived: 76.5 + 2×1.0 |
| Sleeve ID — narrow axis | 53.0 mm | Derived: 51.0 + 2×1.0 |
| Sleeve OD — wide axis | 88.5 mm | Derived: matches flange OD wide |
| Sleeve OD — narrow axis | 62.5 mm | Derived: matches flange OD narrow |
| Sleeve wall — wide-axis side | 5.0 mm | Derived: (88.5 − 78.5)/2 |
| Sleeve wall — narrow-axis side | 4.75 mm | Derived: (62.5 − 53.0)/2 |
| Sleeve length below flange-front | 30 mm | User-confirmed (Q5 resolved); shortened from 48 mm in v3.4 — the 18 mm extension existed only for the v3.4 bottom buttress which is removed in v4 |
| Sleeve inner corner radius | 7 mm | = extrusion outer corner r (6) + clearance (1) |
| Sleeve −X wall | Removed | Retained from v3.1 — treadmill console clearance |
| Dumbbell shaft diameter | ~46 mm | User-measured |
| Dumbbell bell diameter | ~111 mm (r ≈ 55.5 mm) | User-measured |
| Saddle arc radius | 23 mm | Derived: shaft_diameter / 2 = 46 / 2 |
| Fork spread angle (included) | 60° | Retained from v3.4, user-confirmed |
| Fork spread angle (per arm) | 30° | Derived: 60° / 2 |
| Fork plate tilt | 15° from horizontal | User-locked |
| Fork plate inboard edge Z | 0 mm (flange-top) | User-confirmed (Q1 resolved: flush with flange top) |
| Saddle center Y | 54.5 mm | Derived: sleeve_od_narrow/2 + saddle_radius = 31.25 + 23 |
| Saddle center Z above flange-top | +6.23 mm | Derived: (54.5 − 31.25) × tan(15°) = 23.25 × 0.2679 |
| Tine tip Y | 97.5 mm | Derived: saddle_center_y + saddle_radius + tine_extension = 54.5 + 23 + 20 |
| Tine tip Z above flange-top | +17.75 mm | Derived: (97.5 − 31.25) × tan(15°) = 66.25 × 0.2679 |
| Tine extension past saddle center | 20 mm | Retained from v3.4 |
| Fork plate thickness | 12 mm normal to plate surface | Retained from v3.4 |
| Fork plate thickness in Z at root | ~11.59 mm | Derived: 12 × cos(15°) |
| Bell seat surface | Flat top | User-confirmed (Q2 resolved) |
| Fork plate X range | [−39.25, +44.25] mm | Retained from v3.4 post-recentering |
| Strut profile | Curved arc R = 9.0 mm | Computed — see strut geometry section |
| Estimated shaft length saddle → lower bell | ~120 mm | User-confirmed proceed with estimate (Q3 resolved); flag for modeler verification |
| Lower bell clearance (estimated) | ~57 mm clear of sleeve | Derived — see clearance check |

**Bounding box (locked):**

| Axis | Value | Math |
|---|---|---|
| X | 88.5 mm | plug_wide (68.5) + 2 × flange_overhang (10) — unchanged from v3.4 |
| Y | 128.75 mm ≈ 129 mm | sleeve_back (31.25) + tine_tip_y (97.5) |
| Z | ~56 mm | plug_depth (30) + flange (8) + plate_top_at_tine_tip (17.75) — plate top at tine-tip elevation is 17.75 mm above flange-top |

Z note: the plate bottom at the root (inboard edge) is at Z = −11.59 mm (inside the flange/sleeve zone — this is the strut's lower landing point, which sits on the flange outer +Y face at Z = 0). The overall part Z span from plug-back to highest point: 30 + 8 + 17.75 = 55.75 mm, rounded to 56 mm. Well inside X1C 256 mm build volume.

## Features

### Feature 1: Internal Plug

- **Purpose:** Anchors the holder inside the extrusion bore; provides lateral shear restraint. In v4 the plug no longer carries the dominant bending moment (that is now taken by the compression strut + flange bearing), but it is still the primary lateral stabilizer.
- **Critical dimensions:**
  - Outer cross-section: 42.5 mm × 68.5 mm rectangular with 2.5 mm corner radius
  - Engagement depth: 30 mm
  - Wall thickness: minimum 3.0 mm on all sides (CF minimum)
- **Mating interface:** Slides into extrusion ID 44.5 mm × 70.5 mm, inner corner r < 3 mm
  - Fit type: sliding/clearance (1 mm/side, 2 mm diametric gap)
  - Resulting gap: 1.0 mm on each face — easy insertion; some rattle; acceptable for gravity-held sliding fit
- **Load case (v4):** Plug carries shear (lateral force from the weight of the dumbbell pushing the holder sideways along the rail) and friction-based axial retention (gravity clamps the holder down; friction prevents it sliding along the rail axis). Bending moment at the plug root is eliminated in v4.
- **Printability note:** 30 mm tall rectangular section, no overhangs, no bridges. No flags.

### Feature 2: Seating Flange

- **Purpose:** Hard stop against the extrusion rim face; provides the bearing surface that receives the compressive load transferred down from the strut. In v4 the flange top face is the critical load-transfer datum — the compression strut lands here.
- **Critical dimensions:**
  - Thickness: 8 mm
  - Radial overhang past plug face: 10 mm all sides
  - Outer envelope: 62.5 mm × 88.5 mm, corner radius 7 mm
- **Mating interface:** Rests on extrusion outer face (51.0 × 76.5 mm, outer r = 6 mm). No mechanical attachment.
- **Load-bearing note:** The strut base lands on the flange top face at the sleeve outer +Y edge (Y = +31.25, Z = 0). The flange must transfer this compressive load into the extrusion rim face below. At 8 mm thickness and solid CF construction this is more than adequate.
- **Printability note:** Flat horizontal layer — no overhangs. No flags.

### Feature 3: External Sleeve (C-shape, −X open)

- **Purpose:** Wraps the rail's outer surface to provide a second engagement point — inside the rail (plug) and outside the rail (sleeve) in opposition. Stiffer than plug-only engagement. The sleeve outer +Y face is the vertical datum that the fork plate root and strut base land on.
- **Critical dimensions:**
  - Outer envelope: 88.5 mm × 62.5 mm (matches flange OD), corner radius 7 mm
  - Inner cavity: 78.5 mm × 53.0 mm (rail OD + 2 × 1 mm clearance), inner corner radius 7 mm
  - Wall thickness: 5.0 mm (wide axis), 4.75 mm (narrow axis)
  - Length below flange-front face: 30 mm (Z range: [−38, −8] in flange-top-datum convention)
  - −X wall: removed (console clearance cut, retained from v3.1). Sleeve is a C-shape open on −X.
- **Mating interface:** Slides over rail outer surface (51.0 × 76.5 mm, r = 6 mm). 1 mm/side clearance.
- **Printability note:** Sleeve walls vertical in plug-up orientation — no overhangs. C-shape open on −X eliminates the corner overhang on that side. No flags.

### Feature 4: Fork Plate (v4 — tilted, above flange)

- **Purpose:** Tilted plate above the flange that catches the upper bell and transfers load compressively down through the strut. The plate is 15° from horizontal (outboard/+Y edge higher), which both positions the shaft for gravity retention (anti-walk tilt) and converts the dumbbell weight into a compressive force on the strut.
- **Critical dimensions:**
  - Plate inboard edge: Y = +31.25 mm (flush with sleeve outer +Y face), Z = 0 (flush with flange-top face)
  - Plate tilt: 15° from horizontal, outboard edge higher
  - Saddle center: Y = +54.5 mm, Z = +6.23 mm above flange-top
  - Tine tips: Y = +97.5 mm, Z = +17.75 mm above flange-top
  - Plate thickness: 12 mm normal to plate surface (~11.59 mm in Z at the root)
  - Plate X range: [−39.25, +44.25] mm (83.5 mm total; −X cut for console clearance)
  - Saddle arc radius: 23 mm (conforming to shaft D 46 mm)
  - Fork spread angle: 60° included (30° per arm)
  - Top surface: flat (no dish); bell contacts plate at line contact
  - +Y end: open — shaft slides in laterally from the +Y direction to seat in the arc
- **Mating interface:** Upper bell (D 111 mm) rests on the tilted plate top surface. Line contact at bell equator. Gravity-only retention. Anti-walk preload: W × sin(15°) ≈ 0.26 W inboard.
- **Plate bottom at root (underside):** The plate underside at the inboard root is at Z = 0 − 12 × cos(15°) = −11.59 mm. This point is the upper tangent of the strut arc (point B in the strut geometry section). The plate underside at the root is therefore inside the flange+sleeve zone — the strut arc bridges this from the flange-top outer corner to the plate underside.
- **Printability note:** Plate underside at 15° from horizontal — within the 45° self-support limit (underside angle from horizontal = 15°, well inside the 45° limit). The open +Y end and the saddle arc (30° per arm off center) are within the self-support limit. No support required. No flags.

### Feature 5: Compression Strut (v4 — curved arc)

- **Purpose:** Transfers compressive load from the fork plate underside (inboard root) to the flange top face. In v4 this replaces the v3.4 top buttress + bottom buttress + ribs with a single upward-curving element. The strut is a concave-up circular arc (center above the arc) running from the flange outer +Y face (Z = 0) to the fork plate underside, landing tangentially on both surfaces.
- **Strut arc geometry (derived — see computation below):**
  - Arc radius: **R = 9.0 mm**
  - Arc center location: Y = 40.25 mm, Z = 0 (in the Y-Z plane, extruded across full plate X width)
  - **Tangent point A (flange-top landing):** Y = +31.25 mm, Z = 0. The arc is tangent to the sleeve outer +Y face (a vertical surface) at this point — the arc arrives vertically (+Z tangent direction). The strut merges flush with the top outer corner of the sleeve/flange +Y face.
  - **Tangent point B (plate underside landing):** Y ≈ +42.5 mm, Z ≈ −8.6 mm. The arc is tangent to the plate underside (which runs at 15° from horizontal) at this point. The tangent point is approximately 11.2 mm along the plate underside from the plate root (inboard edge). The arc arrives parallel to the plate surface — smooth merge, no kink.
  - Arc span: from A (top-of-flange corner) curving down and outboard to B (plate underside), sweeping approximately 75° of arc.
  - X extent: [−39.25, +44.25] mm — full fork plate X width. The strut is a full-width curved web, not two edge ribs.
- **Load case:** The strut carries the compressive component of the dumbbell weight transmitted through the tilted plate. For a 3 lb (13.3 N) dumbbell: compressive force ≈ W × cos(15°) ≈ 12.8 N. At R = 9 mm and full X width of 83.5 mm, the strut cross-section is highly overdetermined — no stress flag.
- **Printability note:** The strut arc curves from vertical (at A) to 15° from horizontal (at B), spanning approximately 75°. The outermost point of the arc's underside faces downward at approximately 15° below horizontal at B — within the 45° self-support limit. The strut prints without support in plug-vertical orientation. Flag for geometry analysis to verify the exact underside angle at the arc midpoint does not exceed 45°.

### Feature 6: Plug + Flange (unchanged from v3.4)

Already described above (Features 1 and 2). Restated here for completeness: the plug (42.5 × 68.5 mm, 30 mm deep, 2.5 mm corner r) and flange (8 mm thick, 10 mm overhang, 88.5 × 62.5 mm outer, 7 mm corner r) are dimensionally identical to v3.4. No changes.

## Strut Arc Geometry Computation

This section documents the derivation of the R = 9.0 mm strut arc so the modeler can replicate or verify it.

**Constraints:**
1. The arc must be tangent to the sleeve outer +Y face (vertical plane at Y = +31.25 mm) at flange-top (Z = 0). This requires the arc tangent at point A to be vertical — the arc center is therefore directly horizontal from A at the same Z.
2. The arc must be tangent to the fork plate underside at point B. The plate underside runs at 15° from horizontal (same angle as the plate itself). The arc center must be perpendicular to the plate surface at B, on the concave side (above the arc), i.e., in the direction 90° counterclockwise from the plate underside direction: (−sin 15°, +cos 15°) = (−0.2588, +0.9659) in (Y, Z).
3. The arc center is equidistant from both A and B (same radius).

**Solving for R:**

Let arc center = (Y_c, Z_c). From constraint 1: Z_c = 0 and Y_c = 31.25 + R.

The plate underside passes through the inboard root at (Y = 31.25, Z = −11.59) with direction vector (cos 15°, sin 15°) = (0.9659, 0.2588) in (Y, Z). Parametrically, B = (31.25 + t·cos15°, −11.59 + t·sin15°).

The perpendicular from center to B must have length R and direction (−sin15°, cos15°) from B toward center:

Center = B + R·(−sin15°, cos15°)

Setting center Y-component: 31.25 + R = (31.25 + t·cos15°) − R·sin15°

This gives: t = R(1 + sin15°)/cos15°

Setting center Z-component: 0 = (−11.59 + t·sin15°) + R·cos15°

Substituting t: 0 = −11.59 + R(1+sin15°)sin15°/cos15° + R·cos15°

Collecting: 11.59 = R·(1 + sin15°)/cos15°

With sin15° = 0.2588, cos15° = 0.9659:

R = 11.59 × cos15° / (1 + sin15°) = 11.59 × 0.9659 / 1.2588 = 11.20 / 1.2588 = **8.90 mm**

Rounded to **R = 9.0 mm** (clean value; rounding error < 1%).

**Resulting coordinates (R = 9.0 mm):**

- Arc center: (Y = 40.25, Z = 0)
- Tangent point A: (Y = 31.25, Z = 0) — at the sleeve +Y outer top corner
- t = 9.0 × (1 + 0.2588)/0.9659 = 9.0 × 1.3034 = 11.73 mm
- Tangent point B: Y = 31.25 + 11.73 × 0.9659 = **42.58 mm**, Z = −11.59 + 11.73 × 0.2588 = **−8.55 mm**

**Arc summary:**

| Parameter | Value |
|---|---|
| Arc radius | 9.0 mm |
| Center (Y, Z) | (40.25, 0) |
| Tangent point A — flange corner | (Y = 31.25, Z = 0), tangent direction: +Z (vertical) |
| Tangent point B — plate underside | (Y ≈ 42.6, Z ≈ −8.6), tangent direction: 15° from horizontal (parallel to plate) |
| Arc sweep angle | ≈ 75° (from vertical at A to 15°-from-horizontal at B) |
| X extent | [−39.25, +44.25] mm — full fork plate width |
| Profile | Concave-up (center above the arc), center at Z = 0 level |

**Modeling note for Fusion:** Create a 2D sketch in the Y-Z plane, draw a circular arc of R = 9 mm centered at (40.25, 0) with endpoints at A and B. Verify tangency to both the vertical sleeve face and the tilted plate underside face. Extrude across X = [−39.25, +44.25].

## Lower Bell Clearance Check

With fork plate launch Z = 0 and saddle at (Y = 54.5, Z = +6.23 mm above flange-top), the shaft runs downward-outboard at 15° from vertical: direction vector (Y, Z) = (+sin15°, −cos15°) = (+0.2588, −0.9659).

Using the estimated shaft length from saddle center to lower bell inner face = 120 mm (user-confirmed to proceed with estimate; flag for modeler to verify against actual dumbbell):

- Lower bell inner face: Y = 54.5 + 120 × 0.2588 = **85.6 mm**, Z = 6.23 − 120 × 0.9659 = **−109.5 mm**
- Lower bell outer face: Y = 85.6 + 30 × 0.2588 = **93.4 mm** (assuming 30 mm bell axial height)
- Lower bell outermost radial extent: 93.4 + 55.5 = **148.9 mm** outboard
- Sleeve outer +Y face: Y = +31.25 mm
- Clearance: 148.9 − 31.25 = **117.6 mm** — no interference

The shaft path from the saddle down past the sleeve exterior to the lower bell does not intersect the sleeve or plug body (the fork plate is above the flange; the shaft hangs in free air from the saddle downward past the sleeve's lower extent). The shaft exits the sleeve zone at Z ≈ −38 mm (bottom of sleeve at Z = −38 mm from flange-top), at which point it has moved approximately (38 − 6.23)/0.9659 × 0.2588 = 8.5 mm outboard from the saddle Y position, placing it at Y ≈ 63 mm — well clear of the sleeve outer face (Y = 31.25 mm). No intersection.

**Flag for modeler:** verify geometrically in Fusion that the shaft axis line (parameterized above) does not intersect any solid body. Especially check near Z = −8 mm (bottom of flange) and Z = −38 mm (bottom of sleeve).

## Material & Tolerances

- **Material:** Carbon-fiber-reinforced filament (CF-PLA, CF-PA, or CF-PETG) on the Bambu Lab X1C.
- **CF tolerance note:** CF-reinforced filaments shrink less than unfilled PLA. The project's standard tolerance table (press fit −0.15, clearance +0.25, sliding +0.35 mm/side) is calibrated for PLA. For CF materials, clearances may run tight by 0.05–0.15 mm. The 1 mm/side plug and sleeve clearances are intentionally generous to absorb this variation.
- **CF brittleness:** Minimum wall thickness for all structural features: 3.0 mm (vs. 1.2 mm PLA standard). Inter-layer adhesion is lower in CF — the v4 compression load path is specifically chosen to minimize bending stress on the layer interfaces.
- **Fit types:**
  - Plug-to-extrusion: sliding/clearance, 1 mm/side (user-specified)
  - Sleeve-to-extrusion: sliding/clearance, 1 mm/side (user-specified)
  - Shaft-in-saddle: gravity cradle, conforming arc contact — no mechanical fit tolerance
  - Bell-on-plate: flat plate, gravity bearing — no fit tolerance

## Constraints

- Build volume: 256 × 256 × 256 mm (Bambu X1C). Bounding box ~88.5 × 129 × 56 mm — well within limits.
- Nozzle: 0.4 mm. Minimum CF wall: 3.0 mm (≥ 7 perimeters).
- Single-piece part, no assembly, no fasteners, no inserts.
- Gravity-held mount. Anti-walk retention by geometry (15° tilt). No straps, clamps, adhesive, or setscrews.
- Modeling backend: Fusion 360 (new .f3d — do not reuse or branch from v3.4 Fusion file).

## Printability Pre-Screen

| Feature | Issue | Severity | Status |
|---|---|---|---|
| Fork plate underside (15° from horizontal) | At 15° from horizontal, the underside is well within the 45° self-support limit | Cleared | No support needed |
| Saddle arc tine inner faces (30° per arm) | 30° off the saddle axis — within 45° self-support limit | Cleared | No support needed |
| Strut arc underside | Concave-up arc spans ~75°; the midpoint of the arc underside descends partway. The tangent at midpoint (~37.5° from vertical) is 52.5° from horizontal, which is within the 45° self-support limit from horizontal... but note the check: at the arc midpoint the underside faces at ~52° below horizontal — borderline. | Medium | Flag for geometry analysis. In plug-vertical orientation the outermost arc angle should be checked. Geometry analysis must confirm no unsupported overhang exceeds 45°. |
| Shaft path through part | Shaft axis line from saddle downward must not intersect any solid. Clearance check above shows comfortable margins but geometry must be verified in Fusion. | Medium | Flag for modeler |
| CF brittleness + load path | v4 compression load path is specifically designed to minimize inter-layer bending stress. Geometry analysis should verify that wall cross-sections at the strut-to-flange and strut-to-plate junctions are adequate for CF. | Medium | Flag for geometry analysis |
| Print orientation | Plug-vertical is recommended baseline. Print-reviewer to re-evaluate once Fusion model is complete. | Low | Review at print stage |

---

## v2 Amendments (2026-05-10)

After v1 was modeled and inspected, we iterated several rounds of tweaks in Fusion. The iteration cumulatively broke the geometry; this section locks down the **intended** v2 refinements (the design intent that came out of the iteration) and explicitly lists the moves that were tried and abandoned. The rebuild starts from v1 and applies ONLY what's in this section.

### v2-A: Plate-to-cap transition — swept organic loft (replaces v1's strut)

**Why:** v1's strut (R=9.53 mm curved web, full plate X-width but only ~12 mm of YZ extent) reads as a discrete pin-shaped feature stuck on the cap. The user wants a continuous sculpted transition where the cap appears to flow into the underside of the plate, not connect via a separate part.

**What we rip out:** the v1 R=9.53 mm strut entirely.

**What replaces it:** a lofted body that smoothly connects the sleeve+flange outer +Y face to the underside of the plate. Constraints:

- **Bottom boundary:** sleeve+flange outer +Y face — vertical line at Y = +31.25 mm, Z from −38 mm (sleeve bottom) up to 0 mm (flange top). Loft surface is tangent to this vertical face (so the loft "rises out of" the sleeve, not glued to it).
- **Top boundary:** plate underside line — tilted line from (Y = 34.36, Z = −11.59) at the plate inboard root to (Y = 87.21, Z = +2.57) at the plate outboard tine. Loft surface is tangent to the plate underside (15° slope) at this line.
- **Cross-section in plate-X:** the loft's "depth" (how far the surface bulges out away from the sleeve+flange face) **varies across plate X**. At plate centerline (X = 0, where the shaft and saddle U live), the loft pulls back to leave a shaft passage. At the plate ±X edges (where the tines sit cantilevered), the loft extends out further to provide structural support.
- **Saddle U clearance:** the loft must NOT block the saddle U through-slot. The shaft passes through the plate via the U slot and continues below the plate; the loft body must have a cut-out (or its varying X-cross-section must naturally narrow) so the shaft has clearance at saddle X.
- **Single body, watertight.** Joined into the main holder body.

**Implementation note for the modeler:** the most straightforward way is to loft across three (or more) profiles in YZ:
- At X = −39.25 mm (−X plate edge): a full closed profile bounded by the sleeve+flange face (vertical), plate underside (tilted), and an outer arc R ≈ 33 mm tangent to both.
- At X = 0 mm (saddle center): a minimal closed profile (or no profile at all — degenerate slice) so the loft surface pulls in tight at the shaft passage.
- At X = +44.25 mm (+X plate edge): same as −X profile, mirrored.

Then loft between these three profiles. The resulting body has wide tine support at the plate edges and a "scooped" inboard region at the saddle where the shaft passes. If the X=0 degenerate slice causes Fusion to fail the loft, fall back to a small (e.g., 3–5 mm wide) profile at X=0 and then cut a shaft-axis cylinder (R=23 along plate-X direction) through the body to clear the shaft passage.

### v2-B: Saddle U entry lead-in chamfer — lateral insertion from the front

**Use case:** User stands at +Y (the outboard "front" of the holder). User picks up the dumbbell with shaft axis along plate-X (left-right). User brings the dumbbell in from the front and slides the shaft into the saddle U from the +Y direction (shaft axis stays plate-X; shaft AXIS POSITION moves in −plate-Y direction inward until the shaft seats in the arc).

**Chamfer locations (all R = 1.0 mm):**

1. **Long +Y outboard top edge of the plate** — the single horizontal edge at plate +Y outboard, plate-top side. Post-rotation: world Y ≈ 84.10 mm, world Z ≈ 14.16 mm, X spanning the plate range. This is the main "ramp" the shaft slides over.
2. **+X arm exit corner** — at the plate +X / +Y outboard corner where the +X arm wall meets the plate +X face. Post-rotation: world (X = +44.25, Y = 84.10, Z = 14.16). Chamfer the local edges at this corner.
3. **−X arm exit point** — on the plate −X edge segment at world (X = −39.25, Y = 75.75, Z = 11.92) — where the −X arm exits through the plate −X face before reaching the +Y outboard edge.

**Modeler best effort:** if a single chamfer feature on all edges fails (Fusion's chamfer is fussy at tight vertices), fall back to per-edge chamfers. Per-edge failures are OK on the side corners — they're nice-to-have. The long +Y outboard top edge is the most important and most likely to succeed.

### v2-C: Things explicitly NOT to do (lessons learned)

- **DO NOT add a full-width "underside fill" body** spanning the entire plate X range from sleeve up to plate underside with a *constant* X-cross-section. It closes off the saddle U from below, blocking the shaft passage. (The v2-A swept loft IS allowed because its cross-section varies in X to leave room for the shaft at saddle center.)
- **DO NOT add a cylindrical bore perpendicular to the plate** to "carve out shaft clearance." The saddle U-slot geometry already provides plate-perpendicular shaft clearance. The shaft axis is along plate-X, not plate-Z, so any clearance cut should be along plate-X.
- **DO NOT redo the rectangular flange** as a separate lofted body. The flange stays as v1 spec (Z=−8 to 0, 88.5×62.5 mm at world origin, R=7 corners). The "flange grows out of the fork" feeling now comes from the v2-A loft, not from reshaping the flange.
- **DO NOT shift the flange** off the rail centerline.

### v2-D: What stays exactly as v1

- Plug + flange + sleeve cap: dimensions, position, corner radii — unchanged.
- Fork plate: position, tilt, X range (centered at X = +2.5 from −39.25 to +44.25), thickness, saddle U cut (arc R=23 + arms at 60° spread, exit through plate ±X edges).

### v2-E: Target dimensions and quality

- Volume target: 200 ± 20 cm³ (v1 was 182 cm³; the loft adds material at the tine edges that v1 doesn't have).
- Bbox: 88.5 × 118.46 × 52.16 mm (same as v1 — loft stays within the existing Y/Z envelope).
- Single watertight body. Modeler verifies with `trimesh.is_watertight` after export.

### v2-F: Shaft orientation note (for clarity going forward)

The dumbbell shaft is held with its axis along **plate-Z** (perpendicular to the fork plate face). The plate is tilted 15° from horizontal about the plate-X axis, so plate-Z is tilted 15° from vertical-world-Z — the shaft leans outboard at the bottom. Bells sit at the ±plate-Z ends of the shaft (one bell above the plate, one bell below, both along the shaft direction).

The shaft passes *through* the plate via the saddle U slot. Its cross-section in plate-XY (the plate's plane) is a circle of R = 23 mm.

Loading procedure:

1. User stands at +plate-Y (the outboard "front" of the holder, away from the treadmill console).
2. User picks up the dumbbell — shaft is held at ~15° from vertical, axis along plate-Z direction.
3. User brings the dumbbell into the holder from the +Y direction (the shaft moves in −plate-Y direction).
4. The shaft's circular cross-section enters the U slot at the +Y outboard opening (the slot is wide here — full plate width at plate-Y = 54.71 mm).
5. User slides the dumbbell inward until the shaft cross-section seats in the saddle arc — shaft axis ends up at plate-Y = 24.07 mm, shaft surface contacting the arc.
6. Gravity preloads the upper bell against the inboard saddle arc wall via the 15° tilt (W × sin15° ≈ 0.26 W horizontal component, inboard).

**Why the lead-in chamfer is at +Y outboard:** during the lateral slide-in, the shaft's leading edge crosses the plate's +Y outboard face and the slot's interior walls (the +X arm wall and the −X arm wall) as it moves inward. Chamfering the top edge at the plate +Y outboard face and the corners where the arm walls meet the plate ±X faces softens those crossings.
