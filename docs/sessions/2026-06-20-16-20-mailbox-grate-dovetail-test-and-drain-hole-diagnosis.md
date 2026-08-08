---
date: 2026-06-20
project: 3d-printing
type: session-log
---

# 2026-06-20 — Mailbox grate: dovetail fit-test strip + drain-hole slicer diagnosis

## Quick Reference
**Keywords:** mailbox-standoff-grate, dovetail test print, fit-test strip, 0.2mm clearance, tileperf-K seam slice, drain holes, two-color cap, slicer skinning, top/bottom shell bridging, Bambu Assemble objects, through-hole, render-input mistake, H2 printed solid
**Project:** 3d-printing
**Outcome:** Built + committed an 8 g dovetail fit-test strip that mates the printing H2 tile (validates the 0.2mm clearance before committing to all four). Then diagnosed two drain-hole issues: (1) a preview render that looked solid was a render-input mistake (geometry is fine), and (2) the user's printed H2 came out SOLID because the slicer skins the Ø3.2mm holes shut — the 1mm color cap is thinner than the top+bottom shell count, and the base+cap are separate stacked objects that each skin the z=3 interface. Fix = Assemble the two objects into one.

## What Was Done
- Realized the spec flagged a high-priority dovetail mating test print that we skipped. Built `test-dovetail-strip-K-mates-H2.stl` — a thin full-height slice of `tileperf-K`'s vertical seam edge (rail + teeth/notches, no mesh/letter/legs), carved via trimesh box-intersection so the teeth + 0.2mm clearance exactly match the real tile. 23×170×4mm, ~8g, watertight, strip↔H2 interference 0.0000cc.
- Added a "Test print — dovetail fit check" section to the design doc with a slotted-on preview image + drop-in test instructions; committed strip + image + doc (4ce0f19, direct to main).
- Diagnosed "missing drain holes on the top colored surface" the user spotted in the committed `dovetail-test.png`: geometry is intact (50 drains in H2-base, 36 in cap, through-holes); the preview was rendered from `H2-base.stl` ALONE (no letter-cap overlay) in single color, so the colored cap (which makes the holes legible) was absent and the recessed tan-on-tan base letter washed out at draft quality → read solid. Render-input mistake, not a design regression. Did NOT fix (user said leave it).
- User printed the H2 tile → came out SOLID despite the slicer object-view showing holes. Diagnosed the slicer is skinning the holes shut (see Solutions).

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Single mating strip (not a printed pair) | One full tile (H2) is already printing; a faithful K-edge slice mates it → tests the real 0.2mm fit for ~8g |
| Carve strip from tileperf-K via box intersection | Guarantees teeth/notches/clearance identical to the production tile (no re-derivation) |
| Don't fix the misleading preview render | User explicitly said diagnose-don't-fix; geometry is correct |

## Key Learnings
- A thin two-color "cap" (here 1mm ≈ 5 layers) that is THINNER than the slicer's combined top+bottom shell layers gets treated as all-solid-surface, and the slicer bridges small holes shut. Through-holes need to be deeper than top_shell+bottom_shell, or be part of one continuous object.
- Two separate STACKED objects each generate their own solid top/bottom skin at the shared interface plane; a small hole crossing that plane gets capped by those skins even if both objects have the hole. Assembling them into one object removes the internal interface and lets the hole run continuously.
- Bambu "Assemble into one object" fixes BOTH the object-overlap warning AND this hole-capping — same step.
- When rendering a preview that includes a two-color tile, include the cap overlay or the render silently drops a whole feature (the perforated colored show face).

## Solutions & Fixes
- **H2 printed solid (drain holes filled):** not the model — the slicer skins the Ø3.2mm holes shut. Two compounding causes: (1) the 1mm color cap is ~5 layers < top+bottom shell count → entire cap is solid surface, holes bridged; (2) base + cap are separate stacked objects → each skins the z=3 interface, capping holes there too. Confirm via the sliced layer/toolpath preview (not object preview) at mid-letter, or by slicing single-color `tileperf-H2.stl` (one continuous 4mm hole survives the shells). Fix: select both objects → Assemble into one object (continuous 4mm through-hole), or reduce top/bottom shell layers, or thicken the cap.

## Files Modified
- `designs/mailbox-standoff-grate/output/test-dovetail-strip-K-mates-H2.stl`: NEW ~8g dovetail fit-test strip (mates H2).
- `docs/images/mailbox-standoff-grate/mailbox-standoff-grate-dovetail-test.png`: NEW preview (note: rendered base-only, so it misleadingly lacks the cap/drain-holes).
- `docs/mailbox-standoff-grate.md`: added "Test print — dovetail fit check" section + Downloads row.
- (committed as 4ce0f19, direct to main)

## Follow-ups
- [ ] User to reprint H2 for real drainage: Assemble the two objects into one (or print single-color `tileperf-H2.stl`) so the drain holes stay open.
- [ ] Decide whether to document the Assemble-for-through-holes gotcha in the doc's two-color section (offered; user hadn't answered).
- [ ] Dovetail fit-test result still pending (does the 8g strip drop onto H2 snugly at 0.2mm?). Adjust clearance in build_assembly.py if tight/loose.
