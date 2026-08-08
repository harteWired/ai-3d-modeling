---
date: 2026-05-08
project: 3d-printing
type: session-log
---

# 2026-05-08 — Dumbbell holder v3.4 ship + hero render style overhaul

## Quick Reference
**Keywords:** workout-dumbbell-holder, v3.4, dual-engagement, plug + sleeve, fork plate, R23 saddle, top + bottom buttress r=22, ribs along fork bottom, sleeve −X wall removed, control-panel clearance, Fusion 360 MCP backend, fusion360-mcp-server, mcp__fusion__execute_code, direct add-in TCP protocol, {"type": "<cmd>", "params": {...}}, atomic clear+build+export pattern, subagent MCP propagation gap, geometry-analyzer, print-reviewer, test-print-planner, plug-sleeve-stub, fork-plate-sample, buttress-arc-sample, github publish, hero render style, scad-lib/blender-presets/studio.py, catalog backdrop, warm beige PLA, Catmull-Clark blob failure, limited dissolve only, back-top-threequarter angle, complex-features-toward-camera

**Project:** 3d-printing

**Outcome:** Shipped workout-dumbbell-holder v3.4 — first design routed through the Fusion 360 MCP backend, iterated through 4 user-driven shape revisions (v1 perpendicular-shaft → v2 parallel-shaft → v3 sleeve+lowered-fork+control-panel-cut → v3.1 −X wall cut → v3.2 top buttress → v3.3 sleeve grow + bottom buttress + ribs → v3.4 curved-fin ribs + recentered cantilever). Modeled 3 test prints (plug-sleeve-stub, fork-plate-sample, buttress-arc-sample). Published the entire design to GitHub (README design table row, full design doc at `docs/workout-dumbbell-holder.md`, hero renders at `docs/images/workout-dumbbell-holder/`). Replaced the project's default Blender hero-render preset (`scad-lib/blender-presets/studio.py`) from dark-studio to catalog-style with warm beige PLA, soft 2-light setup, light cyc, Filmic tone mapping, and limited-dissolve mesh cleanup — driven by user feedback that the original renders sucked.

## What Was Done

1. **Resumed prior session** via /resume; loaded the workout-dumbbell-holder spec (locked at last session, modelingBackend=fusion, all 7 spec questions resolved).

2. **Tried to dispatch modeler-fusion subagent — halted three times** because Claude Code does not propagate MCP servers (`mcp__fusion__*`) into subagent tool registries. Removing the `tools:` allowlist from the agent definition didn't help (subagents don't inherit MCP servers in any configuration we tried). Switched to driving Fusion from the main session.

3. **Bridge debugging** — fusion360-mcp-server v1.27.0 was sending `{"command": ...}` payloads but the current Fusion add-in expects `{"type": "<cmd>", "params": {...}}`. Probed the add-in protocol manually via raw TCP; once the format was figured out, used a small Python helper (`/tmp/fusion_call.py`) to bypass the wedged MCP server entirely. Bridge restoration also required the user to: re-enable the Fusion add-in, fix Windows portproxy rules (Default Switch IP changed 172.28.144.1 → 172.31.144.1 on reboot), and stop the belfry daemon that had taken port 9876.

4. **Built workout-dumbbell-holder iteratively v1 → v3.4** in Fusion via direct add-in protocol:
   - v1: vertical fork U-saddle (shaft perpendicular to rail)
   - v2: rotated saddle 90° to horizontal plane, shaft parallel to rail through plate slot, cradle reach 70 mm
   - v3: added external sleeve (dual-engagement), lowered fork to 20 mm below rail-top, cradle reach increased to 90 mm to clear bell-flange interference
   - v3.1: cut sleeve −X short wall for treadmill console clearance (per reference photo)
   - v3.2: added r=22 top buttress (gusset from flange-top-edge to fork-top)
   - v3.3: extended sleeve down 18 mm, added symmetric r=22 bottom buttress, added 2 ribs along fork bottom (rectangular)
   - v3.4: reshaped ribs to curved-fin profile (3-point arc tapering full depth at inner end → zero at outer end), recentered cantilever in X (cut +X overhang to match −X cut so tine walls are symmetric 4.7 mm)
   - Final volume 253.5 cm³, bbox 88.5 × 141.25 × 56 mm

