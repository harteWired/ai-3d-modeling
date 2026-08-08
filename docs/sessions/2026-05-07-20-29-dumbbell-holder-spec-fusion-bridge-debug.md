---
date: 2026-05-07
project: 3d-printing
type: session-log
---

# 2026-05-07 — Dumbbell holder spec + Fusion bridge debug

## Quick Reference
**Keywords:** workout-dumbbell-holder, treadmill extrusion, internal plug, deep engagement, dowsing-rod cradle, R23 saddle, 60° spread, CF-reinforced, modelingBackend fusion, modeler-fusion, fusion MCP bridge, host.docker.internal:9876, VS Code port squat, Errno 104 connection reset by peer, fusion360-mcp-server, fusion-mcp-wrapper.sh, fusion-mcp-bridge.ps1, MCP session-load ordering, JSON-RPC probe, get_scene_info, spec-writer, vault note per design

**Project:** 3d-printing

**Outcome:** New design `workout-dumbbell-holder` intaken end-to-end through spec-writer (requirements.md + spec.json + vault note) — first design slated for the Fusion MCP backend (`modelingBackend: "fusion"`). All 7 spec-writer open questions resolved with the user. Fusion MCP bridge debugged from scratch: container TCP path verified, then a phantom listener on Windows :9876 diagnosed via `Connection reset by peer` (Errno 104), traced to a non-VS-Code-Ports-tab process squatting the port; user freed it and end-to-end probe got a real `get_scene_info` response from the live empty Fusion document. Modeler dispatch deferred — fusion MCP tools didn't load into the current Claude Code session because the bridge wasn't up at session start.

## What Was Done

1. **Spec intake for workout-dumbbell-holder** via spec-writer agent (called twice — once for initial intake, once to lock open questions):
   - Read user's idea note at `vault/projects/3d-printing/2026-05-07-workout-dumbbell-holder.md` + reference photo `attachments/2026-05-07-workout-dumbbell-holder-reference.jpg` (orange ~1–3 lb rubber-coated dumbbell on a silvery rectangular treadmill rail).
   - Locked geometry: internal-plug clip-on cradle, plug 42.5×68.5×30 mm into extrusion ID 44.5×70.5 mm, flange 8 mm thick × 10 mm radial overhang, cradle reach 70 mm, R23 mm circular saddle tangent into 60°-included flared arms.
   - `modelingBackend: "fusion"` — first real design routed to the Fusion backend.
   - `requiresId: false` — utility part, no aesthetic motif.
   - Bounding box: 88.5 × 108 × 62.5 mm (well inside X1C).

2. **Fusion MCP bridge debugging — from probe to working end-to-end**:
   - Confirmed container can reach `host.docker.internal:9876` (TCP connect succeeds).
   - Initial JSON-RPC probe via `fusion-mcp-wrapper.sh` returned `Errno 104 Connection reset by peer` — diagnosed as phantom listener (Windows side accepting TCP then immediately resetting). User reported "VS Code is occupying that port" but the port wasn't in VS Code's Ports tab — meaning it was a different process (likely a stale Code-related backend or extension host).
   - Provided user with PowerShell `Get-NetTCPConnection -LocalPort 9876` recipe to identify the actual owning process.
   - User freed the port. Re-probed via wrapper: got back real `get_scene_info` response showing `design_name: Untitled, bodies: 0, sketches: 0, camera eye [25.6,-25.6,25.6]` — bridge is fully functional.

3. **Discovered MCP-tool-loading gap**: even though the bridge is live now, the parent Claude Code session never loaded `mcp__fusion__*` tools (because the bridge wasn't up at session start, and Claude Code's MCP loader doesn't retry). Modeler-fusion dispatch deferred until the user restarts Claude Code so MCP tools load fresh.

## Decisions & Trade-offs

| Decision | Rationale |
|---|---|
| `modelingBackend: "fusion"` for this design | Whole point of the run is to field-test the Fusion MCP backend on a real design. CF-reinforced FDM utility part is a reasonable first test. |
| Plug engagement depth = 30 mm (not 80 mm spec-writer suggested) | User: "80 is hella deep." 30 mm in a 44.5×70.5 mm bore is plenty for a 1–3 lb dumbbell at 70 mm cantilever (moment ≈ 0.91 N·m). |
| Saddle = R23 mm circular arc tangent to 60° flared arms (not a sharp V) | User: "I don't want a straight V, make sure there's a smooth continuous curve in it." Saddle radius matches shaft radius (D 46 mm) so the shaft seats fully. |
| Beefier flange: 8 mm thick × 10 mm overhang (not 5/5) | User: "you can beef up the flange." Better seat against the rim, more material to resist cantilever moment. |
| Gravity retention only (no setscrew, no friction pad) | User: "Just use gravity and deep engagement." Simpler print, easier to lift dumbbell out mid-workout. |
| Defer modeler-fusion dispatch | Fusion MCP tools didn't load into this Claude Code session (bridge wasn't up at start). Restarting the session is cleaner than driving Fusion via Bash + JSON-RPC from inside the agent. |

