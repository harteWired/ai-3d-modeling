---
date: 2026-05-22
project: 3d-printing
type: session-log
---

# 2026-05-22 — GPU autodetect for hero renders + strain-analyzer agent v1

## Quick Reference
**Keywords:** scripts/_render_device.py, CYCLES_DEVICE env var, OPTIX CUDA HIP METAL ONEAPI autodetect, safe CPU fallback, mock-bpy smoke test, workout-dumbbell-concept2 archived, designs/_archive/, strain-analyzer agent v1, requiresStrainAnalysis spec flag, loadCase block schema, scad-lib/materials.json, PLA PLA-CF PETG, interlayer_derate, σ = Mc/I closed-form beam theory, bin/strain-analyze.js, python/strain_analyze.py, solid_rect hollow_rect solid_circle hollow_circle, AGENT-WORKFLOW.md stage 4.5, docs/images/pipeline.svg strain node, workout-dumbbell-holder 15 lb load correction, plug-root SF 45.7, fork-plate-root SF 16.1, FEA stub recommendation, git-publishing README pass, hero render diagram update

**Project:** 3d-printing

**Outcome:** Resumed two threads after a crash. (1) GPU autodetect for Blender Cycles hero renders landed with a centralized `scripts/_render_device.py` helper — `CYCLES_DEVICE` env override, 5-backend autodetect, CPU fallback verified via 11-case mock-bpy smoke test. CPU-only contributors see zero regression. (2) Closed-form strain-analyzer agent v1 shipped end-to-end: spec schema (`requiresStrainAnalysis` + `loadCase`), materials library, Python beam-theory engine, Node CLI, agent definition, pipeline wiring, README + diagram updates. v1 deliverable validated on workout-dumbbell-holder — user flagged the real dumbbell weight is 15 lb, not the stale 1-3 lb in requirements; corrected load gives fork-plate-root SF=16.1× (closed-form floor, ignores buttress reinforcement) which lines up with the print-review's ~25× estimate. workout-dumbbell-concept2 abandoned and archived. Five commits pushed to main.

## What Was Done

1. **Recovered crash context** via the bridge note + `git status` + ls of `scripts/`. Found uncommitted GPU work on disk (4 modified render scripts + new `_render_device.py`) but no strain-analyzer artifacts — that thread hadn't started.

2. **GPU close-out**:
   - Audited `scripts/_render_device.py` for defensive behavior — try/except around bpy import, addon prefs lookup, `compute_device_type` setter, `refresh_devices()`. Every failure path lands on CPU.
   - Built a mock-bpy smoke harness exercising 11 scenarios: no bpy installed, no GPU devices, CUDA available, OPTIX available, `CYCLES_DEVICE=CPU` override, `CYCLES_DEVICE=GPU` with no GPU, invalid env value, missing cycles addon, `compute_device_type` raises, `refresh_devices` raises, bpy ImportError. All 11 PASS with correct CPU fallback.
   - Added a "Cycles compute device" section to README documenting the env var + autodetect probe order.
   - Discovered `render-ptouch-assembly.py` was a separate untracked script (mtime matches the other render-script edits); wired it the same way.
   - Commit `a0c9082` ships the GPU work. Two follow-up commits: `d6e32f5` backfills v3.4 spec.json bbox (38 → 56) + v3.3/v3.4 requirements blocks from the un-committed 2026-05-08 ship, `0f4b6d1` archives `workout-dumbbell-concept2` under `designs/_archive/` with ABANDONED.md (pruned 17 dev iteration PNGs to save ~20 MB; kept final STL/F3D/modeling-report.md).

3. **Strain-analyzer agent scoping**: ran 6 AskUserQuestion checkpoints to lock the design.
   - Failure mode: mechanical load (cantilevers, brackets, holders)
   - Engine: closed-form first, escalate to FEA — but ship v1 with FEA as a stub recommendation only
   - Trigger: opt-in via `requiresStrainAnalysis` spec flag (mirrors `requiresId`)
   - v1 deliverable: re-analyze workout-dumbbell-holder
   - Materials: `scad-lib/materials.json` seeded with PLA, PLA-CF, PETG
   - User briefs me (rather than me drafting a proposal first)