5. **Ran reviews on v3.4** — geometry-analyzer (PASS: watertight, all walls ≥3mm CF floor, all clearances exact at 1mm/side both interfaces, R=23 saddle exact) and print-reviewer (PASS-WITH-CONDITIONS: plug-vertical orientation recommended; 3 unavoidable functional bridges; CF safety factor >25×; 3 conflicts flagged for user — bell-rest support marks, sleeve cavity cleaning, flange −X clearance question).

6. **Published v3.4 to GitHub** (commit `d004053`):
   - `designs/workout-dumbbell-holder/` — spec.json (v3.4) + requirements.md + 17 output/test-print files
   - `docs/workout-dumbbell-holder.md` — full design doc (geometry overview, dimensions, dual-engagement rationale, control-panel clearance, print orientation, test prints, full v1 → v3.4 iteration history)
   - `README.md` — added a row in the Designs table tagged "v4 (Fusion)"

7. **Modeled 3 test prints in Fusion** (commit `fc821f9`):
   - plug-sleeve-stub (HIGH, 91.3 cm³): full plug (hollowed, 3mm walls) + flange + 25 mm sleeve, −X wall cut
   - fork-plate-sample (MEDIUM, 61.4 cm³): Y-truncated fork plate + both buttresses + 3 mm base plate
   - buttress-arc-sample (LOW, 3.7 cm³): 20 mm X-slice of top buttress + base plate
   - Each modeled via single atomic execute_code call (clear + build + inline export + base64 return) because the saved Fusion file kept auto-restoring v3.4 between separate operations.

8. **OOPS** — the atomic clear+build approach overwrote the user's saved Fusion file ("2026-05-08 First viable plug v1") with the buttress-arc-sample. Restored by using `app.importManager.importToTarget` to open the v3.4 F3D archive as a new "Untitled" document; user can save-as over the corrupted file.

9. **Initial hero renders** (commit `1fe7c16`): rendered 4 PNGs at standard quality (Cycles 128 samples, OIDN denoiser) using the existing dark-studio preset. Top-threequarter chosen for the main part after iso/threequarter/front-threequarter all hid the cantilever behind the sleeve cube.

10. **User reaction to renders: "These suck"** — pointed at the ptouch-cradle assembly-hero style. Took those notes (light cyc, warm two-tone PLA, soft 2-light setup, mesh cleanup) and rewrote `scad-lib/blender-presets/studio.py` as the project default. **Catmull-Clark subsurf modifier melted the blocky dumbbell holder into a blob** on first try — dropped subsurf, kept limited-dissolve + auto-smooth. Re-rendered all 4 PNGs (commit `f7e108c`).

11. **User: "rotate hero 180° to show the cutout, always orient for complex features"** — added `back-top-threequarter` angle preset (180° flip of `top-threequarter` about Z, location `(-1.4, 1.8, 1.7)`), re-rendered main part. Now shows cantilever in foreground with both buttress curves visible and the −X cut as the gap on the right (commit `5b75144`). Saved feedback memory: always orient hero renders to put cuts/curves/asymmetries toward the camera.

## Decisions & Trade-offs

