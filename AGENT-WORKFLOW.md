# Multi-Agent Workflow

This project uses specialized agents to manage context across complex design tasks. Each agent has a focused role, its own context window, and communicates through structured files — not conversation history.

## When to use agents

| Complexity | Criteria | Pipeline |
|---|---|---|
| **Simple** | Single part, ≤5 features, no assembly | `spec-writer` → `modeler` (with inline print check) → `shipper` |
| **Medium** | Single part, >5 features | `spec-writer` → [`id-designer`*] → `modeler` → `geometry-analyzer` → [`strain-analyzer`†] → `print-reviewer` → `test-print-planner` → `modeler` (test pieces) → `shipper` |
| **Complex** | Multi-part assembly | `spec-writer` → [`id-designer`*] → `modeler` (per part, parallel) → `geometry-analyzer` (per part, parallel) → [`strain-analyzer`† per loaded part] → `print-reviewer` + `fit-reviewer` (parallel) → `test-print-planner` → `modeler` (test pieces, parallel) → `shipper` |

*`id-designer` runs when `spec.json` has `requiresId: true` — i.e. designs with a face, motif, or visible placement. Skipped for utility parts (brackets, adapters, internal components). See rule 2 below.

†`strain-analyzer` runs when `spec.json` has `requiresStrainAnalysis: true` and a populated `loadCase` block — i.e. parts under external mechanical load (cantilever holders, brackets, mounts). Skipped for decorative/low-load parts. See rule 4.5 below.

## Model per agent

| Agent | Model | Reason |
|---|---|---|
| `spec-writer` | sonnet | Structured writing from a clear user brief |
| `id-designer` | opus | Aesthetic judgment, conversational design loop with user, open-ended creative decisions |
| `modeler` | sonnet | OpenSCAD generation from a well-defined spec — throughput over judgment |
| `modeler-fusion` | sonnet | Same as modeler |
| `geometry-analyzer` | sonnet | Reading quantitative data, running analysis, interpreting results |
| `strain-analyzer` | sonnet | Running closed-form beam-theory math, interpreting safety factors |
| `print-reviewer` | sonnet | Evaluating reports against known printability rules |
| `fit-reviewer` | sonnet | Dimensional tolerance checking against spec |
| `test-print-planner` | sonnet | Structured output from existing report data |
| `shipper` | haiku | Commit, tag, push — no reasoning required |

When dispatching via the Agent tool, pass `model: 'opus'` for `id-designer`, `model: 'sonnet'` for all others, `model: 'haiku'` for shipper.

## Agent dispatch rules

1. **Spec stage:** Dispatch `spec-writer`. Wait for `requirements.md` + `spec.json` before proceeding.
2. **ID stage (conditional):** If `spec.json` has `requiresId: true`, dispatch `id-designer`. **This is the pipeline's only conversational agent** — it runs a multi-turn mockup-dial-in loop with the user and returns when the user locks the brief. Output is `designs/<name>/id/brief.md` + pinned reference images. For multi-part assemblies, one brief covers the family. Skip if `requiresId: false`. See `.claude/agents/id-designer.md` and `designs/_id-library/README.md`.
3. **Model stage:** Check `spec.json` → `modelingBackend`:
   - `"openscad"` (default, or field absent): dispatch `modeler`. Works headlessly from the devcontainer.
   - `"fusion"`: dispatch `modeler-fusion`. **Requires Fusion 360 running on the Windows host with the MCP add-in active and the `fusion` MCP server connected.** See `docs/fusion-mcp-setup.md`.
   
   Both agents read `spec.json` AND `id/brief.md` (if present) and produce the same outputs: `output/<name>.stl` + `output/modeling-report.json`. Everything downstream is backend-agnostic. For multi-part assemblies, dispatch one modeler per part in parallel. Wait for all to report PASS.
4. **Geometry stage:** Dispatch `geometry-analyzer` per part (parallel for multi-part). Produces `geometry-report.json` (mesh analysis) and `slicer-report.json` (PrusaSlicer G-code analysis, if slicer is installed). These are ground-truth geometry data for the reviewer.
4.5. **Strain stage (conditional):** If `spec.json` has `requiresStrainAnalysis: true`, dispatch `strain-analyzer`. Reads `loadCase` block + `scad-lib/materials.json` and runs closed-form beam-theory math via `node bin/strain-analyze.js`. Produces `output/strain-report.json` + `output/review-strain.md`. The agent appends an interpretive Discussion section to the review and flags FEA escalation when the closed-form margin is tight (SF < 3) or the section isn't a clean prism. Skipped silently if `requiresStrainAnalysis` is absent or false. v1 does not run FEA itself — it only recommends.
5. **Review stage:** Dispatch `print-reviewer` and (if multi-part) `fit-reviewer` in parallel. The print-reviewer now reads quantitative geometry data from the analyzer, not SCAD source. Both are read-only. If either reports FAIL, dispatch `modeler` with the specific fix instructions, re-run geometry analysis, then re-review.
6. **ID critique stage (user-initiated, can repeat):** After render + review — or any time the user looks at renders and wants to iterate aesthetics — dispatch `id-designer` in **critique mode** with the render paths. The agent reads `id/brief.md` + `output/*.png` + `review-printability.md`, runs a critique dialogue, and emits `id/modeler-notes-v<n>.md` plus amendments to the brief's Revisions section. Orchestrator then re-dispatches `modeler` with the fix notes, re-runs geometry + review, and loops. This stage is optional, user-gated, and can run as many rounds as needed. It is also valid **out of flow** — the user can ping `id-designer` directly with render paths to run critique mode without going through the orchestrator.