4. **Strain-analyzer agent built end-to-end** (commit `f391d02`):
   - `scad-lib/materials.json` — yield, tensile, Young's modulus, density, `interlayer_derate` per material. Bambu/Polymaker/Prusament-derived figures.
   - `python/strain_analyze.py` — closed-form engine. Section properties for solid/hollow rect + circle. Moment via `r × F` cross product. σ = Mc/I. Allowable σ = yield × interlayer_derate when `layerOrientation: "interlayer"`. Cantilever tip deflection from `F·L³ / (3·E·I)`. FEA recommendation flag when SF < 3 or shape not in closed-form set.
   - `bin/strain-analyze.js` — Node orchestrator matching the `bin/geometry-analyze.js` pattern. Calls `.venv` Python, writes `strain-report.json` + a templated `review-strain.md`.
   - `.claude/agents/strain-analyzer.md` — agent definition with full loadCase schema, layerOrientation guidance, "what this agent does NOT do" (no auto-FEA, no force inference, no STL probing in v1), failure-mode flag list.
   - `AGENT-WORKFLOW.md` — new stage 4.5 between geometry and review, mirroring the requiresId/id-designer conditional pattern. Agent details table updated. Inter-agent communication tree gets strain-report.json + review-strain.md rows.
   - README + CLAUDE.md updated with brief mentions of the new agent + bin command.

5. **v1 deliverable run** (commit `e4f3449`): added `loadCase` block to workout-dumbbell-holder spec.json with 2 critical sections (plug-root hollow_rect 68.5×42.5 wall 3mm; fork-plate-root solid_rect 83.5×12). Initial run with 13.3 N (3 lb dumbbell) gave SF=229 / SF=81 — both PASS but the plug-root number is obviously over-built.

6. **git-publishing README pass** (commit `21e0196`): loaded git-publishing skill section 2 (README structure), section 5 (diagrams), section 8 (voice).
   - README: added strain-analyzer + GPU bullets to "What It Does"; added "Diagrams in this repo" section after the SVG (per Section 5.2 — editorial SVG is the project diagram standard); added strain-analyzer row to the Agent Details table; bumped Pipeline Scaling table; updated Project Structure with strain-report.json + review-strain.md + materials.json; added v4.2 row to Architecture Versions covering both strain and GPU work.
   - `docs/images/pipeline.svg`: added strain-analyzer node at x=520 (between geometry-analyzer x=160 and fit-reviewer x=880) in section 03 // ANALYZE. Conditional green-dashed treatment matching fit-reviewer. New arrow from merge point to strain-analyzer, new arrow from strain-analyzer down to print-reviewer, new `strain-report.json` arrow label. Second footnote line documenting the requiresStrainAnalysis trigger + materials.json input.
   - Rendered a 1920px proof via `cairosvg` (installed in `.venv`) to `docs/images/drafts/pipeline-proof.png` for user review before commit. User approved.

7. **Load correction** (commit `2a86d87`): user flagged that the actual workout dumbbells are 15 lb (66.7 N), not the 1-3 lb in stale v1 requirements. Updated:
   - `spec.json` loadCase: 13.3 N → 66.7 N with comment trail
   - `requirements.md`: load-case bullet, v3 load-case summary, plug-engagement resolved-decisions row — all corrected to ~6500 N·mm moment at the plug root
   - Regenerated strain report: plug-root σ=0.690 MPa SF=45.7×, fork-plate-root σ=1.955 MPa SF=16.1×. Both PASS at minSF=3.0.

## Decisions & Trade-offs

| Decision | Rationale |
|---|---|
| Smoke test GPU helper via mock-bpy harness, not real Blender | Blender not installed in this container. Mocking the bpy interfaces and exercising every failure path is actually a more thorough audit than a single Blender render — 11 scenarios verified vs. 1 real render that would have covered only the CPU path. |
| Archive concept2 under `designs/_archive/` rather than delete | User picked "Archive under output/" — STL/F3D/modeling-report.md keep the Fusion construction notes (Matrix3D tilted-plate trick, YZ sketch coord convention) recoverable for a future tilted-fork design. Dev iteration PNGs (~20 MB across 17 files) dropped because they don't add value long-term. |
| Strain-analyzer v1 ships closed-form only, FEA as a recommendation flag | "Ship v1 fast, decide on FEA backend (CalculiX vs FreeCAD-FEM) as a v2 design choice." Avoids a real install + driver-code investment before knowing if the closed-form numbers are useful enough. The CLI sets `fea_recommended: true` with a reason; agent restates it in plain language. |
| `loadCase` schema declares critical sections explicitly, not auto-extracted from STL | v1 simplicity — user (or upstream agent) declares section shape + dimensions + location + layerOrientation. v2 may add trimesh-based section probing. |
| `layerOrientation` defaults to "interlayer" for v1 dumbbell-holder | Conservative — print-review flagged both sections as worst-case inter-layer tension in plug-vertical print. User can override to "in-plane" if they want the optimistic number. |
| Single materials library at `scad-lib/materials.json`, with per-design `materialOverride` | User picked the library option (vs inline-only or both). Library provides defaults; spec can override any field for filament-specific variants. |
| Pipeline diagram: place strain-analyzer between geometry-analyzer and fit-reviewer in same row | Three-column layout fits in existing ANALYZE section height (no need to bump everything below down by 80 px). Required re-positioning geometry-analyzer (x=280 → x=160) and fit-reviewer (x=760 → x=880) plus rewriting their arrow paths to/from print-reviewer. Conditional green-dashed treatment matches fit-reviewer's pattern. |
| User flagged 15 lb load mid-session — corrected spec.json + requirements + regenerated strain report | The 1-3 lb figure was a stale v1 carryover. Fork-plate-root SF dropped from 81× to 16.1× under the corrected load. Still PASS at minSF=3.0, and the closer number actually validates the strain-analyzer's utility — a wildly over-built SF=80 hides the question of "how much margin do I really have?" |

