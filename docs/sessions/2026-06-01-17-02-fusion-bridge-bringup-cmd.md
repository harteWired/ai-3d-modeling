---
date: 2026-06-01
project: 3d-printing
type: session-log
---

# 2026-06-01 — Fusion bridge bring-up .cmd + subnet-mask overflow fix

## Quick Reference
**Keywords:** battery-capsule-holder, Fusion 360 MCP, fusion bridge, port 9876, host.docker.internal, fusion-mcp-wrapper.sh, fusion-mcp-bridge.ps1, fusion-bridge-up.cmd, netsh portproxy, Windows Firewall, WSL2 172.29.176.0/20, Get-NetworkAddress op_BitwiseAnd overflow, PowerShell 5.1 uint32 shift, BitConverter uint64 mask, self-elevating cmd UAC, MCP loader no mid-session retry, modeler-fusion subagent-MCP gap, OpenSCAD vs Fusion compare, PR #1 merged, PR #2 pending, commit 52fb428

**Project:** 3d-printing

**Outcome:** Resumed the battery-capsule-holder Fusion-rebuild thread (OpenSCAD v1 already merged as PR #1; goal is a parallel Fusion build to compare before taking design feedback). Could not build this session — the `fusion` MCP tools never loaded (port 9876 was refused at start; Claude Code's MCP loader doesn't retry mid-session, so a relaunch is required after the bridge is live). Packaged the Windows-side bring-up into a one-click self-elevating `scripts/fusion-bridge-up.cmd`, and fixed a real bug in `fusion-mcp-bridge.ps1`: `Get-NetworkAddress` overflowed PS 5.1's uint32 shift (`op_BitwiseAnd` on Object[]), which dropped adapter discovery into the broad `172.16.0.0/12` firewall fallback. User ran the cmd; bridge applied and port 9876 confirmed LISTENING (green) despite the discovery error. Both scripts committed + pushed (52fb428).

## What Was Done
- Resumed via /resume; flagged that the prior 07:14 session was never compressed (breadcrumb newer than newest log). Most recent committed work was battery-capsule-holder OpenSCAD v1 (PR #1, merged to main).
- Read the battery-capsule-holder vault note + spec/scad to reconstruct state: OpenSCAD v1 PASSes (89×68×20 blob, 6 nested teardrop sockets, vol 46.4 cm³); user had asked for a parallel Fusion build to compare surface quality before giving feedback. Blocked last session on the Fusion MCP bridge.
- Diagnosed the full bridge chain: Fusion add-in (Windows :9876) ← PowerShell portproxy/firewall bridge ← host.docker.internal:9876 ← container relay in fusion-mcp-wrapper.sh ← uvx fusion360-mcp-server. Probed port 9876 → Connection refused; `ToolSearch +fusion` → no tools loaded this session.
- Created `scripts/fusion-bridge-up.cmd`: self-elevates via UAC, runs fusion-mcp-bridge.ps1 -Port 9876, then checks Get-NetTCPConnection -LocalPort 9876 and prints green OK / yellow "start the add-in", reminds to relaunch Claude Code.
- User ran it; hit a ps1 error in Get-NetworkAddress but bridge still applied via fallback and port came back LISTENING. Fixed the ps1 bug.
- Committed + pushed both scripts (52fb428).

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Don't pre-stage the full Fusion build script this session | User chose "just bring up the bridge"; a big speculative execute_code script can't be live-tested and Fusion has many gotchas (construction axes unsupported, coord conventions) that need a live session to iterate. |
| Package bring-up as a self-elevating .cmd | One double-click instead of remembering admin PowerShell + exact ps1 invocation; idempotent + persistent rules make re-runs safe. |
| .cmd does NOT start the Fusion add-in | The add-in lives inside Fusion's Add-Ins panel; a batch file can't launch it. The .cmd only forwards to it and reports listen status. |
| Fix the ps1 rather than leave the /12 fallback | The broad fallback widens the firewall scope beyond the actual WSL subnet; the fix restores the intended precise scoping. |

## Key Learnings
- A relaunch is mandatory to build: Claude Code's MCP loader registers server tools only at startup and does not retry mid-session, so even bringing the bridge up live can't load `fusion` tools into the running session.
- The Fusion add-in (not the bridge) is what makes :9876 listen — the portproxy/firewall bridge only forwards. A refused port usually means the add-in isn't running, not that the bridge is missing.
- The bridge ps1 is run-once/persistent (netsh portproxy + firewall rules survive reboots), so it likely doesn't need re-running each session — only the add-in + a Claude Code relaunch do.
- The bridge can "work" (port LISTENING, green) even while throwing the adapter-discovery error, because it falls back to 172.16.0.0/12 — the error is non-fatal but silently broadens firewall scope.

## Solutions & Fixes
- **Get-NetworkAddress overflow (fusion-mcp-bridge.ps1):** PS 5.1 overflowed `[uint32]::MaxValue -shl (32-$prefix)`, raising `op_BitwiseAnd` on System.Object[] and emptying adapter discovery. Rewrote to do mask math in guarded uint64 with BitConverter (reverse bytes → ToUInt32 → mask via `0xFFFFFFFFL -shl (32-prefix) -band 0xFFFFFFFFL` → cast back). Verified logic on 172.29.176.1/20 → 172.29.176.0/20.
- **Bridge bring-up friction:** new `scripts/fusion-bridge-up.cmd` self-elevates and reports listen status in one step.

## Files Modified
- `scripts/fusion-bridge-up.cmd`: NEW — self-elevating one-click Windows bring-up for the Fusion MCP bridge (apply rules + report port 9876 listen status + relaunch reminder).
- `scripts/fusion-mcp-bridge.ps1`: fixed Get-NetworkAddress uint32-shift overflow (now uint64 + BitConverter); restores precise WSL-subnet firewall scoping instead of the /12 fallback.

## Follow-ups
- [ ] Relaunch Claude Code with the Fusion bridge live (port 9876 listening) → /resume → drive the battery-capsule-holder Fusion build from the main session (modeler-fusion subagent-MCP gap still open).
- [ ] Build the Fusion version to match OpenSCAD v1 geometry (teardrop = hull of back-circle r=12.2 + tip r=0.6; cluster offset ∩ superellipse n=2.6 lofted base→top; 1.5 mm rim chamfers; 6 blind 18 mm sockets, nested 3×2 with 9.0 mm X-stagger; 89×68×20 target).
- [ ] Export STL + render → branch design/battery-capsule-holder-fusion / PR #2 → compare side-by-side with PR #1 before taking user design feedback.
- [ ] (optional) Re-run fusion-bridge-up.cmd to narrow firewall scope to the exact subnet now that the ps1 is fixed.
- [ ] Still open project-wide: subagent MCP propagation so modeler-fusion can be dispatched directly; strain-analyzer v2 FEA backend; print plug-sleeve-stub for dumbbell-holder v3.4.