7. **Test print stage (optional):** Dispatch `test-print-planner` once all reviews pass. It reads the finalized reports, consumes upstream flags (`spec.json` → `testPrintCandidates`, `review-printability.md` → Test Print Recommendations), and produces `test-prints.json` + stub design directories. Then dispatch `modeler` for each test print (parallel). Test prints go through lightweight validation only (render + dimension check), not the full review pipeline. The orchestrator may skip this stage for simple parts or if the user opts out.
8. **Ship stage:** Dispatch `shipper` once all reviews and test prints are complete. For designs that went through the ID stage, the orchestrator should also prompt the user for library-promotion approvals (new family / references / lessons) before shipping — `id-designer` proposes, user decides.

   **Hero render sub-stage:** When `spec.json` has `heroRender.enabled: true`, the shipper produces gallery-quality renders via Blender + Cycles (`bin/render-hero.js`) after the OpenSCAD ship-quality renders. Optional GLB export feeds the in-browser interactive 3D viewer at `docs/viewer.html`. The hero render is for the README + design page header; OpenSCAD renders remain authoritative for technical illustration. Per-design lighting/material overrides go in `designs/<name>/id/render-preset.py` (written by `id-designer` when the brief calls for a specific look). See `.claude/agents/shipper.md` step 1.5.

## Orchestrator responsibilities

The top-level conversation (you, reading this) is the **orchestrator**. You:
- Manage the user dialogue — questions, decisions, design intent
- Dispatch agents and read their **summaries** (not full reports)
- Make go/no-go decisions between stages
- Never hold full SCAD source, review arithmetic, or validation output in your context — that's what the agents are for

## Reference-photo intake — multi-source image registration

When reference **photos** are part of a design's input, never extract a dimension from a
single read. Use a triangulated, multi-method process — this is an orchestrator duty,
before spec-writer.

### Why (blind benchmark, 2026-05-31 — battery-capsule openings vs. user calipers)

Five blind methods measured the capsule openings; scored against calipers
(clear 27.8 × 23.6, teal 27.5 × 23.7 mm):

| Method | Scale basis | MAE (mm) | Max err |
|---|---|---|---|
| gemini-flash | 1 cm mat grid | **2.5** | 4.7 |
| gemini-pro | 1 cm mat grid | 5.65 | 5.8 |
| claude-ruler | mm ruler ticks | 7.6 | 8.3 |
| claude-grid | 1 cm grid + ruler | 7.78 | 9.2 |
| claude-circles | circle templates | 8.03 | 9.0 |

**Variance caveat — the ranking is unstable.** In an ad-hoc read minutes earlier the same
methods flipped: Gemini Flash overshot to ~45 mm (worst) while Claude's grid read landed
~28–32 mm (best) — same images, opposite winner. **Do not crown one method.** The durable
signal: every photo read ran 2.5–8 mm off, and run-to-run spread can exceed the error itself.

### Protocol

1. Run **≥2 independent passes blind** — different model and/or scale basis; neither pass
   sees the other's numbers or any caliper value. Reusable harness: the `Workflow` script
   `image-registration-accuracy` (parallel measure agents → score → protocol).
2. Anchor scale to the **1 cm grid squares** when present — the most consistent reference
   (ruler-tick and circle-template bases fared no better).
3. Triangulate to a per-dimension **median**; treat the inter-pass spread as the uncertainty
   band and carry it into clearance sizing.
4. **Constrain vision agents**: one read per image, no cropping/derivative files, no sub-tool
   calls. Unconstrained agents ballooned to multi-MB transcripts chasing pixel precision.

### Hard rule — fit-critical dimensions

Any bore / pocket / rim the part must mate to **MUST be confirmed with user calipers before
modeling.** Photos may only (a) seed the estimate and (b) size a test-coupon clearance range.
Photo reads run 2.5–8 mm off — beyond any press/clearance tolerance.

## Inter-agent communication

Agents communicate through files in `designs/<name>/`:
```
designs/<name>/
├── requirements.md           ← spec-writer output
├── spec.json                 ← spec-writer output (includes requiresId flag)
├── id/                       ← id-designer output (only if requiresId: true)
│   ├── brief.md              ← authoritative aesthetic spec; appended with Revisions as critiques land
│   ├── moodboard/            ← pinned reference images (design mode)
│   ├── mockups/              ← design-mode iteration history
│   ├── modeler-notes-v*.md   ← per-round critique → modeler fix list
│   ├── critique-v*/          ← optional reaction mockups per critique round
│   └── conversation-log.md   ← dialogue snapshot across all modes and rounds
├── <name>.scad               ← modeler output
├── output/
│   ├── modeling-report.json  ← modeler output (dims + feature inventory)
│   ├── geometry-report.json  ← geometry-analyzer output (mesh analysis)
│   ├── slicer-report.json    ← geometry-analyzer output (PrusaSlicer analysis)
│   ├── strain-report.json    ← strain-analyzer output (raw safety-factor data, only if requiresStrainAnalysis)
│   ├── review-strain.md      ← strain-analyzer output (human-readable, only if requiresStrainAnalysis)
│   ├── validation-report.json ← pipeline output
│   ├── review-printability.md ← print-reviewer output (verbose)
│   ├── review-fitment.json   ← fit-reviewer output
│   ├── test-prints.json      ← test-print-planner output (manifest)
│   ├── *.stl, *.png          ← rendered artifacts
│   └── iterations/           ← round-by-round history
├── test-prints/              ← test print designs (planner + modeler output)
│   ├── <id>/
│   │   ├── requirements.md   ← test-print-planner output
│   │   ├── spec.json         ← test-print-planner output
│   │   ├── <id>.scad         ← modeler output
│   │   └── output/           ← rendered test piece artifacts
```
