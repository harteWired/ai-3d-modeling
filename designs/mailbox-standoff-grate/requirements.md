# Mailbox Stand-off Grate

A raised drainage grate that sits inside a leaky mailbox to keep mail up out of the
water that pools on the floor. Prints in four interlocking dovetail-jigsaw quadrants so
each piece fits through the (smaller) door and onto the 256 mm bed; assembled inside the
box. Continuous cross-hatch drainage mesh with one two-color letter per quadrant
(M / H / H / K).

> **Design note:** the aesthetic evolved during modeling. The original brief (below) called
> for a swirling-vortex rib pattern; that proved fragile at the rib junctions, so the field
> became a **subtractive perforated plate** and then — per user direction — a **continuous
> 45° cross-hatch mesh** that carries the open-area/weight target. Each letter is a
> **mostly-solid two-color glyph** (second filament) with small drain holes, sitting in the
> mesh so it reads cleanly without a snag-prone open center.

## Source

- Dimensions: vault note `projects/3d-printing/2026-06-16-mailbox-standoff-plate.md` (Telegram, 2026-06-16)
- Intent + aesthetics: conversation 2026-06-15

## Problem

The mailbox leaks somewhere and water pools on the bottom; mail sitting on the floor
gets wet. Need a robust, simple grate that floats mail above the pooled water and lets
water drain through and away underneath.

## Mailbox interior (measured)

| Dimension | Value |
|---|---|
| Depth (front-to-back) | 13.75 in = **349.25 mm** |
| Width (side-to-side) | 9.75 in = **247.65 mm** |
| Front-bottom lip | ~1 in (25.4 mm) **deep** into the cavity from the front wall, underside ~¼ in (6.35 mm) off the floor |
| Edges/corners | all caulked (radiused/filled) — plate cannot reach true floor at the wall corners |
| Door opening | "about 1 in smaller all around" than the interior; door is large. No exact number — confirmed non-blocking by the 2×2 split |
| Pooled water | thin film only |

## Functional requirements

1. **Float the deck ~15 mm off the floor** (within the user's ½–¾ in band). Clears the
   caulk fillets, the thin water film, and the front lip (top of lip ≈ 6.35 mm + lip
   thickness; 15 mm floats above it).
2. **Drain freely** — open grate, target ~40–50 % open area so water passes straight
   through and runs off underneath. No closed top surface.
3. **Hold mail without poke-through** — drainage gaps small enough (~8–12 mm channels)
   that envelope corners don't dip or catch.
4. **Robust + simple** — light load (letters, small parcels). Stiff enough not to flex
   when a parcel lands on it.

## Print / assembly constraints

1. **Four-part 2×2 jigsaw.** Interior depth 349 mm exceeds the 256 mm bed *and* a
   full-width piece won't pass the door, so two halves can't work. Four quadrant pieces
   (~119 × 170 mm each) print flat and pass the door.
2. **Letters, one per quadrant** (plan view, "top" = back of box / far from door):
   - Back-left = **M** · Back-right = **H**
   - Front-left = **H** · Front-right = **K**
3. **Jigsaw interlock along the central cross seam** — resists lateral splay; gravity
   holds the assembly down. Assembly clearance ~0.2 mm/side on the interlock.
4. **Reinforce the 4-way center junction** — all four pieces meeting at one point is the
   weak spot. Stagger the seams or add a keyed central boss/overlap so the middle
   doesn't splay or hinge. (Solve in modeling.)
5. **Legs down to the true floor**, gravity-located:
   - ≥ ~20 mm inboard of the side and back walls (clear the corner caulk fillets)
   - front legs ≥ ~30 mm back from the front wall (land behind the 1-in front lip, on
     flat floor)
6. **Prints flat, grate-side up** — open cells are just holes, no bridging or supports.
7. **Material: PLA for v1**, reprint in PETG/ASA if it sags in summer mailbox heat
   (a metal box in sun can pass PLA's ~60 °C softening point). Keep geometry
   material-agnostic — no PLA-only tricks.

## Aesthetic (as built)

- **Continuous 45° cross-hatch mesh** across each tile — a uniform diamond lattice
  (1.8 mm ribs, ~46 % open) inside a solid perimeter/seam frame. Consistent and
  continuous, reads as one screen across the assembled grate.
- One **two-color letter per quadrant** (M / H / H / K). The letter is a **mostly-solid
  glyph in a second filament** with small Ø3.2 mm drain holes — legible, no thin outline,
  and no large open center for mail to catch on.
- Structural-first: the mesh carries the open-area/weight target so the letters can stay
  solid. Bold sans (Arial Black) glyphs for legibility.

> Earlier iterations (vortex ribs → subtractive turbine-hole plate → hollow-outline
> "negative" letters) are superseded by the cross-hatch + solid-letter design above.

## Dimensions (assembled, target)

| Axis | Value |
|---|---|
| X (width) | ~237.6 mm (interior − 5 mm/side wall clearance) |
| Y (depth) | ~339.2 mm |
| Z (height) | ~19 mm (15 mm legs + ~4 mm grate deck) |

## Out of scope / deferred

- Exact door opening number (user won't measure; 2×2 split makes it non-blocking).
- Strain analysis — load is light (mail), no `loadCase`.