## Key Learnings

- **Mock-bpy smoke testing is a viable substitute for real Blender** when auditing defensive Blender Python. Inject a fake `bpy` module via `sys.modules` (or a `BadFinder` for ImportError), supply controllable `bpy.context.preferences.addons["cycles"].preferences` with parameterized fail modes, and exercise every catch-block path. Covers more failure modes than a single real render and runs in <1 s.
- **Inter-layer tension is the worst-case stress direction for FDM bending**, and `layerOrientation: "interlayer"` is the right default for plug-vertical or any orientation where the beam axis is parallel to layer planes. Cross-references with `review-printability.md` should agree on which sections are interlayer-loaded.
- **The closed-form SF is a floor, not a ceiling.** Beam theory on a solid_rect ignores buttresses, ribs, fillets — reinforcement that geometry analyzes can't see. For workout-dumbbell-holder fork-plate-root, closed-form gives 16.1× under 15 lb; the print-review's hand estimate of ~25× including buttress/rib credit is plausible. The agent should restate this gap explicitly in its discussion.
- **Stale requirement figures bite.** workout-dumbbell-holder requirements.md had carried the 1-3 lb v1 figure through 3 version amendments without anyone catching that the real dumbbells are 15 lb. The strain agent landing forced the question because the load actually feeds into a calc. Validation pressure → caught a stale spec. Worth doing more of.
- **GitHub SVG caching is a thing.** User reported "diagram on README is old" — GitHub's image-rendering cache can take a few minutes to update even after the underlying SVG commit lands. Hard reload or private window clears it. The commit was live; only the rendered preview lagged.
- **AskUserQuestion checkpoints make agent-scoping go fast.** 6 focused questions resolved the strain-analyzer scope end-to-end (failure mode → engine → trigger → v1 deliverable → FEA v1/v2 split → materials library shape). Beats writing a proposal doc + waiting for review.
- **Pipeline-diagram edits are bounded surgery.** The editorial SVG looks intimidating but adding a node + rewiring 2 arrows + relabeling is ~60 lines of Edit calls. Render proof via cairosvg in `.venv`. ImageMagick `convert` chokes on modern CSS (`letter-spacing`, font fallbacks) — don't use it for editorial SVGs.

## Solutions & Fixes

- **Defensive GPU helper pattern**: every code path that touches Blender's preferences or device enumeration is wrapped in try/except. Failure → `scene.cycles.device = "CPU"` + a one-line `[render-device]` log explaining what fell back and why. The single log line is critical for user trust — silent fallback is worse than a noisy one.
  ```python
  try:
      prefs = bpy.context.preferences.addons["cycles"].preferences
  except (KeyError, AttributeError):
      scene.cycles.device = "CPU"
      print("[render-device] Cycles addon prefs unavailable — using CPU")
      return {"mode": "CPU", "backend": "NONE", ...}
  ```
- **SVG proof rendering**: cairosvg (`pip install cairosvg` in `.venv`) renders modern SVGs faithfully, including the editorial CSS that ImageMagick can't handle:
  ```bash
  .venv/bin/python -c "import cairosvg; cairosvg.svg2png(url='docs/images/pipeline.svg', write_to='docs/images/drafts/pipeline-proof.png', output_width=1920)"
  ```
  Drafts directory is already untracked — proofs land there and don't accidentally commit.
- **Bridge-note next-action updates mid-session**: each crash-resume or thread-switch updates the vault next-action so the next `/resume` starts cleanly. Kept the bridge-note in sync at: (a) after GPU work landed, (b) after concept2 archived, (c) after strain-analyzer scoping, (d) at session end.
- **Pipeline diagram: 3-column ANALYZE layout** — geometry-analyzer at x=160, strain-analyzer at x=520, fit-reviewer at x=880. All three w=240. Centers at 280 / 640 / 1000. Section width is 1200 (x=40 to 1240), so even 120-px gaps. Re-routed arrows: merge point (640, 460) fans to all three at y=540; each analyzer's arrow drops to (640, 688) print-reviewer top. Conditional treatment via stroke="#6fd1b4" stroke-dasharray="6,4" matches the existing fit-reviewer style.

