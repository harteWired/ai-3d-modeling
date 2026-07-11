# Shibumi Mount Adapter — Requirements (Phase 1)

## Program context
Phase 1 of the Shibumi-adapters program. Reproduce the **attachment mechanism** — the grey
molded capture socket that slides onto the beach-chair cleat — as a dimensionally-accurate,
tolerance-tunable 3D print. Later phases build holders (water bottle w/ modular size cutouts,
table, phone/Kindle pocket) that reuse this mechanism.

**Phase 1 scope: the mount mechanism ONLY.** No holders yet.

## Architecture (resolved from photos 16–33 + Matt's measurements)
A **slide-in capture socket**. A flat cleat blade enters the **open mouth end** and slides in
**lengthwise**; the socket's side-wall tops **curl inward into lips** that trap the blade's back
face; two thin floor rails set the blade's seating height. Closed **arch bridge** at the far end.

- Side walls rise ~10 mm and their tops overhang inward ~2 mm/side (undercut capture lips).
- Far end = closed arch bridge; mouth end = open (lengthwise entry).
- Floor carries an **inverted-U tongue**: two thin rails (2.15 wide) joined by a rounded bridge
  at the closed end, with a wide (8.2) central slot; rails sit 4.5 mm off each side wall.
- Decorative concentric sewing terraces + flange of the original are **DROPPED**; only the
  functional socket on a minimal backing is modeled.

## Dimensions

### Measured — high confidence
| Feature | Value |
|---|---:|
| Loop outer width (short axis) | 28.2 mm |
| Loop outer length (long axis) | 40.1 mm |
| Inner cavity width | 21.2 mm |
| Wall base thickness | ~3.5 mm |
| Rail (leg) width, each | 2.15 mm |
| Central slot (between rails) | 8.2 mm |
| Rail offset from each side wall | 4.5 mm |

Short-axis check: 4.5 + 2.15 + 8.2 + 2.15 + 4.5 = 21.5 ≈ 21.2 cavity ✓

### Estimated from photos — parametric, correct on first test print
| Feature | Estimate |
|---|---:|
| Loop standoff height (backing → wall top) | ~10 mm |
| Socket depth (floor → lip underside) | ~7 mm |
| Inward lip overhang, per side | ~2 mm |
| Rail height | ~3 mm |
| Inner cavity length | ~33 mm |
| Backing plate thickness | ~2.5 mm |

### Cleat — reference only, NOT modeled
| Feature | Value |
|---|---:|
| Flat tab width | 27.6 mm (26.9–27.86 across shots) |
| Flat tab thickness | 4.02 mm |
| Round leg-tube OD | 20.01 mm |

Capture check: rail height 3 + blade 4.02 = 7.02 ≈ socket depth 7 (blade back meets lip underside).

## Print intent
- Fully parametric OpenSCAD; every estimated value is an adjustable variable.
- v1 = faithful nominal reproduction, **no taper** — print and test the slide onto the real cleat.
- Undercut lips + arch = an undercut/overhang; modeler + print-reviewer to pick print orientation
  (likely mouth-up or on-back) and flag any support needs. Internal taper for grip is a later round.
- Material: PLA for fit-test; final beach part likely PETG/ASA (UV + hot-trunk).

## Open items
- Validate the ~6 estimated Z dims on the first print.
- Tune internal taper to the 4.02 mm blade for grip after the nominal repro is confirmed.
