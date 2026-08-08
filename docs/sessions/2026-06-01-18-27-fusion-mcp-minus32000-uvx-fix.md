---
date: 2026-06-01
project: 3d-printing
type: session-log
---

# 2026-06-01 — Fusion MCP -32000 root-caused: missing uvx + unapproved project server

## Quick Reference
**Keywords:** fusion MCP, -32000, JSON-RPC server error, mcp__fusion__ tools not loading, enabledMcpjsonServers, project .mcp.json approval, ~/.claude/.claude.json, fusion-mcp-wrapper.sh, uvx missing, ~/.local/bin wiped by container rebuild, uv 0.11.18, astral.sh install.sh, fusion360-mcp-server, host.docker.internal:9876 OPEN, MCP loader startup-only no retry, battery-capsule-holder Fusion build, restart required

**Project:** 3d-printing

**Outcome:** Root-caused why the `fusion` MCP server never loads (was blamed on the Windows bridge across several prior sessions — the bridge was fine the whole time). Two stacked container-side causes, both fixed: (1) the project-scoped `fusion` server in `.mcp.json` was never approved — `enabledMcpjsonServers: []` in `~/.claude/.claude.json`, so Claude Code silently skipped it (never even showed as "connecting"); (2) underneath that, `uvx` — which `scripts/fusion-mcp-wrapper.sh` does `exec`-on — was missing because a May 21 container rebuild wiped `~/.local/bin`, so the exec failed and `/mcp` reported `Failed to reconnect to fusion: -32000`. Pre-approved fusion in config (with backup) and reinstalled uv 0.11.18 via the Astral installer to `~/.local/bin`. Verified `uvx fusion360-mcp-server --help` works and the package installs (30 pkgs). Port 9876 to Windows confirmed OPEN throughout. One restart needed for the MCP loader to pick it up (loader reads only at startup, never retries mid-session).

