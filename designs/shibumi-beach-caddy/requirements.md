# Shibumi Beach Caddy — Requirements (Phase 2)

## Program context
Phase 2 of the Shibumi-adapters program. Phase 1 built the **capture socket** that grabs
the beach chair's molded cleat. Phase 2 builds the thing that hangs off it: **one caddy
that holds a phone, a Kindle, and a Yeti bottle together, ergonomically.**

This supersedes the earlier "swappable single-item holder" idea — Matt wants all three
held **at once**, and (WM#584) originally imagined it **unibody**.

## Who / parameterization
- **Matt** = the reference spec (dims below, from WM#584 2026-07-25).
- **Hana** gets her **own** caddy with her devices' dims (TBD).
- Therefore the model is **parameterized per person**: swapping to Hana's dimensions must
  be a re-slice, not a redesign. All item dimensions live in a per-person params block.

## Matt's item dimensions (reference)
| Item | W (mm) | H (mm) | Thick (mm) | Notes |
|---|---|---|---|---|
| iPhone (in case) | 77 | ~156 **floor** | ~15 | H caliper-maxed → likely more; t includes camera bump |
| Kindle | 130 | ~176 **floor** | 14 | H caliper-maxed → likely more |
| Yeti bottle | Ø ~96 **assumed** | — | — | Matt said "96 radius"; treated as **diameter** (flag pending) |

Tall dims are caliper **floors** → design the cradle heights with extra margin so a
slightly-taller-than-measured device still seats.

## Functional requirements
1. Hold phone + Kindle + Yeti simultaneously, each retained against a beach setting
   (wind, bumps) yet easy to grab one-handed.
2. Mount to the chair via the Phase-1 capture socket (backing interface 28.2×40.1, r3.0).
3. **Prefer unibody.** Split into transport modules only if it is genuinely more portable
   AND stays robust + low-profile (no bulk, no compromise).
4. Survive a **full Yeti's** load as a cantilever off the cleat (see §Structural).
5. Drainage / sand-shedding: open bottoms or slots so sand + water don't collect.
6. Parameterized per person (Matt now, Hana later).

## Structural requirement (why `requiresStrainAnalysis: true`)
A full bottle + tablets cantilevered off a small cleat socket is an overturning-moment
problem (~1.5–2 N·m estimated). Two consequences drive the architecture:
- **Unibody** is preferred structurally: it removes the separable coupling that would
  otherwise be the weakest link.
- The caddy likely must **bear on the chair frame**, with the heavy bottle kept nearest
  the mount and low. **Chair geometry is required** to finalize the load path — this is
  the top open item alongside the Yeti diameter.

## Build-volume constraint
Bambu X1C, 256×256×256 mm (bed diagonal 362 mm). The recommended layout (all receptacles
within the Kindle's 134 mm width, stacked in depth) fits ~140 × 150 mm footprint — see
`ARCHITECTURE.md` §Packaging.

## Open items
See `spec.json` → `open_items`. Top two blockers to real geometry: **Yeti diameter** and
**chair load path**. Neither blocks the packaging/massing work already done.

## Constraints
- Fully parametric OpenSCAD; every device dim + margin is an adjustable variable.
- Include `fdm-pla.scad`, `bambu-x1c.scad`, `common.scad`.
- `report_dimensions()` for bbox validation.
