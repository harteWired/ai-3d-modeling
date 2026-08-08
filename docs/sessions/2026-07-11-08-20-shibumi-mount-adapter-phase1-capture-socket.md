---
date: 2026-07-11
project: 3d-printing
type: session-log
---

# 2026-07-11 — Shibumi Mount Adapter: Phase 1 capture-socket fit test (reverse-engineered from photos)

> **Backfill note.** This log was reconstructed from git (commits `90c4f10`→`f94245c`) + design
> files after a Jinn container crash (~15:00 UTC 2026-07-11) interrupted a `compress fast`. No live
> transcript survived; the "Raw Session Log" section is therefore a git-derived reconstruction, not a
> verbatim capture. All work described was committed and pushed before the crash — nothing was lost.

## Quick Reference
**Keywords:** shibumi-mount-adapter, beach-chair cleat, capture socket, slide-in mount, reverse-engineered from caliper photos, 4-way multi-model registration (Claude+Gemini+2 blind agents), cross-section closure check, parametric OpenSCAD, capture lip, inverted-U floor rails, arch bridge, mouth open end, tolerance ladder, gap 4.0/4.2/4.35, debossed variant numbers, Phase 1 of shibumi-adapters program, support-free arch-end print
**Project:** 3d-printing
**Outcome:** Started a new multi-phase beach-chair accessory program. Phase 1 = reverse-engineer the grey molded **capture socket** that slides onto the Shibumi chair's cleat, as a dimensionally-accurate, tolerance-tunable print, so later holders (bottle/table/phone) reuse a proven mount. Recovered geometry from caliper photos via a 4-way multi-model pass, validated it against two independent cross-section sums + the owner's measured cleat blade, modeled it in parametric OpenSCAD, and shipped a **3-piece clearance ladder** (capture gap 4.0/4.2/4.35, variant number debossed into each backing) via PR #8 → main. Phase 1 is READY TO PRINT — blocked only on Matt's physical fit-test against the real cleat.

