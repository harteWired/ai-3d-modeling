---
date: 2026-04-26
project: 3d-printing
type: session-log
---

# 2026-04-26 — ptouch-cradle post-ship cleanup (docs + test prints)

## Quick Reference
**Keywords:** ptouch-cradle, post-ship cleanup, doc audit, stale docs, superseded banners, hollow test prints, hollow-volumes norm, test-print-planner, printer-corner-fit, L-shape test, tray-slot-fit-pair hollow shell, brief.md round-5/6/7 Revisions backfill, conversation-log Turn 12, README hero render swap, fan-tub-adapter v3 stalled banner, humidity-output v1 superseded, caliper-test image link
**Project:** 3d-printing
**Outcome:** After shipping ptouch-cradle v3 (commit 31a2e27), did a post-ship sweep: audited and fixed all stale docs (8 files), hollowed the tray test-piece (saved 70% filament) and codified hollow-volumes as a norm in test-print-planner agent, backfilled rounds 5-7 in id/brief.md Revisions + Turn 12 in conversation-log.md, and added a second test print (printer-corner-fit L-test) for printer-pocket fitment validation. All committed and pushed.

## What Was Done

1. **Doc audit (commit `ea92875`):** delegated to a research agent to scan all 9 design docs in `docs/` + the README. Findings: 5 stale, 1 needing decision, 3 current. Fixed in one commit:
   1. README cradle row — hero render swapped to bare three-quarter (was use-state with printer); description updated to mention the test print; new row added for the stalled fan-tub-adapter v3 proposal so it's no longer orphaned from the gallery.
   2. ptouch-cradle.md — added Test Prints section with the tray-slot-fit-pair link (was missed at ship time since the test print landed in a separate commit after).
   3. humidity-output.md — added "Superseded by V2" banner at top (was reading as current despite the README marking it superseded).
   4. caliper-test.md — fixed image link mismatch (top-down caption was pointing at `caliper-test-front.png` instead of `caliper-test-top.png`).
   5. glitter-wizard-hat.md — pipeline table updated (geometry/print review marked complete instead of "pending"; artifacts existed but the doc lagged).
   6. fan-tub-adapter-v2.md — added v3-proposal cross-reference in the version-banner block.
   7. fan-tub-adapter-v3-proposal.md — added "Status: Stalled" banner at top so readers know it's a forward proposal with stub design dirs only, not current implementation.

2. **Hollow tray test-piece (commit `e6b736e`):** the round-7-shipped tray-slot-fit-pair had the tray slug as a solid 103.2 × 25 × 30 mm cube. User flagged the wasted bulk; rebuilt as a 1.6mm-walled shell with 1.6mm floor, open at the top. The exterior remains identical so fit-test validity is preserved. Volume drop: ~77 cm³ → ~22 cm³ for that piece (~70% reduction).

3. **Hollow-volumes norm (same commit):** added a new simplification principle to `.claude/agents/test-print-planner.md`: "Hollow significant volumes — solid blocks larger than ~2 cm³ that aren't validating bulk-material behavior should always be hollowed. Match the parent design's wall thickness for the shell." Future test prints automatically apply this.

4. **brief.md + conversation-log.md backfilled (same commit):** the brief's main spec block + form-language + features section were stale (round-3-era content describing cable notch, feet, "tray scoop + integrated finger-grip" — all of which were removed/replaced in rounds 5-7). Updated:
   1. hero_views, proportions, fillet_schedule, features, decoration_policy, anti_brief, print_orientation YAML blocks
   2. Form-language prose (removed feet sentence)
   3. Feature-by-feature rationale (replaced scoop+grip section with uniform-low-front-wall + interior-floor-ramp sections; removed foot-to-plate section; updated cable-notch description)
   4. Modeler-notes pointer (v3 → v7 with full version history note)
   5. Appended Round 5 / 6 / 7 Revisions entries (closed-bin restoration; lowered-center cutout; uniform low front wall + r=20 sweeps)
   Conversation log gained Turn 12 covering round-7 land, ship pipeline, test-print addition, doc audit.

