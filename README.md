# AI 3D Modeling

[![by harteWired](https://img.shields.io/badge/by-harteWired-e6a562?style=flat&labelColor=15151e)](https://github.com/harteWired)

Describe a part. Get a printable STL — spec'd, validated, reviewed for printability, and shipped with test prints for critical fitment. No CAD skills required.

This is an AI-native parametric modeling pipeline built on [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with two modeling backends: [OpenSCAD](https://openscad.org/) (headless, git-native, default) and [Autodesk Fusion 360](https://www.autodesk.com/products/fusion-360/) via MCP (organic geometry, freeform surfaces). The human owns the design intent — dimensions, constraints, how things mate. The AI handles the CAD work, iterates against a validation pipeline, and doesn't ship until the geometry passes quantitative review.

**Printer:** Bambu Lab X1 Carbon — 256 × 256 × 256 mm, 0.4 mm nozzle, PLA.

## What It Does

- **Dual modeling backends** — OpenSCAD (headless, git-native, default) for functional and rectilinear geometry; Autodesk Fusion 360 via MCP for organic shapes, compound curves, and freeform surfaces. Both backends produce the same STL + report outputs; everything downstream is backend-agnostic. See [`docs/fusion-mcp-setup.md`](docs/fusion-mcp-setup.md).
- **Industrial design loop** — conversational `id-designer` agent runs a mockup-first aesthetic pass before modeling on visible parts (`requiresId: true`). After renders land, critique mode produces a concrete fix list for the modeler. Shared aesthetic library at `designs/_id-library/`.
- **Ground-truth printability** — trimesh slices the mesh at every layer height; PrusaSlicer confirms support and bridge behavior from actual G-code
- **Automated review** — every overhang, bridge, wall thickness, and mating clearance is checked against FDM/PLA limits before the part ships
- **Closed-form strain analysis** — load-bearing parts (`requiresStrainAnalysis: true`) declare a `loadCase` block; `strain-analyzer` runs beam-theory σ = Mc/I against the declared critical sections and reports safety factors with FDM interlayer derate. Flags FEA when the closed-form margin is tight.
- **Test print planning** — critical fitment interfaces get broken out into minimal-material hollow test pieces so you verify fit before committing to a full print
- **Multi-part assemblies** — interference and fit checks across parts using trimesh + PyVista
- **GPU-aware hero renders** — Blender Cycles auto-detects OPTIX / CUDA / HIP / METAL / ONEAPI and falls back to CPU. Override with `CYCLES_DEVICE`. CPU-only contributors see no regression.

## Designs

| Design | Preview | Arch | Description | STL |
|--------|---------|:----:|-------------|-----|
| [Caterpillar 18650 Holder](docs/caterpillar-18650-holder.md) | ![Top-three-quarter view of the caterpillar 18650 holder — a segmented zig-zag caterpillar body holding six round 18650 wells that alternate up and down the chain, each with a small central nipple-indent at its floor, a rounded head lobe with two eye dimples and two antenna nubs, and a tapered tail](docs/images/caterpillar-18650-holder/caterpillar-18650-holder-hero.png) | v4 (Fusion) | A desk caddy holding 6 bare **18650 cells** upright, shaped as a **zig-zag caterpillar** (derivative of the capsule caterpillar). Six round Ø19.2 mm wells in a nose-to-tail zig-zag chain (±7 mm, ~42° spine), a segmented body with a **head** (eye dimples + antenna nubs) and tapered **tail**. Each socket floor has a **nipple indent** (Ø7 × 1.8 mm) so button-top cells insert **positive-side-down** (negative end up). ~1.5 mm walls; loose drop-in. 119.5 × 45.9 × 24.5 mm, watertight, prints flat support-free. | [STL](designs/caterpillar-18650-holder/output/caterpillar-18650-holder.stl) |
| [Caterpillar Capsule Holder](docs/caterpillar-capsule-holder.md) | ![Top-three-quarter view of the caterpillar capsule holder — a segmented zig-zag caterpillar body holding six deep teardrop sockets that alternate up and down in a nose-to-tail nested chain, with a rounded head lobe bearing two eye dimples and two antenna nubs at one end and a tapered tail at the other](docs/images/caterpillar-capsule-holder/caterpillar-capsule-holder-hero.png) | v4 (Fusion) | A drawer caddy holding 6 battery capsules upright, shaped as a **zig-zag caterpillar**. The six teardrop sockets are strung into a nose-to-tail nested chain that zig-zags (±10 mm, ~42° spine), giving a segmented body with a rounded **head** (eye dimples + antenna nubs) and a tapered **tail**. Tightly packed (~1.45 mm walls); capsules drop in either end up, outer-grip only (never the bore). 169 × 61.5 × 24.5 mm, watertight, prints flat sockets-up support-free. | [STL](designs/caterpillar-capsule-holder/output/caterpillar-capsule-holder.stl) |
| [Battery Capsule Holder (Fusion)](docs/battery-capsule-holder-fusion.md) | ![Top-three-quarter view of the Fusion battery capsule holder — a soft-filleted rounded-rectangle slab with six deep teardrop sockets in a staggered interlocked layout, alternate pockets flipped 180° so their pointed ends nest into the wedge gaps beside neighbouring fat ends](docs/images/battery-capsule-holder/battery-capsule-holder-fusion-hero.png) | v4 (Fusion) | _**One-shot model test** — generated in a single modeling pass, no design iteration._ **Clean-room** independent redesign of the same 6-capsule drawer rack — built in Fusion by an agent walled off from the OpenSCAD solution (it never saw the `.scad`/spec/renders, only the problem brief). A soft-filleted **rounded slab** (vs the organic dune-hull): 80.4 × 73.9 × 21 mm, six 18 mm teardrop sockets in a staggered interlocked layout, 1 mm × 45° lead-in chamfers, four ⌀15 rubber-pad foot recesses. Converged independently with the OpenSCAD build on the fit-critical numbers (0.35 mm clearance, 2.0 mm min wall). | [STL](designs/battery-capsule-holder-fusion/output/battery-capsule-holder-fusion.stl) |
| [Battery Capsule Holder (OpenSCAD)](docs/battery-capsule-holder-openscad.md) | ![Isometric view of the battery capsule holder — an organic superellipse blob rack with six nested teardrop sockets, alternate ones flipped 180° so their points tuck into neighbours' round-back gaps; the dune-hull body swells at the base and draws inward toward the chamfered socket mouths](docs/images/battery-capsule-holder/battery-capsule-holder-iso.png) | v4 (OpenSCAD) | _**One-shot model test** — generated in a single modeling pass, no design iteration._ Organic drawer rack holding 6 battery capsules upright, beaker-rack style. Outer-grip-only blind sockets (18 mm) never touch the capsule bore; capsules drop in either end up. Densely **nested teardrops** (alternate rows rotated 180°), a non-rectangular superellipse base, walls that swell at the base and ramp inward to 1.5 mm chamfer lead-ins, and four non-slip foot recesses. Dims from user calipers. **Sibling [Fusion build](docs/battery-capsule-holder-fusion.md)** tackles the same brief a different way. | [STL](designs/battery-capsule-holder/output/battery-capsule-holder.stl) |
| [Workout Dumbbell Holder](docs/workout-dumbbell-holder.md) | ![Top-threequarter view of the workout dumbbell holder — sleeve cube wraps the treadmill rail extrusion (with the −X short wall cut for console clearance, visible as the chamfered front-left edge); horizontal cantilever fork plate extending up-right with the R23 saddle slot opening at the top edge; r=22 quarter-cylinder buttresses smooth the fork-sleeve junction; arc-shaped reinforcing ribs along the fork underside](docs/images/workout-dumbbell-holder/workout-dumbbell-holder-iso.png) | v4 (Fusion) | Clip-on holder for a vertical treadmill rail extrusion. Dual engagement — plug inside the rail, sleeve around the outside — with a horizontal slot through which the dumbbell shaft hangs vertically along the rail. Top + bottom r=22 buttresses, ribs along the fork bottom, sleeve −X wall removed for control-panel clearance. **First design routed to the Fusion 360 MCP backend.** 3 test prints modeled. | [STL](designs/workout-dumbbell-holder/output/workout-dumbbell-holder.stl) · [F3D](designs/workout-dumbbell-holder/output/workout-dumbbell-holder.f3d) |
| [P-touch Cradle](docs/ptouch-cradle.md) | ![Two-part assembly hero render — warm mocha cradle with light cream tray pulled forward in the label-catch position. Three-quarter view reads the tray's r=20 S-curve side sweeps, low front wall, and r=1.6mm rolled top-edge fillet. Blender Cycles, complementary-beige PLA palette.](docs/images/ptouch-cradle/assembly-hero.png) | v4 | Quiet two-part desk dock for Brother PT-P750W. Symmetric 25mm bathtub cradle holds printer; removable tray catches auto-cut labels. No decoration — clean fillets, S-curve corner sweeps on the tray, top-edge fillet r=wall_t aligned across both parts. 2 test prints (tray-slot fit + printer-pocket U-fit). | [Cradle](designs/ptouch-cradle/output/cradle.stl) · [Tray](designs/ptouch-cradle/output/tray.stl) |
| [Glitter Wizard Hat](docs/glitter-wizard-hat.md) | ![Conical wizard hat cap for vintage lava lamps with single row of alternating star and moon cutouts near the base](docs/images/glitter-wizard-hat/gwh-large-iso.png) | v4.1 | Replacement cap for vintage Glitter Wizard lava lamps. Hollow cone with star/moon cutouts, retention lip for bottle neck fit. Two sizes: large (114.3 mm) and small (95 mm). | [Large](designs/glitter-wizard-hat/output/glitter-wizard-hat-large.stl) · [Small](designs/glitter-wizard-hat/output/glitter-wizard-hat-small.stl) |
| [Caliper-Test Gridfinity Bin](docs/caliper-test.md) | ![Gridfinity 2x1 bin with two-stage caliper pocket — wide display cavity at bottom, narrow beam slot at top, 45-degree finger-relief chamfer at opening](docs/images/caliper-test/caliper-test-iso.png) | v4 | Gridfinity 2×1 12u bin for a 6-inch digital caliper. Two-stage contoured pocket seats the display body; the beam extends above the rim for grab-and-go access. 4 test prints for fitment verification. | [STL](gridfinity-bins/designs/caliper-test/output/caliper-test.stl) |
| [Waffle Caulk Spudger](docs/waffle-caulk-spudger.md) | ![Caulk spreader tool for waffle-grid bin lid channels — convex spreader tip, taper zone, and ergonomic handle](docs/images/waffle-caulk-spudger/waffle-caulk-spudger-iso.png) | v4 | Handheld caulk spreading tool for 9.4 mm waffle-grid channels. Convex tip profiles a smooth bead for adapter bonding. No supports, prints flat. | [STL](designs/waffle-caulk-spudger/output/waffle-caulk-spudger.stl) |
| [Humidity-Output V2](docs/humidity-output-v2.md) | ![Humidity duct mount V2 — spigot with lead-in taper and foam seal zone](docs/images/humidity-output-v2/humidity-output-v2-iso.png) | v4 | 4" flex duct mount for HDPE tub lids. Spigot with EPDM foam seal, zip-tie clamping, lead-in taper. 2 test prints for fitment verification. | [STL](designs/humidity-output-v2/output/humidity-output-v2.stl) |
| [Humidity-Output V1](docs/humidity-output.md) | ![Humidity duct mount V1 — original spigot design](docs/images/humidity-output/humidity-output-iso.png) | v1 | Original duct mount — superseded by V2 (spigot was oversized, no lead-in taper, fins started mid-air). | [STL](designs/humidity-output/output/humidity-output.stl) |
| [Fan-Tub Adapter v2.0](docs/fan-tub-adapter-v2.md) | ![Fan-tub adapter base plate with snap-fit clip system](docs/images/fan-tub-adapter-base/fan-tub-adapter-base-iso.png) | v1 | 119mm fan mount for Martha tent lids. Two-part snap-fit — base plate caulked to lid, retention clip with cantilever arms. Zero fasteners. | [Base](designs/fan-tub-adapter-base/output/fan-tub-adapter-base.stl) · [Clip](designs/fan-tub-adapter-clip/output/fan-tub-adapter-clip.stl) |
| [Fan-Tub Adapter v1.0](docs/fan-tub-adapter.md) *(frozen)* | ![Original single-piece fan mount with bolt-on design](docs/images/fan-tub-adapter/fan-tub-adapter-iso.png) | v1 | Original bolt-on fan mount. Y-branch waffle engagement, hex nut counterbores, thumbscrew attachment. Superseded by v2.0. | [STL](designs/fan-tub-adapter/output/fan-tub-adapter.stl) |
| [Fan-Tub Adapter v3.0](docs/fan-tub-adapter-v3-proposal.md) *(proposal — stalled)* | — | v4 | Shroud-cap + guided-snap proposal addressing v2 flimsiness. Design dirs stubbed (`requirements.md` + `spec.json` only); implementation paused. Forward-looking only. | — |

## How It Works

Specialized agents split the work — each owns a stage, communicates through structured files, and never sees the full conversation history. The orchestrator (top-level Claude session) manages user dialogue and dispatches agents. Two stages are opt-in via spec flags: `id-designer` (aesthetic loop, `requiresId`) and `strain-analyzer` (mechanical safety factor, `requiresStrainAnalysis`).

![AI 3D Modeling Pipeline — spec-writer creates requirements; modeler / modeler-fusion generate geometry with optional id-designer for aesthetic passes. geometry-analyzer slices the mesh; fit-reviewer checks multi-part assemblies; strain-analyzer runs closed-form beam-theory on load-bearing parts. print-reviewer gates on FDM limits — pass continues to test-print-planner, fail loops back to modeler. test modeler produces test pieces; shipper publishes via Blender hero renders.](./docs/images/pipeline.svg)

**Diagrams in this repo:**

- [`docs/images/pipeline.svg`](docs/images/pipeline.svg) — editorial SVG pipeline overview (above). Authoritative architecture diagram, kept in sync with `AGENT-WORKFLOW.md`.
- Per-design hero renders live under [`docs/images/<design>/`](docs/images/) — Blender Cycles, catalog-style preset (`scripts/_render_device.py` + `scad-lib/blender-presets/studio.py`).
- Diagram style: editorial SVG for the pipeline; Mermaid for any inline control-flow snippets in design docs. No ASCII diagrams in published READMEs.

<details>
<summary><b>Agent details</b></summary>

| Agent | What it does | Key outputs |
|-------|-------------|-------------|
| **spec-writer** | Turns user intent into structured requirements. Flags tight tolerances, printability risks, test print candidates. Sets `modelingBackend`, `requiresId`, `requiresStrainAnalysis`. | `requirements.md`, `spec.json` |
| **id-designer** | Conversational industrial-design agent. Two modes: *design* (mockup-first aesthetic loop before modeling) and *critique* (post-render fix list after each iteration). Only runs when `requiresId: true`. | `id/brief.md`, `id/modeler-notes-v*.md` |
| **modeler** | Writes OpenSCAD, iterates against validation until PASS. Reads `id/brief.md` as the aesthetic contract. Produces a feature inventory in print-Z order for the reviewer. | `<name>.scad`, `modeling-report.json` |
| **modeler-fusion** | Builds geometry in Autodesk Fusion 360 via MCP. Same input/output contract as **modeler**; used when `modelingBackend: "fusion"` for organic shapes (lofts, sweeps, T-splines). Exports STL + F3D. | `output/<name>.stl`, `modeling-report.json` |
| **geometry-analyzer** | Slices the rendered STL at every layer height (trimesh). Optionally runs PrusaSlicer for G-code-level bridge/support analysis. Works on STL regardless of modeling backend. | `geometry-report.json`, `slicer-report.json` |
| **strain-analyzer** | Closed-form beam-theory on declared critical sections. Reports σ = Mc/I, allowable stress (with FDM interlayer derate), safety factor, tip deflection. Flags FEA when the closed-form margin is tight or the section isn't a clean prism. Only runs when `requiresStrainAnalysis: true`. | `strain-report.json`, `review-strain.md` |
| **print-reviewer** | Checks every feature transition, overhang, bridge, wall thickness, and mating clearance against FDM limits. Classifies bridges as functional or avoidable. Read-only. | `review-printability.md` |
| **fit-reviewer** | Mesh-based interference and clearance checks for multi-part assemblies. | `review-fitment.json` |
| **test-print-planner** | Identifies critical geometries — tight fitment, near-limit overhangs, novel features — and specs minimal-material test pieces. Hollow volumes by default. | `test-prints.json`, stub design dirs |
| **shipper** | Renders views, writes the GitHub design page, updates README, commits, pushes. | `docs/<name>.md`, committed artifacts |

</details>

<details>
<summary><b>Pipeline scaling by complexity</b></summary>

| Complexity | Criteria | Pipeline |
|---|---|---|
| **Simple** | Single part, ≤5 features | `spec-writer` → `modeler` → `shipper` |
| **Medium** | Single part, >5 features | Full pipeline with geometry analysis, print review, test prints; `strain-analyzer` if load-bearing |
| **Complex** | Multi-part assembly | Parallel modelers + analyzers, fit-reviewer added, parallel test prints; `strain-analyzer` per loaded part |

</details>

### Ground-truth geometry — not source code inference

The old approach — inferring printability from SCAD source — doesn't work. The mesh is the ground truth; the source code is a recipe that may not produce what you expect.

The geometry analyzer slices the actual STL at 0.2mm intervals, computing per-layer cross-sections, overhang faces, bridge spans, and wall thickness. The optional slicer pass runs PrusaSlicer (same engine as OrcaSlicer — Slic3r → PrusaSlicer → BambuStudio → OrcaSlicer lineage) and parses the G-code for support material and bridge moves. The print reviewer consumes this quantitative data, not SCAD arithmetic.

### Test prints — verify before you commit

Mating interfaces with tight clearances get test prints automatically. A 90° arc section of a spigot costs a fraction of the material and prints in minutes — enough to trial-fit against the real duct and know if the OD is right before burning hours on the full part.

## Quick Start

```bash
# One-time setup (installs OpenSCAD, Xvfb, cli-anything-openscad, Python venv, PrusaSlicer)
sudo bash setup.sh
npm install

# Validate an existing design
node bin/validate.js designs/humidity-output-v2

# Run geometry analysis
node bin/geometry-analyze.js designs/humidity-output-v2 --skip-slicer

# Closed-form strain analysis (opt-in: requires `requiresStrainAnalysis: true` + `loadCase` in spec.json)
node bin/strain-analyze.js designs/workout-dumbbell-holder

# Check a multi-part assembly
node bin/check-assembly.js assemblies/<name>.json
```

> [!IMPORTANT]
> `setup.sh` requires sudo — it installs system packages and creates a Python venv. Run it once per environment.

### Cycles compute device (hero renders)

Blender hero renders auto-detect a GPU and fall back to CPU when none is available. Override via the `CYCLES_DEVICE` environment variable:

```bash
CYCLES_DEVICE=CPU   blender --background --python scripts/render-hero.py -- ...   # force CPU
CYCLES_DEVICE=GPU   blender --background --python scripts/render-hero.py -- ...   # autodetect best GPU
CYCLES_DEVICE=OPTIX blender --background --python scripts/render-hero.py -- ...   # pin a specific backend (CUDA | HIP | METAL | ONEAPI)
```

With no env var the probe order is OPTIX → CUDA → HIP → METAL → ONEAPI; first working device wins, otherwise CPU. Every render prints a single `[render-device]` line showing what was picked.

## Project Structure

```
designs/<name>/
├── requirements.md          # What to build (from spec-writer)
├── spec.json                # Validation targets + tolerances
├── <name>.scad              # Parametric OpenSCAD source
├── output/
│   ├── <name>.stl           # Print-ready mesh
│   ├── geometry-report.json # Mesh analysis (trimesh)
│   ├── strain-report.json   # Beam-theory safety factor (if requiresStrainAnalysis)
│   ├── review-printability.md
│   ├── review-strain.md     # Human-readable strain review (if requiresStrainAnalysis)
│   └── test-prints.json     # Test print manifest
└── test-prints/             # Minimal-material test pieces
    └── <id>/                # Each gets its own modeler run

scad-lib/
├── fdm-pla.scad             # FDM/PLA tolerance constants
├── bambu-x1c.scad           # Build volume assertions
├── materials.json           # Yield, modulus, FDM interlayer derate per material
└── common.scad              # fdm_hole(), chamfer_cylinder(), etc.
```

## FDM/PLA Tolerances

Every design includes `fdm-pla.scad`. These are the constants — derived from real prints on the X1 Carbon.

| Fit Type | Offset | Use Case |
|----------|--------|----------|
| Press fit | −0.15 mm | Friction-held joints |
| Clearance fit | +0.25 mm | Easy insert/remove |
| Sliding fit | +0.35 mm | Moving parts |
| Hole compensation | +0.4 mm diameter | Bolt holes, dowel holes |
| Min wall | 1.2 mm (3 perimeters) | Structural walls |
| Max overhang | 45° | Unsupported overhangs |
| Max bridge | 10 mm | Horizontal spans |

## Architecture Versions

| Version | Name | What changed |
|---------|------|-------------|
| **v1** | Monolithic | Single CLAUDE.md, inline printability review, no ground-truth geometry |
| **v2** | Multi-agent | Specialized agents with file-based handoff. Print reviewer reads SCAD source — better, but still inferring |
| **v3** | Ground-truth geometry | geometry-analyzer produces mesh-based reports. Reviewer consumes quantitative data, not source code |
| **v4** | Test print planning | test-print-planner identifies critical geometries. Upstream agents flag candidates. Avoidable bridges get flagged, not silently passed |
| **v4.1** | CLI-Anything integration | OpenSCAD rendering via `cli-anything-openscad` Python CLI — parallel views, JSON output with auto-parsed dimensions, thread-safe Xvfb. Replaces direct subprocess management |
| **v4.2** | Strain analysis + GPU renders | `strain-analyzer` adds closed-form bending stress + safety factor as an opt-in pipeline stage (`requiresStrainAnalysis` flag, `loadCase` block in spec.json, `scad-lib/materials.json` library). Blender Cycles renders pick GPU via `CYCLES_DEVICE` autodetect with safe CPU fallback for contributors without a GPU |

## License

MIT
