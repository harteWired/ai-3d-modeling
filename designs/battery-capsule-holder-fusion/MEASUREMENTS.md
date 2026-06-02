# Battery Capsule Holder — Measurement Intake

Status: **CONFIRMED (core dims) via user calipers, 2026-05-31.** Two minor items open.

## Source

Three top-down photos on a self-healing cutting mat with a printed grid:
- `reference/2026-06-01-scoops-01.jpg`  (filenames keep the legacy `scoops` capture name)
- `reference/2026-06-01-scoops-02.jpg`
- `reference/2026-06-01-scoops-03.jpg`

The held object is a **battery capsule**: a clear half + a teal half that attach to
close (batteries inside), mounted closed. Asymmetric teardrop / D-shaped cross-section.

## The held object — CALIPERED (ground truth)

| Property | Value |
|---|---|
| Cross-section, widest axis (teardrop long axis) | **27.8 mm** (clear) / 27.5 mm (teal) |
| Cross-section, narrower axis | **23.6 mm** (clear) / 23.7 mm (teal) |
| Height, assembled / closed | **69.0 mm** |
| Clear vs teal halves | match within ~0.3 mm → **uniform**, one pocket profile |
| Holder interface | **OUTER body only — must NOT enter the inner bore** |

Design pocket profile: teardrop ≈ **27.8 × 23.7 mm** (max of each axis) + clearance.

### Resolved (user, 2026-05-31)
- Body profile: **straight / uniform** teardrop along its height → simple prismatic pocket.
- Socket depth: **18 mm** (user choice — shallow, low-profile drawer rack). Capsule
  stands ~51 mm proud.
- Seam / V protrusion: **don't care** — at 18 mm the socket grips only the lower
  straight body, below the mid-height seam and the upper-half V feature. Pocket =
  body footprint + clearance, no relief notch needed.

## Scale calibration (for the registration study)

- Grid major square = **10 mm (1 cm)** — confirmed by Claude (circle-template mm
  cross-check) and Gemini. Long-edge ruler is cm (0–42); short ruler is inches (0–8).

## Photo estimates vs ground truth (informs the registration protocol)

The blind 5-method benchmark (workflow `image-registration-accuracy`) gave, vs the
caliper truth of 27.8 mm widest / 23.6 mm narrower:

| Method | Widest | Narrower | MAE |
|---|---|---|---|
| gemini-flash | 30.5 | 21.5 | **2.5 mm (best)** |
| gemini-pro | 22 | 18 | 5.65 |
| claude-ruler | 20.4 | 16.8 | 7.6 |
| claude-grid | 21 | 17 | 7.78 |
| claude-circles | 20.5 | 16.5 | 8.03 (worst) |

**Caution — the ranking is run-unstable.** In the FIRST ad-hoc read, the order flipped:
Gemini Flash overshot to ~45 mm (worst) and Claude's grid read landed ~28–32 mm (best).
Same images, opposite winner. The durable takeaway is not "method X wins" but that
*every* photo read ran 2.5–8 mm off and run-to-run spread can exceed the error — hence
multi-pass + **calipers mandatory for fit-critical dims**. Protocol baked into
`AGENT-WORKFLOW.md`.

## Locked design decisions (2026-05-31)

- Capacity: **6 capsules**, staggered/alternating teardrop array
- Retention: **loose drop-in** (gravity, beaker-rack) → clearance fit
- Mounting: **inside a drawer** → low profile, non-slip base, no tall walls
- Each pocket accepts the capsule **either end up**; pocket grips the outer teardrop
  body, **no internal post** (never touches the bore)
- Capsule is 69 mm tall → proposing a ~25–30 mm socket depth (anti-tip) rather than a
  full-height sleeve, to keep the drawer rack low-profile. **Confirm with user.**
