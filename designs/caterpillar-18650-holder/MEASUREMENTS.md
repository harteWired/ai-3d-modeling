# Caterpillar 18650 Holder — Reference Dimensions

The held object is a **bare 18650 lithium cell, button-top** (the "nipple"/positive nub
is what the floor indent is for). 18650 = nominal 18 mm dia × 65 mm length.

## Cell reference (standard, button-top)

| Property | Value | Source |
|---|---|---|
| Body diameter | ~18.4 mm (nominal 18) | 18650 standard; unprotected cell body |
| Length (button-top) | ~65–68 mm | standard |
| Positive button (nipple) dia | ~5–6 mm | standard button-top |
| Positive button protrusion | ~1–1.5 mm | standard button-top |

> Protected/wrapped 18650s run fatter (~18.6–19 mm) and longer — this model targets
> **unprotected button-top cells**. For protected cells, widen the bore (see build.py).

## Design choices (user-confirmed, 2026-06-03)

- **Bore fit:** loose drop-in → **Ø19.2 mm bore** (cell ~18.4 + ~0.4 mm/side). Grab-and-go,
  slight rattle, no bind.
- **Socket depth:** **18 mm** (shallow rack, matches the Caterpillar Capsule Holder). Cell
  stands ~47 mm proud.
- **Insertion:** **positive-side-down.** A central **Ø7 mm × 1.8 mm-deep nipple indent** in
  each socket floor clears the positive button so the cell body rests flat on the 18 mm
  floor ring; the negative flat end faces up.
- Capacity **6 cells**, zig-zag caterpillar form (derivative of the capsule caterpillar).

## Validation (mesh, trimesh — ground truth)

- Watertight single body, 36.95 cm³, bbox 119.5 × 45.9 × 24.5 mm
- Ray-cast at each socket **center → floor z = 1.20 mm** (nipple indent, 1.8 mm deep)
- Ray-cast off-center within bore **→ floor z = 3.00 mm** (main socket floor / rest ring)
- Thinnest inter-bore wall ~1.50 mm (≥ 1.2 mm FDM floor)