## Files Modified

- `scripts/_render_device.py` — created. Cycles compute device autodetect with safe CPU fallback at every failure point. `CYCLES_DEVICE` env override. One-line `[render-device]` log.
- `scripts/render-{hero,part,assembly,in-use,ptouch-assembly}.py` — wired to `configure_cycles_device()` helper (replaces hardcoded `scene.cycles.device = "CPU"`).
- `scad-lib/materials.json` — created. PLA, PLA-CF, PETG seed values with yield, tensile, Young's modulus, density, interlayer_derate, notes.
- `python/strain_analyze.py` — created. Closed-form beam-theory engine. Handles solid/hollow rect + circle. Cross-product moment resolution. Cantilever deflection. FEA recommendation flag.
- `bin/strain-analyze.js` — created. Node CLI orchestrator, writes `strain-report.json` + templated `review-strain.md`. Matches the `bin/geometry-analyze.js` pattern.
- `.claude/agents/strain-analyzer.md` — created. Agent definition with full loadCase schema, layerOrientation guidance, "v1 does NOT do" scope, failure-mode flag list.
- `AGENT-WORKFLOW.md` — added stage 4.5 (strain), agent-details row, inter-agent-communication tree entries for strain-report.json + review-strain.md.
- `README.md` — multiple updates: What It Does (strain + GPU bullets), How It Works intro (opt-in stages call-out), Diagrams in this repo section, Agent Details table row, Pipeline Scaling table, Project Structure tree, Architecture Versions v4.2 row, Cycles compute device section.
- `CLAUDE.md` — Commands section gains `bin/strain-analyze.js` line; Conventions gains `requiresStrainAnalysis` mention.
- `docs/images/pipeline.svg` — strain-analyzer node added (x=520, y=540, w=240, h=60, conditional green-dashed). geometry-analyzer repositioned (x=280 → x=160). fit-reviewer repositioned (x=760 → x=880). New arrows: merge→strain, strain→print-reviewer. New arrow label `strain-report.json`. Footnote second line for requiresStrainAnalysis.
- `designs/workout-dumbbell-holder/spec.json` — backfilled v3.4 bbox z=56 + description (separate commit). Added loadCase block (initial 13.3 N, corrected to 66.7 N for the 15 lb dumbbell).
- `designs/workout-dumbbell-holder/requirements.md` — backfilled v3.3 + v3.4 amendment blocks. Load-case bullet + v3 load-case summary + plug-engagement resolved-decisions row corrected for 15 lb load.
- `designs/workout-dumbbell-holder/output/{review-strain.md,strain-report.json}` — generated by the strain-analyzer CLI. Regenerated under corrected 15 lb load.
- `designs/_archive/workout-dumbbell-concept2/` — created. ABANDONED.md + final STL + F3D + modeling-report.md + spec.json + requirements.md. Iteration PNGs pruned.
- `vault/projects/3d-printing.md` — `next-action` field updated through the session. Log entry appended (this session).
- `vault/projects/3d-printing/workout-dumbbell-concept2.md` — status changed to `abandoned`, banner added.

## Follow-ups

- [ ] **Print plug-sleeve-stub** for workout-dumbbell-holder v3.4 (HIGH gating, pre-existing). PASS = full v3.4 part is greenlit.
- [ ] **Subagent MCP propagation** — schema for `mcpServers:` in `.claude/agents/*.md` frontmatter so `modeler-fusion` (and any future Fusion-driving subagent) can see `mcp__fusion__*` tools instead of being driven from the main session.
- [ ] **strain-analyzer v2** — real FEA backend (CalculiX or FreeCAD-FEM) for sections where the v1 stub flags `fea_recommended: true` (tight margin or non-prism geometry). Closed-form floor on the dumbbell-holder fork-plate-root is 16.1× but ignores the buttress/rib reinforcement — FEA would recover the true SF.
- [ ] **STL section probing** (strain-analyzer v2) — auto-extract cross-sections from the STL at declared `location_mm` instead of having the user declare width/height. Removes a class of manual-arithmetic errors.
- [ ] **Dynamic loading factor** in loadCase schema — currently the user folds the dynamic factor into `magnitude_N` manually. A `dynamicFactor` field that the agent multiplies in would be cleaner.
- [ ] **ptouch-cradle test pieces** (pre-existing) — print tray-slot-fit-pair + printer-corner-fit before the full v11 cradle/tray run.
