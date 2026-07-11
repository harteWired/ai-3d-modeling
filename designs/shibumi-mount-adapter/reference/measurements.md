> 🆕 **HANDOFF 2026-07-11 → modeler:** the Z-geometry photos you were blocked on are IN.
> 18 new shots in `photos/2026-07-11-shibumi-adapter-16..33.jpg` (28 omitted). See the two
> "📸 Photos received 2026-07-11" sections below — mount profile/standoff/socket-depth/end-on
> cross-section (16–25) **and** the cleat = flat ~27.6 mm leg-pivot tab (26–33). Still un-calipered:
> Z values (scale off 28.2/46.61) and the cleat-tab thickness. Ready to reconcile Z → parametric v1.

# Shibumi Mount Adapter — Reference Measurement Analysis

Phase 1 of the Shibumi-adapters program: reproduce the **attachment mechanism** (the grey
molded buckle/loop) dimensionally, print it, dial in tolerances against the real cleat.
Later phases add holders (bottle, table, phone/Kindle) that reuse this mechanism.

Source: Matt's caliper photos (2026-07-10), 15 images in `photos/`.
Analysis method: 4 independent blind reads — Claude (main), Gemini 3.1-pro, and two blind
Claude agents — reconciled below. Spread between passes = uncertainty estimate.

## DEFINITIVE PARAMETER SET (2026-07-11, post exhaustive Gemini scan of all 32 photos + Matt ground-truth)

Reconciled from: Matt's direct caliper values (authoritative), a Gemini 3.1-pro scan of every
image, and Claude re-reads of the contested shots. This is the source of truth for the model.