| Decision | Rationale |
|---|---|
| Drive modeler-fusion from main session, not subagent | Subagents don't see `mcp__fusion__*` tools; tried `tools: ..., mcp__fusion__*` (wildcard not supported) and removing `tools:` entirely (MCP servers don't propagate). Main-session driving works. |
| Bypass fusion360-mcp-server v1.27.0 with raw TCP | The MCP server's payload format diverged from the Fusion add-in's expected `{"type": ..., "params": {...}}` shape. Direct TCP at `host.docker.internal:9876` works fine. |
| Single atomic clear+build+export per test print | Fusion's saved file was auto-restoring v3.4 between separate execute_code operations, wiping in-progress geometry. One-shot atomic builds avoid the race. |
| Cradle reach increased 70 → 90 mm in v3 | With cradle reach 70, the upper bell (D=111) extends to Y=14.5–125.5 and overlaps the flange/sleeve at Y=14.5–31.25, Z=−2 to −8. Increasing reach to 90 puts bell inner edge at Y=34.5, clearing the flange by 3.25 mm. |
| Sleeve −X wall removed (and corners) | Treadmill console abuts rail on −X side per reference photo. Cut at X=[−44.25, −39.25], full Y, Z=[−56, −8] gives a clean C-shape sleeve with 5 mm clearance from where the wall used to be. |
| Buttress at r=22 (chosen radius) | Rolls smoothly from flange-top edge (Z=0) down to fork-top (Z=−22) — exactly 22 mm, so the tangent points sit on the existing edges with no awkward intersection. |
| Bottom buttress mirror about Z=−28 (mid-fork) | Symmetric reinforcement under the cantilever. Required growing sleeve from 30 mm length to 48 mm so there's enough Z-space below the fork for the r=22 arc to land on the sleeve-bottom edge. |
| Recentered cantilever (cut +X to match −X cut) | After v3.1 the cantilever was asymmetric: 4.7 mm tine wall on −X, 9.7 mm on +X. Cutting +X overhang restores symmetry to 4.7 mm each side. Affected fork plate, both buttresses, and both ribs. |
| Drop Catmull-Clark subsurf from studio.py preset | First attempt melted the dumbbell holder's orthogonal walls into a rounded blob — Catmull-Clark treats every edge as smooth without crease info. Limited-dissolve + auto-smooth at 30° is enough for blocky parts; organic parts can opt in via `id/render-preset.py`. |
| `back-top-threequarter` angle for the main hero | Default `top-threequarter` put the sleeve cube in front and hid the cantilever + −X cut behind it. 180° flip about Z puts the distinctive features in the foreground. |

## Key Learnings

- **Subagent MCP propagation gap.** Claude Code does not propagate MCP servers from a parent session to subagents — neither `tools:` allowlist with `mcp__fusion__*` (wildcard not supported) nor removing the `tools:` field entirely grants the subagent visibility. Outstanding fix needed in `.claude/agents/modeler-fusion.md`: probably an `mcpServers:` field, schema TBD.
- **Fusion add-in protocol** is `{"type": "<cmd>", "params": {<args>}}\n` over plain TCP at `host.docker.internal:9876`. Returns `{"status": "success", "result": {...}}` or `{"status": "error", "message": "..."}`. The fusion360-mcp-server we have ships with a different (older?) schema and silently returns garbled responses.
- **Fusion's saved-file auto-restore can wipe your in-memory work.** When using a saved Fusion document as a scratch space, separate execute_code operations may restore the saved state between them. Use single atomic execute_code calls or operate on a fresh Untitled document.
- **Catmull-Clark subsurf is a hammer that breaks every nail.** It rounds all edges, including the orthogonal walls and corners that should stay sharp. Without edge crease tagging it's destructive on blocky CAD geometry. Limited dissolve + auto-smooth is the safe default.
- **Hero render angle matters more than the render style.** A great preset rendered at the wrong angle hides the interesting features. Always inventory the part's distinctive features before picking the camera direction; pick a position that puts them toward the camera.
- **belfry on port 9876** — the user's Telegram-to-Claude bridge daemon (separate project) bound the same port the Fusion bridge needs. Took most of an hour to diagnose because the symptoms looked like add-in misbehavior.
- **Windows portproxy rules go stale on reboot.** Default Switch IP can shift (e.g. 172.28 → 172.31), invalidating port forwards. `fusion-mcp-bridge.ps1 -Port 9876` re-discovers and rebuilds the rules.
- **Volume estimates from the test-print-planner agent ran low.** Planner estimated 35 cm³ for plug-sleeve-stub; actual is 91 cm³ (flange alone is 44 cm³). Same pattern for fork-plate-sample (planner 25 → actual 61). Future runs should validate the estimate by computing the included features rather than top-down guessing.

## Solutions & Fixes

