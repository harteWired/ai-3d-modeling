@../../CLAUDE.md

# 3D Printing

AI-native 3D modeling pipeline. OpenSCAD parametric models → STL → validation → print.

## Obsidian Vault Integration

Project bridge note: `/workspace/projects/obsidian-vault/vault/projects/3d-printing.md`

**Before starting work:** Check the bridge note for `next-action`, recent log entries, and follow-ups. Notes left between sessions live there, not in this repo.

## Multi-Agent Workflow

This project uses specialized agents for design tasks. See `AGENT-WORKFLOW.md` for the full orchestration guide (agent dispatch rules, complexity tiers, inter-agent communication).

**Quick reference — pipeline stages:** spec-writer → [id-designer*] → modeler → geometry-analyzer → print-reviewer → test-print-planner → shipper

*`id-designer` is the pipeline's only conversational agent. Runs when `spec.json` has `requiresId: true` — aesthetic designs with a face, motif, or visible placement. Produces `designs/<name>/id/brief.md` + pinned mockups. Library of shared aesthetic references lives at `designs/_id-library/`. See `.claude/agents/id-designer.md`.

## Printer: Bambu Lab X1 Carbon

| Spec | Value |
|---|---|
| Build volume | 256 x 256 x 256 mm |
| Nozzle | 0.4 mm |
| Layer height | 0.2 mm default, 0.08-0.28 mm range |
| Material | PLA |

## FDM/PLA Tolerances

| Fit Type | Offset | Use Case |
|---|---|---|
| Press fit | -0.15 mm | Friction-held joints |
| Clearance fit | +0.25 mm | Easy insert/remove |
| Sliding fit | +0.35 mm | Moving parts |
| Hole compensation | +0.4 mm diameter | Bolt/dowel holes |
| Min wall | 1.2 mm (3 perimeters) | Structural walls |
| Max overhang | 45 degrees | Unsupported |
| Max bridge | 10 mm | Horizontal bridging |

## Commands

```bash
sudo bash setup.sh                              # One-time setup
npm install && npm test                          # Install + verify
node bin/validate.js designs/<name>              # Full pipeline
node bin/validate.js designs/<name> --render-only    # Render only
node bin/validate.js designs/<name> --analyze-only   # Skip render
node bin/geometry-analyze.js designs/<name>      # Mesh + slicer analysis
node bin/strain-analyze.js designs/<name>        # Closed-form bending stress + safety factor (opt-in)
node bin/check-assembly.js assemblies/<name>.json    # Assembly check
```

## Gemini MCP

- **`gemini_analyze`** — use for render validation during iteration loops. Pass the rendered PNG path rather than loading the image into Claude's context: `gemini_analyze(prompt="Does this 3D render show a clean, manifold shape with no obvious geometry defects, clipping, or visual artifacts?", files=["/workspace/projects/3d-printing/designs/<name>/render.png"])`. Especially useful in multi-round validation loops where accumulating images would bloat context.

## Conventions

- Each design lives in `designs/<name>/` with `requirements.md`, `spec.json`, `<name>.scad`
- Designs with `requiresId: true` also have `designs/<name>/id/` containing `brief.md`, `moodboard/`, `mockups/`, `conversation-log.md`
- Designs with `requiresStrainAnalysis: true` declare a `loadCase` block in `spec.json` (forces, critical sections, material). `scad-lib/materials.json` provides yield + interlayer-derate defaults for PLA, PLA-CF, PETG. `strain-analyzer` agent runs closed-form beam theory; flags FEA when margin is tight or section isn't a clean prism.
- Shared aesthetic library at `designs/_id-library/` (families, references, lessons) — agent reads at start of ID projects, proposes promotions at end
- OpenSCAD libs in `scad-lib/`: always include `fdm-pla.scad` and `bambu-x1c.scad`
- Use `report_dimensions()` to echo bbox for validation parsing
- OpenSCAD rendering via `cli-anything-openscad` CLI (handles Xvfb internally, JSON output, parallel views)
- Geometry analysis uses trimesh (Python .venv) and optionally PrusaSlicer CLI
- Tests use `node --test` (zero dev deps)
- Always push after committing — git is the revision history