## What Was Done
- Started with `/resume` (3 sessions); flagged the live thread is the battery-capsule-holder parallel Fusion build, blocked on `fusion` MCP tools not loading despite a same-session restart.
- Confirmed `fusion` tools absent via `ToolSearch +fusion` (no match); at startup only `gemini` was listed as connecting — `fusion` wasn't even attempted.
- Verified the NON-causes: project `.mcp.json` defines fusion correctly; wrapper `scripts/fusion-mcp-wrapper.sh` exists + executable; `host.docker.internal:9876` probes OPEN from the container (bridge + add-in live).
- Found cause #1: `~/.claude/.claude.json` → `projects["/workspace/projects/3d-printing"].enabledMcpjsonServers = []`. Project-scoped MCP servers are untrusted until approved, so the loader skipped fusion silently. Backed up the config and added `"fusion"` to `enabledMcpjsonServers`.
- After user ran `/mcp`, it reported `Failed to reconnect to fusion: -32000` — approval cleared (server now attempted) but the connection failed. That exposed cause #2.
- Found cause #2: `${HOME}/.local/bin/uvx` does not exist (`~/.local/bin` held only `pymupdf`, dir mtime May 21 = container rebuild). The wrapper `exec`s uvx, so the MCP server never launched → `-32000`. `uv`/`uvx` gone from disk entirely.
- Reinstalled uv via `curl -LsSf https://astral.sh/uv/install.sh | sh` → uv 0.11.18 + uvx landed in `~/.local/bin` (exactly the wrapper's hardcoded path). System `pip install --user uv` was blocked by PEP 668 (externally-managed env).
- Verified the chain: `uvx fusion360-mcp-server --help` runs and prints usage; the package downloads + installs cleanly ("Installed 30 packages"). Manual JSON-RPC handshake tests through the wrapper were inconclusive (sandbox signal 144 + my own `pkill -f fusion-mcp-wrapper` self-matching the test command) — not worth more rabbit-holing; the real client (Claude Code on restart) is the proper verifier.
- Cleaned up stray relay on 127.0.0.1:9876 so the next launch rebinds cleanly.
- Saved a reference memory (reference_fusion_mcp_minus32000.md) with the diagnosis checklist.

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Pre-approve fusion in `~/.claude/.claude.json` (Option B) rather than have user approve via `/mcp` | Faster + deterministic; backed up the config first. Either way needs a restart since the MCP loader is startup-only. |
| Reinstall uv via Astral installer, not pip | System pip blocked by PEP 668; the Astral installer drops uv+uvx into `~/.local/bin` — exactly the path the wrapper `exec`s, matching how it was originally installed. |
| Stop manual JSON-RPC handshake testing after the entrypoint resolved | Signal-144 + self-pkill noise made hand-rolled MCP tests unreliable; `uvx ...--help` + clean package install + OPEN bridge is sufficient proof. Real verification = Claude Code handshake on restart. |
| Save a reference memory | This recurs on every container rebuild (wipes `~/.local/bin/uvx`); a checklist prevents re-blaming the Windows bridge next time. |

## Key Learnings
- The `fusion` MCP failure was container-side, NOT the Windows bridge — the bridge tested OPEN the entire time. Prior sessions chased the bridge unnecessarily. Check container side first.
- Project-scoped `.mcp.json` servers are untrusted until added to `enabledMcpjsonServers` in `~/.claude/.claude.json`. Unapproved → silently skipped, not even shown as "connecting". The real config lives at `/home/node/.claude/.claude.json` (not `~/.claude.json`).
- A container rebuild wipes `~/.local/bin`, removing `uvx`. Since `fusion-mcp-wrapper.sh` does `exec ${HOME}/.local/bin/uvx ...`, a missing uvx surfaces as MCP `-32000` (JSON-RPC server error), not an obvious "command not found".
- The MCP loader only reads server config at startup and never retries mid-session — every fix (approval or uvx) requires a Claude Code restart.
- `-32000` specifically means the server process failed to come up / handshake, distinct from a refused TCP port (which would be a bridge/add-in problem).

## Solutions & Fixes
- **Approval gate:** add `"fusion"` to `projects["/workspace/projects/3d-printing"].enabledMcpjsonServers` in `/home/node/.claude/.claude.json` (backup saved at `~/.claude/backups/.claude.json.pre-fusion-enable.bak`).
- **Missing uvx:** `curl -LsSf https://astral.sh/uv/install.sh | sh` → uv 0.11.18 + uvx to `~/.local/bin`. Verify with `uvx fusion360-mcp-server --help`.
- **Diagnosis order for future:** (1) probe `host.docker.internal:9876` OPEN, (2) check `enabledMcpjsonServers`, (3) check `~/.local/bin/uvx` exists, (4) restart.

## Files Modified
- `/home/node/.claude/.claude.json` — added `"fusion"` to the 3d-printing project's `enabledMcpjsonServers` (backup at `~/.claude/backups/.claude.json.pre-fusion-enable.bak`).
- `~/.local/bin/uv`, `~/.local/bin/uvx` — reinstalled (uv 0.11.18) via Astral installer.
- `/home/node/.claude/projects/-workspace-projects-3d-printing/memory/reference_fusion_mcp_minus32000.md` — new reference memory (won't-load checklist) + MEMORY.md index line.
- `docs/sessions/.resume-log` — breadcrumb appended by /resume.

## Follow-ups
- [ ] **Restart Claude Code**, then `/resume` → confirm `ToolSearch +fusion` returns tools and a first `get_scene_info` returns a real Fusion document (proves the add-in is live, not just the port forwarded).
- [ ] Drive the battery-capsule-holder Fusion build to match OpenSCAD v1 (teardrop = hull back-circle r=12.2 + tip r=0.6; cluster offset ∩ superellipse n=2.6 lofted base→top; 1.5 mm rim chamfers; 6 blind 18 mm sockets nested 3×2 with 9.0 mm X-stagger; bbox 89×68×20, vol 46.4 cm³) → STL + render → branch + PR #2 → compare vs PR #1 before taking design feedback.
- [ ] (optional) Add uv/uvx reinstall to `setup.sh` so a container rebuild doesn't silently break the Fusion MCP again.
- [ ] Pre-existing: subagent MCP propagation gap (modeler-fusion can't see `mcp__fusion__*`); strain-analyzer v2 FEA backend; print plug-sleeve-stub for dumbbell-holder v3.4.
