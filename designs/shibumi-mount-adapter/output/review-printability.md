# Printability Review: shibumi-mount-adapter

## Data Sources
- Geometry report: NO (geometry-report.json not present)
- Slicer report: NO (slicer-report.json not present)
- Fallback to SCAD source: YES (primary analysis from shibumi-mount-adapter.scad + modeling-report.json)

---

## Print Orientation

### Modeler's suggested orientation (Orientation A — backing on bed)
Bed face: backing plate bottom (design z=-2.5). Socket opening faces up (+Z). Print-Z = design +Z.

### This review's recommended orientation (Orientation B — arch end on bed)
Bed face: closed arch end (+Y face, the far end of the socket). Long axis vertical. Socket mouth faces UP. Print-Z = design +Y.

**Reasoning and validation are the core of this review. See Step 3.**

---

## Feature Stack (bed → top)

### Orientation A (backing on bed — the modeler's suggestion):
1. Backing plate (print-z: 0.0–2.5 mm)
2. Socket floor + floor rails (print-z: 2.5–5.5 mm)
3. Socket walls lower zone (print-z: 2.5–9.5 mm)
4. Capture lips — overhang zone (print-z: 9.5–12.5 mm)

### Orientation B (arch end on bed — this review's recommendation):
1. Arch end wall cross-section (print-z: 0.0 — first layers)
2. Full socket walls + backing plate strip + floor rails, growing upward (print-z: 0 → 40.1 mm)
3. Mouth opening emerges at print-z = 40.1 mm (open top — no bridging)

Note: Bbox in Orientation B = 28.2 (X) × 12.5 (Y) × 40.1 (Z print). Well within 256 mm build height.

---

## Transition Checks

### Step 3 — Manual arithmetic from SCAD source (no geometry report)

#### Transition 1 (Orientation A): Socket walls → capture lips at design z=7.0

**Geometry:**
- Below z=7: cavity_x = 21.2 mm (open cavity, inner wall at x=±10.6)
- At z=7: lips begin — inner face steps INWARD by 2.0 mm each side
- New inner opening: lip_inner_x = 21.2 - 2×2.0 = 17.2 mm