## What Was Done
- **New program kickoff.** Framed shibumi-mount-adapter as Phase 1 of a beach-chair accessory program: reproduce the attachment mechanism ONLY (no holders yet), so later phases (water bottle w/ modular cutouts, table, phone/Kindle pocket) plug into a validated mount interface.
- **Reverse-engineered geometry from photos** (`31b1b38`). No drawing exists — recovered dimensions from caliper photos via a 4-way multi-model registration pass (Claude + Gemini + two blind agents), reconciled in `reference/measurements.md`. In-plane geometry closes on **two independent short-axis sums** (wall 3.5 + slot 4.63 + tongue 11.95 + slot 4.63 + wall 3.5 = 28.21 ≈ 28.2 outer; inner 21.21 ≈ 21.22). Owner's separately-measured **4.02 mm cleat blade** validated the estimated 7 mm socket depth (rail 3 + blade 4.02 = 7.02 ≈ 7 ✓).
- **Corrected the architecture read.** Earlier interpretation (raised tongue / round-post clip) was wrong. Resolved via the 2026-07-11 cleat-detail photos (26,27,29–33): the cleat is a **flat grey molded tab ~27.6 mm wide** at the leg-pivot knuckle. Since 27.6 > the ~21.2 mouth opening, the blade enters **lengthwise** through the open mouth end. Final architecture = a **slide-in capture socket**: side-wall tops curl inward into **capture lips** that trap the blade's back face; two thin floor **rails** (2.15 wide, 8.2 slot, 4.5 off each wall) set seating height; **closed arch bridge** at the far end; decorative sewing terraces + flange **dropped**.
- **Modeled parametric OpenSCAD**, validated manifold/watertight at **28.2 × 40.1 × 12.5 mm**. Prints support-free stood on its arch end (mouth up) so the capture lips run vertical.
- **Added STL-cut proof renders** (`3c9da77`): `proof-mouth-3q.png` (looking into the open mouth — cavity, inward lips, floor rails, arch bridge) + `proof-short-section.png` (short-axis cross-section) + `proof-top.png`, rendered from the actual STL via `reference/proof.scad`.
- **Fixed capture-lip bridging the mouth** (`ca402c0`): the lip ring's closed band was landing on the −Y MOUTH instead of the far arch end, putting a crossbar across the exact opening the cleat slides into. Flipped the hole offset to −lip_overhang/2 so the band sits at the +Y arch end and the mouth stays fully open.
- **Rebuilt the lip as a contiguous open-U** (`7138c0d`): replaced the shifted ring (which left a pinched/pointy, print-fragile remnant) with a continuous inside border running straight down both long walls to the mouth edge and wrapping the far arch end, open at the mouth. Lip overhang set to **measured 2.1** (photo 10 = 2.12). `measurements.md` now carries the definitive post-Gemini-scan parameter table.
- **Debossed variant numbers** (`f94245c`): parametric `label` cut so the three fit-test sockets are visually distinguishable — A=1 (nominal), B=2 (snug), C=3 (sliding) — 0.8 mm deep on the flat backing outer face, mirrored to read correctly face-on.
- **Shipped PR #8 → main** (`31b1b38` + merge `da6031b`): README row, `docs/shibumi-mount-adapter.md`, spec.json, requirements.md, modeling-report.json, review-printability.md, three fit-test STLs.

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Model the mount mechanism ONLY (drop terraces + flange) | Phase 1 goal is a reusable, proven mount interface; the decorative stitching geometry is irrelevant to fit |
| 3-piece clearance ladder (gap 4.0 / 4.2 / 4.35) | Nominal 4.0 sits on the 4.02 blade with zero clearance (validates X-Y but won't slide); bracket the vertical clearance to find the slide-on sweet spot in ONE print session |
| Vary clearance via rail height (not lip gap) | Keeps the capture-lip geometry constant across variants; rails set seating height = the tunable dimension |
| Deboss 1/2/3 into the backing | Three near-identical prints are otherwise indistinguishable on the bench after printing |
| Print support-free on the arch end (mouth up) | Capture lips run vertical → no overhang supports inside the cavity |
| Contiguous open-U lip (not a shifted ring) | The ring left a pinched pointy remnant at the mouth that was fragile to print; the open-U border is robust and keeps the mouth clear |
| Material-agnostic geometry; PLA for fit tests | Final beach part likely PETG/ASA (UV + hot-trunk resistance); geometry kept neutral so material is a later swap |

## Key Learnings
- **Multi-model photo registration + closure checks give real confidence without a drawing.** Four independent interpretation passes reconciled, then validated by two independent cross-section sums closing to within 0.03 mm AND an orthogonal physical measurement (the 4.02 blade validating the 7 mm depth). This is the [[feedback_multi_source_image_registration]] pattern paying off.
- **The earlier architecture read was wrong** (raised tongue / round-post clip). The mechanism is a flat-tab slide-in capture socket — resolved only once the cleat-detail photos arrived. Lesson: nail down "what does it grab, and which surface" before committing the modeler.
- **Lip band placement matters for function, not just looks:** a closed band on the mouth end silently crossbars the slide-in opening. Always confirm the OPEN end stays open in a proof render.
- **A thin shifted-ring lip leaves a fragile pointy remnant;** a contiguous open-U border is the printable form for a capture lip with one open end.
- **Zero-clearance nominal is a validator, not a usable fit** — ship a clearance ladder when the target dimension sits right on the mating part.

## Files Modified / Created
- `designs/shibumi-mount-adapter/shibumi-mount-adapter.scad`: NEW parametric capture socket (walls, contiguous open-U capture lip @2.1 overhang, inverted-U floor rails, arch bridge, parametric capture gap + debossed variant label).
- `designs/shibumi-mount-adapter/output/fit-test/socket-{A-nominal-gap4.0, B-snug-gap4.2, C-sliding-gap4.35}.stl`: the 3-piece clearance ladder, variant number debossed.
- `designs/shibumi-mount-adapter/output/shibumi-mount-adapter.stl`: nominal reference STL (watertight, 1 body, 28.2×40.1×12.5).
- `designs/shibumi-mount-adapter/output/proofs/proof-{mouth-3q, short-section, top}.png`: STL-cut proof renders.
- `designs/shibumi-mount-adapter/output/{modeling-report.json, review-printability.md}`: modeling + printability review.
- `designs/shibumi-mount-adapter/reference/{measurements.md, draw_socket.py, grid_overlay.py, proof.scad}`: reconciled caliper table + closure checks + helper scripts.
- `designs/shibumi-mount-adapter/reference/photos/`: caliper photos (01–15 from 2026-07-10; 16–33 from 2026-07-11, 28 omitted).
- `designs/shibumi-mount-adapter/{spec.json, requirements.md}`: Phase 1 spec + requirements (corrected architecture).
- `docs/shibumi-mount-adapter.md` + `docs/images/shibumi-mount-adapter/`: design page (proofs, dimension-derivation, tolerance ladder).
- `README.md`: newest-first Designs row.
- Commits: `90c4f10` (photos in) → `31b1b38` (add + PR #8) → merge `da6031b` → `3c9da77` (proofs) → `ca402c0` (lip mouth fix) → `7138c0d` (open-U lip) → `f94245c` (deboss). All pushed.

## Follow-ups
- [ ] **BLOCKED ON MATT (physical):** print the three fit-test variants (A gap 4.0 / B 4.2 / C 4.35) and report which gap grips the real beach-chair cleat blade. This is the only input Phase 1 waits on; everything model-side is done.
- [ ] **Cleat tab THICKNESS not yet calipered** — it sets the socket cavity clearance and is "the one dim to grab next if fit is tight." Ask Matt to measure if the ladder doesn't land a good fit.
- [ ] Next steps once fit lands: internal-taper tuning to recover the original's soft-material grip (rigid PLA reproduces nominal geometry first), and a parametric Fusion rebuild.
- [ ] Then Phase 2+: holders (water bottle w/ modular size cutouts, table, phone/Kindle pocket) that reuse this validated mount interface.

## Raw Session Log

_Reconstructed from git, not a verbatim transcript (see backfill note above)._ The work landed
across seven commits on 2026-07-10 evening through 2026-07-11 07:12 PT: photos ingested and
`measurements.md` updated (`90c4f10`); socket modeled, validated, and shipped via PR #8 with the
3-piece clearance ladder (`31b1b38` + merge `da6031b`); proof renders added (`3c9da77`); two
capture-lip corrections — mouth-bridging band flip (`ca402c0`) then contiguous open-U rebuild at
measured 2.1 overhang (`7138c0d`); and finally debossed 1/2/3 variant labels (`f94245c`). A
`compress fast` was in flight when the Jinn container hung and crashed (~15:00 UTC 2026-07-11);
the box was rebooted, session recovered via /resume, and this log was backfilled from the
committed state.