- **Bridge debugging end-to-end probe** (recipe for next time):
  ```python
  import socket, json
  s = socket.socket(); s.settimeout(5)
  s.connect(('host.docker.internal', 9876))
  s.sendall(json.dumps({"type": "ping", "params": {}}).encode() + b'\n')
  print(s.recv(4096))   # PASS = {"status": "success", "result": {"pong": True}}
  ```
- **Restore overwritten Fusion saved file** via `app.importManager.importToTarget(opts, target)` from the F3D archive at `C:\workspace\projects\3d-printing\designs\workout-dumbbell-holder\output\workout-dumbbell-holder.f3d` (the v3.4 export landed on Windows side via Fusion's exportManager).
- **Files transfer container ↔ Windows.** The container's `/workspace` is NOT bind-mounted from `C:\workspace\` — they are separate filesystems. To move files: have Fusion `exportManager.execute()` write to `C:\workspace\...`, then in the same atomic `execute_code` read the file as bytes, base64-encode, return as the last expression. Decode on the container side.

## Files Modified

- `designs/workout-dumbbell-holder/spec.json` — version bumped through v1 → v3.4, all params for sleeve / fork-offset / buttresses / ribs / recentering captured.
- `designs/workout-dumbbell-holder/requirements.md` — appended v3 Amendment block + v3.1/v3.2/v3.3/v3.4 follow-up sub-sections.
- `designs/workout-dumbbell-holder/output/workout-dumbbell-holder.stl` and `.f3d` — final v3.4 geometry.
- `designs/workout-dumbbell-holder/output/v2-archive/` — v2 STL/F3D/report preserved.
- `designs/workout-dumbbell-holder/output/modeling-report.md` — full v1 → v3.4 build journal at the top of the file.
- `designs/workout-dumbbell-holder/output/geometry-report.json` and `review-printability.md` — review pass outputs.
- `designs/workout-dumbbell-holder/test-prints/{plug-sleeve-stub,fork-plate-sample,buttress-arc-sample}/` — requirements.md + spec.json + STL + F3D each.
- `designs/workout-dumbbell-holder/test-prints/MODELING-NOTES.md` — atomic-build pattern documentation.
- `docs/workout-dumbbell-holder.md` — full design doc with hero render + per-test-print sub-sections.
- `docs/images/workout-dumbbell-holder/` — 4 hero PNGs (workout-dumbbell-holder-iso, plug-sleeve-stub-iso, fork-plate-sample-iso, buttress-arc-sample-iso). Re-rendered twice — once for catalog-style, once for the back-top-threequarter angle on the main.
- `README.md` — added Workout Dumbbell Holder row to the Designs table.
- `.claude/agents/modeler-fusion.md` — stripped the `tools:` allowlist (no functional change yet).
- `scad-lib/blender-presets/studio.py` — rewrote for catalog style: light cyc, warm beige PLA, soft 2-light setup, slight telephoto, limited-dissolve mesh cleanup. Added `back-top-threequarter` angle preset.

## Follow-ups

- [ ] Restart Claude Code and confirm the user has saved over the corrupted "2026-05-08 First viable plug v1" Fusion file with the v3.4 geometry.
- [ ] Print the **plug-sleeve-stub** test piece (HIGH priority gating). PASS = full v3.4 part is greenlit.
- [ ] After plug-sleeve-stub passes: print **fork-plate-sample** to validate bell-rest surface quality + slot dimensional accuracy.
- [ ] After test prints pass: print the full v3.4 part (plug-vertical orientation, supports for fork plate bottom + both buttress arc undersides + sleeve inner ceiling).
- [ ] Investigate the **subagent MCP propagation gap** so future Fusion designs can dispatch `modeler-fusion` directly instead of being driven from the main session. Likely needs an `mcpServers:` field in `.claude/agents/<name>.md` frontmatter — schema TBD.
- [ ] Investigate why fusion360-mcp-server v1.27.0 ships with a `{"command": ...}` payload format when the add-in expects `{"type": ..., "params": {...}}`. Either the server is outdated or the add-in is on a newer protocol.
- [ ] (Pre-existing) Print the ptouch-cradle test pieces (tray-slot-fit-pair + printer-corner-fit) before the full v11 cradle/tray run.