**FUNCTIONAL socket (modeled):**
| Param | Value | Source / confidence |
|---|---:|---|
| Loop outer width (short) | 28.2 | photo 09, measured |
| Loop outer length (long) | 40.1 | photo 17 (re-read; Gemini's 40.71/"cavity" was a misread) |
| Inner cavity width | 21.2 | photo 06; Matt short-axis check = 21.5 |
| Inner cavity length | ~33 | est = 40.1 − 2×3.5 walls |
| Wall thickness | ~3.5 | derived |
| **Capture lip inward overhang / side** | **2.1** | **photo 10 = 2.12 — MEASURED (was est 2.0)** |
| Lip vertical zone height | ~3 | est |
| Standoff (wall top) | ~10 | est |
| Socket depth (floor→lip underside) | ~7 | est; cross-checks rail 3 + blade 4.02 = 7.02 |
| Rail width (each) | 2.15 | Matt, measured |
| Rail height | ~3 | est |
| Rail offset from wall | 4.5 | Matt, measured |
| Central slot | 8.2 | Matt, measured |
| Backing thickness | ~2.5 | est |

**CLEAT (reference, NOT modeled):** tab width 27.8 (photos 15/33; 32=26.9) · tab thickness **4.02** (Matt; Gemini's 2.69 = decimal misread of 26.9) · round tube OD 20.01 (photo 14).

**DROPPED decorative:** outer sewing terrace plate ≈ 46.6 × 46.9 (photos 08/11) — stitch flange, not modeled.

**Conflicts resolved this pass:** (1) 11.95 = across the whole tongue (rail+slot+rail ≈ 12.5), NOT the slot — slot is 8.2. (2) photo 17 = loop outer length 40.1, not cavity length. (3) photo 10 = 2.12 lip overhang (upgrades estimate → measured). (4) cleat thickness = 4.02, not Gemini's 2.69.

**Still estimated (calipers would firm up):** lip zone height, standoff, socket depth, rail height, cavity length, backing thickness. The rail 3 + blade 4.02 ≈ depth 7 identity anchors the Z stack.

---

## What the part is — CORRECTED architecture (2026-07-10, per Matt + zoom re-review)

> ⚠️ SUPERSEDES the earlier "raised tongue" reading, which was WRONG (lighting fooled the
> first passes into seeing a recessed cavity as a raised tongue).

A grey injection-molded plate sewn onto a blue neoprene sleeve. Concentric stepped ridges are
just the sewing terraces (dropped for the print). The functional feature is a **CAPTURE
SOCKET** that a flat cleat blade **slides down into lengthwise**:

- The two side **walls are the tall feature**, and their tops **curl/overhang INWARD** toward
  the centerline — the overhang wraps around the **back** of the cleat (an undercut capture).
- The center is **two LOW rails** on the socket floor (NOT a tall tongue) that register the
  cleat's front face. Much shorter than the walls.
- The socket is **open at the mouth end** (cleat enters) and bridged/closed at the far end.

```
 SHORT-AXIS SECTION
   |<---------------- 28.2 outer ---------------->|
    ______                                  ______
   / lip  \___                          ___/ lip  \    ← wall tops curl INWARD
   | wall      \   overhang wraps the   /      wall |   ▲ wall height = ?? unmeasured
   |            |  BACK of the cleat   |           |   │
   |    __      |                      |     __    |   │ socket cavity (in shadow)
   |   |r1|_____|______________________|____|r2|   |   ▼ rail height = LOW, ?? unmeasured
   ==== floor ======================================
         |<gap>|      two shallow floor rails
   |<------------- ~21.2 cavity floor ----------->|
```

The soft/compliant molded material lets the overhang flex to snap over the cleat; a rigid PLA
copy will likely need an internal taper to recover that grip (later fit round).

### Unresolved from photos (awaiting more shots from Matt)
- All Z values: wall height, inward-overhang amount, rail height, socket depth.
- Mating puzzle: cleat blade is **27.86 wide** but cavity opening is **~21.2** → blade must
  enter edge-on/lengthwise (27.86 along the ~39 cavity length). Need a mated photo to confirm.
- Cleat blade THICKNESS (governs the cavity width the socket must accept) — not yet measured.

### 📸 Photos received 2026-07-11 (16–25) — profile / end-on / cross-section  ← UNBLOCKS most of the above
Matt sent 10 more shots: `reference/photos/2026-07-11-shibumi-adapter-16..25.jpg`. **Un-calipered geometry views** (scale off the known caliper dims), but they finally show the Z / interior:
- **Standoff height + total side profile:** 21, 22, 25 (edge-on + 3/4) — socket + backing plate in side profile; read the raised-loop standoff height here.
- **End-on cross-section INTO the cavity:** 18, 19, 23, 24 — socket depth, inward wall overhang, the internal rail/tongue in section, and the **OPEN short end** (confirms the blade slides in **lengthwise/end-on**, per the mating-puzzle hypothesis).
- **Inward wall overhang + central bar + side slots:** 16, 17, 20, 24, 25.
- **Long-axis internal layout:** 16, 20 (top-down) — tongue running the length, open entry end, top crossbar.
- **Caliper in-frame:** 17 (reads ~40.1 mm — confirm which feature).
- **Caveats (still open):** (1) no shot of the mount actually seated **on the chair cleat** — the open-end sections strongly imply lengthwise entry but a true mated-on-cleat photo would still confirm engagement; (2) blade **thickness** still not calipered; (3) these are visual — derive Z by scaling against the 28.2 / 46.61 known dims, or ask Matt for calipered Z on standoff + socket depth if fit-critical.

### ✅ RESOLVED architecture (2026-07-11, main Claude, from photos 16–25)

Slide-in **undercut socket**. Cleat enters the OPEN mouth end and slides LENGTHWISE; the
inward-curling wall lips grab its back edges; a low central rail structure registers its front.

- **Side walls** rise ~10 mm and their tops **curl inward into a lip/ledge** (undercut) —
  clear in photos 18, 19. Overhang wraps the cleat's back.
- **Far end = closed arch bridge**; **mouth end = open** (photos 22, 24, 25). Lengthwise entry.
- **Center = two LOW rails** on the floor (photos 20, 22), far below the wall tops.
- **Functional raised loop outer length ≈ 40.1 mm** (photo 17 caliper), width 28.2. The 46.61
  (photo 08) is the OUTERMOST decorative terrace — DROPPED. Inner cavity ≈ 33 L × 21.2 W, so a
  27.6 mm cleat slides in lengthwise with ~5 mm clearance. Geometry closes.

**Central feature = inverted-U tongue** (two thin rails joined by a rounded bridge at the closed
end, with a wide central slot). Rail dims are MEASURED by Matt (2026-07-11):

| Feature | Value | Source |
|---|---:|---|
| Rail (leg) width, each | **2.15 mm** | Matt caliper |
| Central slot (between rails) | **8.2 mm** | Matt caliper |
| Rail offset from each side wall | **4.5 mm** | Matt caliper |
| Short-axis check: 4.5+2.15+8.2+2.15+4.5 | 21.5 ≈ 21.2 cavity ✓ | |

> Correction: batch-1 photo 11 = **4.63 ≈ the wall→rail gap (4.5)**, NOT a rail width. Earlier
> passes mis-mapped it as slot/rail. Rails are thin (2.15), not 4.63.

Z / remaining estimates (scaled off 28.2 / 40.1 — correct on first test print):

| Feature | Estimate |
|---|---:|
| Loop standoff height (backing top → wall top) | ~10 mm |
| Backing plate thickness | ~2.5 mm |
| Wall base thickness | ~3.5 mm |
| Inward lip overhang (per side) | ~2 mm |
| Socket depth (floor → lip underside) | ~7 mm |
| Central rail height | ~3 mm |
| Inner cavity length | ~33 mm |
| Inner cavity width | ~21.2 mm |

### 📸 Cleat-detail photos 2026-07-11 (26, 27, 29–33) — resolves "what does the socket grab?"
`reference/photos/2026-07-11-shibumi-adapter-{26,27,29..33}.jpg` (28 was an accidental selfie, omitted). These show the **chair-side cleat**: a **flat grey molded tab** at the leg-pivot junction (where two round tubes cross a moulded knuckle), next to the **~20 mm round tube** and a **round pivot boss/knuckle**. The socket slides onto this flat tab.
- Cleat tab calipered ~**26.9–27.6 mm** wide (30–33), consistent with the earlier **27.86** "wide pivot tab" reading → this is the engaged surface.
- **Resolves open Q4** (cleat is a flat tab, not a round post; the mechanism grabs the ~27.6 mm tab, entering lengthwise since 27.6 > the ~21.2 opening).
- Still not calipered: the cleat tab **thickness** (sets the socket cavity clearance) — the one dim to grab next if fit is tight.

## Reconciled caliper table

| Reading | Photo | Feature | Confidence | Notes |
|---|---:|---|---|---|
| **46.61 mm** | 08 | Buckle loop — OUTER length (long axis) | High | Gemini+2 agents agree |
| **28.2 mm** | 09 | Buckle loop — OUTER width (short axis) | High | all passes agree (~28.2) |
| **21.22 mm** | 05/06 | Buckle INNER opening width (short axis) | High | closes the cross-section ✓ |
| **11.95 mm** | 07 | Center TONGUE-bar width | High | closes the cross-section ✓ |
| **4.63 mm** | 11 | SLOT width, each side (tongue↔wall gap) | High | closes the cross-section ✓ |
| **22.89 mm** | 12 | Across tongue-base region (ambiguous) | Low–Med | ~inner width variant; re-measure |
| **~21.2 mm** | 10 | Repeat inner-opening OR 2nd axis (blurry) | Low | last digit deblurred; re-measure |
| **20.01 mm** | 14 | CLEAT round frame-tube OD (reference only) | High | all agree |
| **27.86 mm** | 15 | CLEAT wider section / pivot boss (ref only) | Med–High | all agree |

## Cross-section consistency check (strong result)

Short-axis section across the buckle closes to within 0.03 mm on **two** independent sums —
this is why confidence on the short-axis numbers is high:

```
wall 3.5 + slot 4.63 + tongue 11.95 + slot 4.63 + wall 3.5 = 28.21 mm  ≈ 28.2 outer  ✓
             slot 4.63 + tongue 11.95 + slot 4.63          = 21.21 mm  ≈ 21.22 inner ✓
```

Derived wall thickness ≈ **3.5 mm** each side ( (28.2 − 21.2) / 2 ).

## MISSING — must measure before modeling (fit-critical)

1. **Standoff height** of the raised loop above the plate (Z). *Not in any photo.* Critical.
2. **Slot depth** — how deep the two 4.63 mm channels run.
3. **Long-axis internal layout** — inner opening length, tongue length, where the tongue
   anchors, and the top crossbar width. Only the 46.61 outer length is known.
4. **Cleat geometry** — is it a 20 mm round post, a rail, or a flat tab, and which dimension
   the mechanism actually grabs? 20.01 (round) and 27.86 (wide) are reference; confirm the
   real engaged surface.

## Open functional question

How the loop engages the cleat is not yet certain (slide-on rail vs. clip-over post vs.
strap keeper). Correspondences worth noting: cleat round 20.0 ≈ inner opening 21.2 (~1.2 mm
gap); cleat wide 27.86 ≈ outer width 28.2. To be confirmed with Matt before modeling.