## Solutions & Fixes

- **Phantom Windows listener on :9876 (`Errno 104 Connection reset by peer`)** — symptom: TCP connect from container succeeds, but JSON-RPC handshake gets immediately reset. Root cause: a non-Fusion process (in this case reported by the user as "VS Code occupying the port" but invisible in VS Code Ports tab) had bound :9876 on Windows, blocking Fusion's add-in from binding. Diagnostic: `Get-NetTCPConnection -LocalPort 9876` in PowerShell shows actual owning PID + ProcessName + ProcessPath. Fix: kill the squatter, then start Fusion add-in.
- **End-to-end Fusion bridge probe recipe** (saved for re-use):
  ```bash
  timeout 12 bash -c '
  printf "%s\n" \
    "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"probe\",\"version\":\"1\"}}}" \
    "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}" \
    "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"get_scene_info\",\"arguments\":{}}}" \
  | /workspace/projects/3d-printing/scripts/fusion-mcp-wrapper.sh 2>&1'
  ```
  PASS = the second JSON response contains `"isError":false` with scene info. Errno 104 in the trace = phantom Windows listener. `Not connected to Fusion 360` = MCP server reachable but no live Fusion app.

## Key Learnings

- **MCP session-load ordering matters**: Claude Code loads MCP servers at session start. If the underlying connection fails (e.g. bridge not up), the loader silently skips and does not retry mid-session. Practical implication: bring the Fusion bridge up *before* starting a Claude Code session that needs `modeler-fusion`. Restart the session if bridge state changed.
- **TCP-connect-success ≠ end-to-end-success on the Fusion bridge**. Need a JSON-RPC probe (or at least a `get_scene_info` call) to know if the actual Fusion add-in is live. Phantom listeners squat the port and reset connections after the TCP handshake.
- **VS Code Ports tab isn't authoritative** for "what's bound on this Windows port?" — it only shows the WSL extension's auto-forwards. Other Windows-side processes (extension hosts, code-server backends, orphaned uvx) won't appear there but will still hold the port. Use `Get-NetTCPConnection` for truth.
- **The `modeler-fusion` agent definition's `tools:` list (`Read, Write, Edit, Bash, Glob, Grep`) does not include `mcp__fusion__*`** — it relies on inheriting from the parent session. If the parent session didn't load the fusion MCP, the agent has no path to drive Fusion except via Bash piping JSON-RPC into the wrapper. Worth flagging if a future session hits the same issue.

## Files Modified

- `designs/workout-dumbbell-holder/requirements.md` — created
- `designs/workout-dumbbell-holder/spec.json` — created (`modelingBackend: "fusion"`, all 7 open questions resolved)
- `vault/projects/3d-printing/workout-dumbbell-holder.md` — created (per project convention: vault note per design at spec time)

## Follow-ups

- [ ] User restarts Claude Code so the fusion MCP server loads as proper `mcp__fusion__*` tools
- [ ] Dispatch `modeler-fusion` agent on `designs/workout-dumbbell-holder/` — first real field test of the Fusion backend
- [ ] After modeling: run geometry-analyzer + print-reviewer (still flag CF inter-layer adhesion vs. cantilever bending axis, plug-root structural cross-section under 30 mm engagement)
- [ ] Decide on print orientation for CF — bending-axis-perpendicular layer lines are the weakest case
- [ ] (still open from prior session) Print ptouch-cradle test pieces (tray-slot-fit-pair + printer-corner-fit) before the full v11 run