5. **Printer-corner-fit L-test added (commit `55053b7`):** user noted that the tray-slot-fit-pair only validates tray-to-slot fit, not printer-to-pocket fit. Built an L-shaped test piece — two perpendicular wall segments forming ONE inside corner of the printer pocket. Long leg 100mm × 3mm × 25mm (along printer's long-axis side), short leg 80mm × 3mm × 25mm (along short-axis side). No floor — the L is rigid enough as printed. ~13 cm³, ~18 min print time. User places the printer's corner against the inside angle and verifies 1mm/side clearance feels right.

6. **All work pushed to origin/main:** verified working tree is clean of design files (only ephemeral lock files + glitter-wizard-hat regenerated geometry report uncommitted). Final HEAD: `55053b7`.

## Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| Audit docs in one shot via a research agent rather than reading each file in main context | Saves main-context tokens; agent's structured report (status + issues per file + recommended action + summary) is exactly the right artifact for batch fixing |
| Add an L-test for printer pocket separately rather than combining with tray test | Different fitment interfaces (tray-to-slot vs printer-to-pocket), different failure modes, different fix paths. One combined test would conflate failure causes |
| L-shape (one corner) vs U-shape (three corners) for the printer test | User specified "L with three corners" (three reference points: two open ends + the inside angle). Single-corner is sufficient — verifies XY clearance on both axes simultaneously, plus tests if printer's corner radius/chamfer clears the cradle's sharp 90° interior corner |
| No floor on the printer-corner-fit L | The L is structurally rigid as printed at 25mm tall × 3mm thick × 80–100mm long. A floor would add ~10 cm³ for no functional benefit. Skip |
| Hollow tray slug uses tray's actual wall_t (1.6mm) and floor_t (1.6mm) | Print behavior matches the real tray (same perimeter count, same first-layer thickness). If thin-wall printability is marginal, it'll surface in the test piece |
| Codify hollow-volumes as test-print-planner principle | Round 1 of any test piece should default to hollowing bulk material. Avoids the "solid block by accident" pattern that wasted 70% of filament on the original tray-slot-fit-pair |
| Backfill brief.md Revisions for rounds 5-7 (rather than just leaving the brief stale) | The brief's Revisions log is the design's design-rationale archive. Future critiques (or readers reviewing the design history) will pull from this — the gap from round 4 to ship was load-bearing context |
| Decision deferred: vent-adapter and fan-tub-adapter-clip-shame orphan dirs | Out of scope for this pass; user said "those are fine" — left them alone |

## Key Learnings

1. **Post-ship sweep is its own work item.** Shipping ≠ done. After v3 hit `main`, there were 5 stale design docs, missing test print, stale brief Revisions, and a wasteful test-print design. None blocking but all leaving the repo in a "not actually current" state. Budget time for post-ship cleanup; don't expect the shipper agent to catch every adjacent file.
2. **Stale docs accumulate when conventions aren't enforced at edit time.** Examples:
   - humidity-output.md was missing a "superseded" banner that fan-tub-adapter.md had — pattern existed but wasn't applied uniformly
   - brief.md's main body wasn't kept in sync with Revisions during rounds 5-7 (only Revisions appended, main body left at round-3 state)
   - caliper-test.md image link was wrong because it was hand-edited at some point
   The fix is either: enforce these via agent definitions / templates, or do periodic doc audits.
3. **Test prints can themselves be wasteful.** The original tray-slot-fit-pair was a solid block — wasted ~55 cm³ of PLA per test print. Codifying "hollow bulk volumes" as a default in the test-print-planner is a small change with compounding savings across future designs.
4. **Two test prints, two failure modes, one bed run.** ~25 cm³ total / ~30 min on a single bed run validates BOTH critical fitment interfaces (tray-to-slot AND printer-to-pocket) before committing to the ~150 cm³ full print. Cheap insurance.
5. **Audit agents work well for systematic doc reviews.** Spawning a general-purpose agent with explicit per-file checklist + reporting format produces an actionable list faster and cleaner than reading each file in main context.

## Solutions & Fixes

1. **Hollow tray slug:** the `mini_tray_section()` module in `tray-slot-fit-pair.scad` was changed from a `linear_extrude` of a solid rounded-rect to a `difference()` between an outer-shell extrude and an interior-cavity extrude. Interior dims: `tray_ext_w - 2 * shell_wall_t` × `test_y_depth - 2 * shell_wall_t` × `tray_ext_h` (open top), with a 1.6mm floor. STL re-rendered.
2. **Cradle hero render in README swap:** image src changed from `cradle-user-front-in-use.png` (with printer proxy) to `cradle-user-front-threequarter.png` (bare). Caption updated to remove "low 25mm bathtub walls frame the printer base" wording.
3. **brief.md form-language section:** the sentence "The feet exist to lift the base off the desk." was deleted because there are no feet in v3. Removed cleanly without re-flowing the surrounding paragraph.
4. **brief.md feature-by-feature section:** entire `### Tray scoop lip + integrated finger-grip` and `### Foot-to-plate upper blend` sections deleted; replaced with `### Tray uniform low front wall + r=20 side fillet sweeps` and `### Tray interior floor ramp` sections describing the round-7 final geometry.
5. **fan-tub-adapter-v3-proposal banner:** added `> **Status: Stalled.** ...` blockquote at the top after the H1, mirroring the pattern fan-tub-adapter.md uses for its frozen-v1 banner.

## Files Modified

**Commits this session:** `ea92875`, `e6b736e`, `55053b7`.

**Doc fixes (`ea92875`):**
1. `README.md` — cradle hero render + caption + test-print mention; new fan-tub-adapter v3 proposal row
2. `docs/ptouch-cradle.md` — Test Prints section + downloads + pipeline table
3. `docs/humidity-output.md` — superseded-by-v2 banner at top
4. `docs/caliper-test.md` — image link `caliper-test-front.png` → `caliper-test-top.png`
5. `docs/glitter-wizard-hat.md` — pipeline table updated
6. `docs/fan-tub-adapter-v2.md` — v3-proposal cross-reference
7. `docs/fan-tub-adapter-v3-proposal.md` — Stalled banner

**Test print + agent norm + brief/log update (`e6b736e`):**
1. `designs/ptouch-cradle/test-prints/tray-slot-fit-pair/tray-slot-fit-pair.scad` — `mini_tray_section()` module rebuilt as hollow shell
2. `designs/ptouch-cradle/test-prints/tray-slot-fit-pair/tray-slot-fit-pair.stl` — re-rendered
3. `.claude/agents/test-print-planner.md` — new "Hollow significant volumes" simplification principle
4. `designs/ptouch-cradle/id/brief.md` — main spec block + form-language + features-section + modeler-notes pointer updated; rounds 5/6/7 Revisions appended
5. `designs/ptouch-cradle/id/conversation-log.md` — Turn 12 appended

**Printer-corner-fit L-test (`55053b7`):**
1. `designs/ptouch-cradle/test-prints/printer-corner-fit/printer-corner-fit.scad` — new
2. `designs/ptouch-cradle/test-prints/printer-corner-fit/printer-corner-fit.stl` — new (rendered)
3. `designs/ptouch-cradle/test-prints/printer-corner-fit/spec.json` — new
4. `designs/ptouch-cradle/test-prints/printer-corner-fit/requirements.md` — new
5. `designs/ptouch-cradle/test-prints/test-prints.json` — added the printer-corner-fit entry alongside tray-slot-fit-pair
6. `docs/ptouch-cradle.md` — Test Prints table updated to 2 entries; Downloads section gained printer-corner-fit STL link; pipeline table gained "2 pieces" mention

**Sessions:**
- `docs/sessions/2026-04-26-07-42-ptouch-cradle-post-ship-cleanup.md` — this log

## Follow-ups

1. **Print both test pieces** before the full cradle/tray print. ~25 cm³ / ~30 min combined on one bed run. Validates tray-slot sliding fit AND printer-pocket corner fit. Adjust XY compensation in Bambu Studio if either fails before committing to the full ~150 cm³ print.
2. **Apply hollow-volumes norm retroactively** to other designs' test prints if any have wasteful solid blocks. Sweep `designs/*/test-prints/*/*.scad` for `linear_extrude` of large solid 2D shapes; replace with hollow-shell construction where appropriate.
3. **Decide fan-tub-adapter v3 fate** at some future point — proposal is now linked from README and has a "Stalled" banner, but the stub design dirs at `designs/fan-tub-adapter-v3-base/` and `designs/fan-tub-adapter-v3-cap/` are dead weight if the proposal is abandoned. Either resume implementation or delete the stubs + proposal doc.
4. **Vent-adapter orphan** at `designs/vent-adapter/` — has no doc, no README row. Decide whether to document, delete, or leave as in-progress scaffolding.
5. **Fan-tub-adapter-clip-shame orphan** at `designs/fan-tub-adapter-clip-shame/` — has SCAD+STL but no doc. Likely an intentional iteration artifact ("shame" suggests a self-deprecating name for an abandoned variant). Confirm and document as such, or delete.
6. **Consider a doc-audit agent** as a periodic sweep — same checklist the research agent used in this session, runnable via a slash command. Catches stale superseded banners, missing test-print mentions, broken image links, etc.
7. **Test-print-planner could automatically generate the printer-pocket-corner test** for any design with a `printer_*` envelope in spec.json. Currently it only generated the tray-slot test from `testPrintCandidates[]`; the printer-pocket corner was a user-spotted gap.

## Errors & Workarounds

1. **Solid tray slug wasn't caught by the test-print-planner.** Round 1 of `tray-slot-fit-pair` produced a solid 103.2 × 25 × 30 mm block via a single `linear_extrude` — wasteful. The planner agent's existing simplification principles ("Extract, don't shrink", "Preserve wall thickness") didn't explicitly require hollowing bulk material when the test only validated exterior dims. **Fix:** added principle #8 ("Hollow significant volumes") to the agent definition. Will catch this pattern by default in future test-print plans.
2. **brief.md drift between rounds.** During rounds 5-7 the conversation focused on per-round modeler-notes-vN.md files; the main brief.md body was never updated to reflect the new geometry. Only the Revisions log got entries. By round 7, the main spec block referenced removed features (cable notch, feet, "integrated finger-grip" scoop) as if they were current. **Fix this session:** rewrote main spec block + form-language + features sections to reflect round-7 final state. **Process fix recommendation:** the id-designer agent should update both the Revisions log AND the affected sections of the main brief whenever a round changes the geometry materially. The current pattern of "append-only Revisions" is good for history but bad for current-state queries.
3. **Stale `## Pipeline` table in glitter-wizard-hat.md.** Said "Geometry — pending" even though `output/geometry-report.json` and `output/review-printability.md` had been generated. The pipeline table is a per-design state summary; it gets stamped at ship time and then drifts as the design accumulates artifacts. **Fix:** updated to "complete" inline; longer-term consideration: either auto-generate this table from the `output/` dir contents or remove it from the doc template.
4. **README cradle row was using the use-state hero (with printer proxy).** That was the right pick at ship time (showed scale + intended use). User preferred the bare three-quarter for the gallery — keeps the README focused on the cradle's own form, not the printer it holds. Swapped image src + caption.

---

## Raw Session Log

(Omitted per "Comprehensive" detail level — Standard preset's structure preserved through Decisions/Learnings/Solutions/Errors sections.)
