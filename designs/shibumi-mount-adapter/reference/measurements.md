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