**Overhang calculation:**
- Horizontal step: 2.0 mm inward (per side)
- Vertical rise for this step: 0 mm (it's an instantaneous step at one layer)
- Overhang angle: 90° (horizontal ledge, perpendicular to build axis)
- Limit: 45°

**Result: FAIL for Orientation A.**

The lip underside is a 2 mm wide, 90°-overhang horizontal ledge facing downward into the cavity. It exceeds the 45° limit. However, the unsupported span is only 2 mm (each side, cantilevered from the wall), which is well within the 10 mm bridge limit. In practice on a Bambu X1C with PLA, a 2 mm bridge will print with minor sag but no collapse. The slicer will likely bridge this without adding support. The printed surface quality on the lip underside will be degraded (layer lines may sag 0.1–0.3 mm), which has functional consequences for the fit since the cleat back face seats against this surface.

**Conflict flag:** The lip underside is a functional seating surface (it contacts the cleat back face). Sagging degrades the capture gap geometry. A chamfered lip underside would fix the printability but changes the capture geometry. See Conflicts section.

#### Transition 2 (Orientation A): Arch end wall → capture lip at design z=7.0

Same analysis as Transition 1. The arch (+Y) end wall carries the same inward lip. Same 90° horizontal ledge, 2 mm span, same result.

**Result: FAIL for Orientation A** (same reasoning and same caveat apply).

---

### Orientation B analysis — does rotating to arch-end-down solve it?

**YES. The lip overhang is eliminated entirely.**

In Orientation B (arch end on bed, mouth up), the design's Y axis becomes print-Z. The design's Z axis (socket depth direction) becomes horizontal. The lip zone (design z=7–10, the inward 2 mm shelf on the long walls) is now a purely vertical feature: it runs along the full print-Z height (Y axis), and in the horizontal cross-section it is simply 2 mm of extra wall thickness on the inner face. No layer grows horizontally past a previous layer for the lips. The slicer sees the lip as a thicker region of the wall cross-section, printed solid from bed to top.

**New features introduced by Orientation B and their overhang status:**

**New check B-1: Arch end wall on bed (print-z = 0)**
The arch end is the closed +Y end of the socket. Its cross-section is the outer rectangle (28.2 × 12.5 mm) minus the inner cavity profile (21.2 wide × 10 mm tall for the socket) minus the wall areas. The arch end has no hole in it — the mouth opening is on the opposite face. The arch end face is solid except for the inner recesses that form the socket geometry cross-section. This face prints as the first layers: a closed frame shape (outer wall + floor cross-section). Solid, well-supported.
**PASS.**

**New check B-2: Floor rails in Orientation B**
Design space: rails run from rail_y_near (-13.5 mm from center) to rail_y_far (+16.5 mm from center). In Orientation B, the Y axis is print-Z, so the rails grow vertically from print-z=0 (arch end) upward. The rail cross-section in design X-Z is: 2.15 mm wide (X) × 3 mm tall (Z, now horizontal depth). In Orientation B, the rails are vertical rectangular pillars, 2.15 mm × 3 mm cross-section, growing to full height. Wall thickness 2.15 mm is just at the 1.2 mm minimum (3 perimeters = 1.2 mm; 2.15 mm = ~5 perimeters). PASS on wall thickness.

The rail BRIDGE at the far (+Y) end: in design space, this joins the two rails at rail_y_far. In Orientation B, this bridge is at the BOTTOM of the print (arch end), and is supported by the arch end wall. No unsupported bridging.
**PASS.**

**New check B-3: Socket floor in Orientation B**
The socket floor (design z=0) is now a vertical face in Orientation B (it faces horizontally, perpendicular to print-Z). It's just a planar face on the side of the part — no bridging, no overhang.
**PASS.**

**New check B-4: Backing plate in Orientation B**
The backing plate (design z = -2.5 to 0, extending the full 28.2 × 40.1 footprint) becomes a vertical slab 2.5 mm thick, running the full 40.1 mm (print-Z height). In Orientation B, the backing plate and the socket outer walls form a continuous vertical profile. No overhang — the backing plate simply extends 2.5 mm "outward" (in design -Z direction, now horizontal). PASS.

**New check B-5: Mouth opening at print-Z top**
The mouth (-Y face) is at the top of the print in Orientation B. It is an open slot — the inner cavity is exposed at the top. No bridging required. The top of the print is an open profile with walls on three sides (two long sides + backing plate) and open on the fourth (mouth). The lip opening at the very top is 17.2 mm wide. No bridging.
**PASS.**

**New check B-6: Wall-to-lip transition in Orientation B (cross-section change)**
From design +Y = 0 (mid-point) up to the mouth, the inner cavity cross-section changes from the lipped zone (17.2 mm wide opening at design z=7–10) to the un-lipped zone (21.2 mm wide at design z=0–7). In Orientation B, since the lips run the full length of the socket (design Y direction = print-Z direction), this is NOT a transition in print-Z — the lips are present at every layer from print-z=0 to print-z=40.1. Actually, looking at the SCAD more carefully: the lips are modeled as a zone that is extruded over lip_zone_height in design Z — but in Orientation B, design Z is horizontal, not vertical. So the lip (a 2 mm shelf in design Z) is a horizontal (in Orientation B) cross-sectional feature that appears at every print layer equally. No transition in print-Z.
**PASS.**

**Summary of Orientation B overhang result:** No overhangs detected. All transitions are either supported-from-below, continuous walls, or open ends. Orientation B eliminates the only structural overhang present in Orientation A.

---

## Tips & Extremities

### Floor rail tips (near the mouth, in Orientation A / near the top in Orientation B)
In design space, the rails stop short of the mouth at rail_y_near = -cavity_y/2 + 3 = -13.5 mm from center, i.e., 3 mm from the inner mouth edge. The rail tips are free-standing: 2.15 mm × 3 mm cross-section, printed as a column.

In Orientation B, the rail tips are at the TOP of the print (near the mouth). The top layers of the rail columns will be free-standing tips. At 2.15 × 3 mm, this is a small but adequate area — not a thin spike. The rail_corner_r = 0.6 mm rounding reduces stress concentration. The rail height (3 mm in design Z = 3 mm horizontal depth in Orientation B) is supported by the socket floor wall at every layer.
**PASS** — but the rail tip surface quality may be slightly rougher at the very top due to small cross-section. Not functionally critical.

### Lip inner edge (at the top of Orientation A / throughout in Orientation B)
In Orientation A, the lip inner edge (top of the lip zone at design z=10) is the very last printed feature. In Orientation B the lip is throughout and not a tip.

### Backing plate corners
Rounded (r=3 mm). No sharp tips. PASS.

### Arch end wall inner corner radius
cavity_corner_r = 2.0 mm on the inner cavity corners. At normal resolution this is fine. PASS.

---

## Horizontal Spans

No geometry report or slicer report available. Manual identification from SCAD:

| Span | Location (design) | Length | Orientation A result | Orientation B result |
|---|---|---|---|---|
| Lip underside — left side | design z=7, inner left wall | 2.0 mm | PASS (short bridge, degrades surface) | N/A (vertical in B) |
| Lip underside — right side | design z=7, inner right wall | 2.0 mm | PASS (short bridge, degrades surface) | N/A (vertical in B) |
| Lip underside — arch end | design z=7, inner arch end | 2.0 mm | PASS (short bridge, degrades surface) | N/A (vertical in B) |
| Rail bridge (U bottom) | design z=0–3, Y far end | 8.2 mm (central slot) | PASS (8.2 < 10 mm) | PASS (supported by arch end wall) |
| Arch end wall top (if printed mouth-down) | n/a | n/a | n/a | n/a |

**Rail bridge in Orientation A:** The central_slot = 8.2 mm bridge at rail_y_far is a horizontal span of 8.2 mm at design z=0–3. This prints at print-z = 2.5–5.5 mm (after the backing plate). The bridge is at the CLOSED end of the socket, where the arch end wall provides side support. 8.2 mm < 10 mm limit.
**PASS — but borderline (82% of limit).** On the Bambu X1C, 8.2 mm PLA bridges typically print with minor surface sag on the underside. This bridge is the FLOOR of the socket — not a seating surface that contacts the cleat (the cleat rides on top of the rails, not under them), so surface sag here does not affect fit. PASS with note.

**Classification per avoidable bridge policy:**
- Lip underside bridges (2 mm, Orientation A): functionally required (the lip is the capture feature). Not avoidable without design change. PASS (functional) — but Orientation B makes them moot.
- Rail bridge (8.2 mm): functionally required (the inverted-U tongue structure needs the bridge to be a closed U). Not avoidable without losing the inverted-U geometry. PASS (functional).

---

## Mating Clearances

| Feature | Socket dim | Cleat dim | Gap | Role | Result |
|---|---|---|---|---|---|
| Cavity width (X, short axis) | 21.2 mm | — | — | Cleat slides along Y, not X-constrained | N/A |
| Socket depth under lip (Z) | 7.0 mm | rail 3.0 + blade 4.02 = 7.02 mm | -0.02 mm | Blade must fit between rail top and lip underside | FAIL — zero clearance |
| Lip opening width (X) | 17.2 mm | ~27.6 mm (long axis of cleat, aligned with Y) | — | Cleat width runs along Y axis, not constrained by lip X | N/A |
| Socket length (Y inner) | 33.0 mm | 27.6 mm (cleat width) | +5.4 mm | Cleat slides in lengthwise; must fit within cavity length | PASS |

### Critical finding: Vertical clearance is essentially zero

The blade rides on rails at height Z=3 mm. Blade thickness = 4.02 mm. Blade top face = Z = 7.02 mm. Lip underside = Z = 7.0 mm. **Designed-in clearance = -0.02 mm (nominal interference).**

The modeler's spec.json notes: "capture check: rail height 3 + blade 4.02 = 7.02 ~= socket depth 7 (blade back face meets lip underside)" and treats this as intentional — a zero-clearance/light-interference fit matching the original's soft-material snap. For a rigid PLA part, this zero clearance means:

1. **The cleat will not slide in unless something deflects.** PLA at these wall thicknesses (3.5 mm) is essentially rigid. There is no compliant snap behavior.
2. **Print shrinkage** (PLA typically 0.1–0.3% linear) will slightly reduce the socket depth, making the interference worse.
3. **Lip underside sag** in Orientation A (0.1–0.3 mm) would ADD material downward, further reducing clearance.

For the Phase 1 fit test, this means the cleat likely will NOT slide in cleanly. This is expected behavior for v1 (nominal repro) — the open item in spec.json is to tune an internal taper later. However, the reviewer recommends adding at least 0.1–0.2 mm clearance (raise the lip bottom by 0.1–0.2 mm or lower the rail by 0.1–0.2 mm) before printing, so the fit test is informative rather than a hard stop.

If printed at strict nominal, the only way the cleat enters is if the lips deflect laterally (unlikely in PLA) or if the cleat is chamfered to force it past the lips. The test print will still validate the XY dimensions and overall fit feel.

---

## Slicer Validation

No slicer report available. N/A.

---

## Conflicts

### Conflict 1: Lip underside is a functional seating surface AND an overhang

**The fix:** Chamfer the lip underside at 45° (e.g., from wall inner face at z=7, ramp to the full 2 mm overhang by z=9, leaving 1 mm solid lip at z=9–10).
**What it affects:** The chamfer changes the lip from a horizontal shelf to a ramped catch. The cleat back face would then seat against a 45° face instead of a flat horizontal one. For a capture socket, the chamfer actually HELPS insertion (acts as a lead-in ramp) but reduces the positive Z-locking (a flat shelf provides a hard stop; a ramp lets the cleat walk out more easily).
**Trade-off:** Lead-in vs. positive retention. The original molded part uses a flexible flat lip (both lead-in and positive retention via flex). A rigid PLA part with a flat lip has no flex — so retention depends entirely on friction from the zero-clearance fit. A chamfered lip in rigid PLA might actually function better since the ramp provides a small wedging grip without requiring compliance.
**User decision required.** This review does not modify the model.

### Conflict 2: Zero vertical clearance makes v1 a hard-stop rather than a fit test

**The fix:** Increase rail_height by 0.1–0.2 mm OR decrease lip_bottom_z by the same amount to create 0.1–0.2 mm of clearance. Or explicitly add a tolerance offset to the socket depth.
**What it affects:** Changes the vertical capture gap from the nominal reproduction of the original. Since all Z values are estimated from photo scaling (not calipered), a small adjustment is well within measurement uncertainty.
**Trade-off:** A small clearance addition makes the fit test informative (blade slides in, you can feel the snap and retention) rather than a guaranteed jam. Without it, the Phase 1 test may produce only negative data ("it doesn't fit") with no insight into the XY geometry fit.
**Recommendation:** Add 0.2 mm clearance (bring rail_height to 2.8 mm or lip_bottom_z to 7.2 mm) before printing the fit test. This is within the uncertainty of the photo-scaled Z estimates.
**User decision required.** This review does not modify the model.

---

## Summary

- Data quality: SCAD source + modeling report (no mesh geometry report, no slicer report)
- Total transitions checked: 6 (3 in Orientation A, 3 new in Orientation B)
- PASS: 4
- FAIL: 2 (lip overhangs in Orientation A — eliminated by Orientation B)
- Slicer agreement: N/A (no slicer report)
- Conflicts requiring user decision: 2
- Print verdict: **PASS-WITH-CONDITIONS** (Orientation B eliminates all overhangs; zero clearance is a fit-test risk)

---

## Print Orientation Recommendation

**Use Orientation B: arch end (-Y closed end) on bed, mouth opening facing up.**

This is a 90° rotation from the modeler's suggested orientation (which had backing-plate on bed).

```
Bed → [arch end wall] → walls+rails grow vertically → [mouth open at top]
```

- Lips print as vertical wall features — no overhang, no support needed
- All surfaces print clean
- Rail bridge at the arch end is at the very first layers, fully supported
- Footprint on bed: 28.2 × 12.5 mm = 352 mm² — use a BRIM (5 mm recommended) to ensure adhesion

**Does Orientation B introduce any new unsupported overhangs?** No. Every feature in Orientation B is either a continuous vertical extrusion or is at the arch end (bed level, fully supported). Confirmed PASS on all 5 Orientation B checks above.

---

## Test Print Recommendations

### Feature 1: Vertical clearance (socket depth vs. rail height + blade thickness)
**Risk:** Nominal zero clearance (-0.02 mm) means the cleat will not slide in without modification. The fit test produces only negative data.
**Recommendation:** Before printing, decide whether to add 0.2 mm clearance (modify rail_height or lip_bottom_z). If printing strict nominal to validate the geometry, accept that the slide-on fit will be tight or impossible — but the XY plan dimensions will be confirmed.
**Suggest:** Print one nominal copy (for dimension validation) and one copy with +0.2 mm clearance (for fit validation). Two prints back-to-back since the part is small.

### Feature 2: Rail bridge (8.2 mm span)
**Risk:** 8.2 mm is 82% of the bridge limit. In Orientation B this bridge is at the bed end, fully supported. No test print issue — but if orientation A were used, this would be the second concern.
**Risk level:** LOW in Orientation B.
**Recommendation:** No separate test needed; it will be validated on the main fit-test print.

### Feature 3: Rail wall thickness (2.15 mm)
**Risk:** Near minimum (MIN_WALL = 1.2 mm; 2.15 mm = ~5 perimeters). The rails are thin and tall (40 mm in Orientation B). At 0.4 mm nozzle / 3 perimeters minimum they are structurally adequate, but the 5-perimeter cross-section leaves little room for mismatch.
**Risk level:** MEDIUM.
**Recommendation:** Print with 4+ perimeters (walls) to ensure the rails are solid. Consider 0.2 mm layer height for dimensional accuracy on these features.

### Feature 4: Brim adhesion (Orientation B footprint)
**Risk:** 28.2 × 12.5 mm footprint is small. At 40.1 mm tall in print-Z, the aspect ratio is 3.2:1. May wobble or peel without a brim.
**Recommendation:** 5 mm brim, 3–4 brim loops. Remove brim carefully — brim on the arch end face could slightly affect fit of the arch end wall if it's tight.

---

## Print Settings for a Valid Fit Test

These settings are optimized for dimensional accuracy on a Bambu X1C printing PLA:

| Setting | Value | Reason |
|---|---|---|
| Layer height | 0.2 mm | Standard; good balance of resolution vs. speed. Do NOT use 0.28 mm — the socket depth is 7.0 mm and layer resolution matters for the capture gap. |
| Perimeters (walls) | 4 | One extra perimeter beyond the 3-perimeter minimum. The rail cross-section (2.15 mm) fills ~5 perimeters; the socket walls (3.5 mm) fill ~8. Ensures rail geometry is fully solid. |
| Top/bottom solid layers | 5 | Ensures the socket floor and backing plate top surface are flat and dimensionally accurate. |
| Infill | 40% gyroid or rectilinear | Socket walls are mostly perimeters; infill fills the backing plate and any wall interior. 40% is more than sufficient for a fit-test part. |
| Support | NONE | In Orientation B (arch end on bed) there are no overhangs requiring support. |
| Brim | 5 mm, 3 loops | Required for the narrow footprint (28.2 × 12.5 mm) with a tall part. |
| Print speed | 50–80% of default | Slow down for better dimensional accuracy on the first fit test. The part is small; the time cost is minimal. |
| Elephant foot compensation | 0.1 mm | The arch end is on the bed and will squish slightly. Compensate to keep the first few layers of the socket profile accurate. |
| Tolerance adjustment | NONE (print nominal) | Unless you decide to add the 0.2 mm clearance first. See Conflict 2. |

**What to measure and check when the print comes off the bed:**

1. **Outer width (X):** caliper across the short axis → expect 28.2 mm ± 0.3 mm.
2. **Outer length (Y):** caliper along the long axis → expect 40.1 mm ± 0.3 mm.
3. **Total height (Z):** caliper → expect 12.5 mm ± 0.2 mm. (In Orientation B this is now the print-X/Y horizontal width, not the print-Z height.)
4. **Lip opening width (X):** try to reach a caliper into the mouth and measure the lip-to-lip gap → expect 17.2 mm. This validates the 2 mm overhang per side.
5. **Socket depth (Z from rail top to lip underside):** measure rail height (expect 3.0 mm) then socket depth (expect 7.0 mm). The gap between rail top and lip underside = 4.0 mm nominal. This is the dimension that must accommodate the 4.02 mm blade.
6. **Slide-on fit:** attempt to slide the actual cleat blade into the mouth. You're looking for:
   - Does it START to enter? (validates mouth geometry)
   - Does it slide freely or does it bind? (reveals fit tightness)
   - Does it seat fully? (validates socket length and rail geometry)
   - Can you feel the lips grip the back face? (validates capture geometry)
7. **Extraction:** can the blade slide back out without excessive force? In v1 (no taper) it should slide freely or very slightly tight.

**Dimensions you're NOT expecting to be perfect on v1 (photo-scaled estimates):** socket depth (7 mm), rail height (3 mm), lip overhang (2 mm). These are the open items. The print tells you the baseline; then tune.
