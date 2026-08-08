---
date: 2026-07-12
project: 3d-printing
type: session-log
---

# 2026-07-12 — Post-crash recovery, session-log backfill, and container-rebuild prep

## Quick Reference
**Keywords:** post-crash recovery, Jinn container crash, resume, session-log backfill, vault next-action fix, belfry send_to, agent-to-agent coordination, Wintermute, fleet model audit, Opus 4.8, status roll-up, container-rebuild prep, bind mount 9p C:\, uv/uvx reinstall, fusion MCP enablement, .venv persistence, shibumi-mount-adapter Phase 1, fit-test parked
**Project:** 3d-printing
**Outcome:** Recovery + coordination session (no new design geometry). Rebuilt state after a Jinn container crash, confirmed nothing was lost, backfilled the missing shibumi Phase 1 session log, corrected a stale vault next-action, and answered a series of fleet-coordination pings via belfry (model audit, status roll-up, container-rebuild prep inventory). Shibumi Phase 1 stays parked on Matt's physical fit-test print.

## What Was Done
- Ran /resume; breadcrumb check caught that the entire shibumi-mount-adapter arc (7 commits, PR #8) and the mailbox-grate completion had no session log — flagged as uncompressed work.
- Post-crash state verification (Jinn hung + crashed ~15:00 UTC 2026-07-11, mid `compress fast`): confirmed HEAD (f94245c) == origin/main, working tree clean, all shibumi Phase 1 work committed AND pushed. Nothing lost — the crash hit after the last commit.
- Backfilled the shibumi Phase 1 session log (docs/sessions/2026-07-11-08-20-shibumi-mount-adapter-phase1-capture-socket.md), reconstructed from git since the live transcript didn't survive.
- Corrected the stale vault next-action (was "Mailbox grate DONE, awaiting next design" — predated the whole shibumi arc) to "BLOCKED ON MATT'S FIT-TEST PRINT — Shibumi Phase 1"; added a 2026-07-11 vault log entry. (These vault edits were already swept into a protective checkpoint commit eea5e0e; vault repo is local-only, no remote.)
- Fleet coordination via belfry send_to (all peer origin=agent messages, never reply): confirmed model = Opus 4.8 (Fable→Opus fleet-wide credit conservation, no-op for this session); delivered a 3D-Printing status roll-up (#139); delivered a container-rebuild-prep persistence status + resource inventory (#150).

## Decisions & Trade-offs
| Decision | Rationale |
|----------|-----------|
| Backfill the shibumi log as a git reconstruction, flagged as such | Live transcript lost in the crash; git history is the ground truth; honesty about provenance |
| Do NOT commit session logs to git | Long-standing local-only pattern (logs untracked for months); they survive on the /workspace bind mount |
| Leave next-action design-focused (blocked on fit-test) | The one real open item is Matt's physical print; rebuild-prep is transient infra, not project state |

## Solutions & Fixes
- Post-crash "am I short of where I left off?": verified via git (HEAD==origin/main, clean tree) that no uncommitted work existed — the crash was harmless to persisted state.
- Stale vault next-action → rewritten to reflect the shibumi Phase 1 fit-test blocker.

## Key Learnings
- /workspace is a 9p bind mount to Windows C:\ → committed AND untracked workspace files survive a container rebuild. Real rebuild risk is state OUTSIDE /workspace.
- Recurring rebuild casualties (outside /workspace, must reinstall): uv/uvx at ~/.local/bin (currently MISSING; needed by the fusion MCP wrapper; reinstall via astral.sh/uv/install.sh) and ~/.claude/.claude.json enabledMcpjsonServers (currently [], re-add "fusion" if wanted). Matches memory reference_fusion_mcp_minus32000.
- The .venv (Python 3.11.2: trimesh 4.11.3, shapely 2.1.2, manifold3d 3.4.0, pillow 12.1.1, numpy, scipy, networkx) lives under /workspace so files persist, but is pinned to /usr/bin/python3 3.11.2 — recreate if the new base image bumps python minor.
- Core render pipeline that must stay baked in the image: openscad, xvfb/xvfb-run, node/npm, python3. Not installed (bake only if wanted): Blender, PrusaSlicer, cwebp (PIL is the webp fallback).

## Files Modified
- `docs/sessions/2026-07-11-08-20-shibumi-mount-adapter-phase1-capture-socket.md`: NEW backfilled Phase 1 session log (git reconstruction).
- `/workspace/projects/obsidian-vault/vault/projects/3d-printing.md`: corrected next-action + added 2026-07-11 log entry (committed in vault as eea5e0e).
- `docs/sessions/.resume-log`: resume + compress ledger markers.

## Follow-ups
- [ ] BLOCKED ON MATT (physical): print shibumi fit-test variants A (gap4.0/=1), B (gap4.2/=2), C (gap4.35/=3); report which gap grips the real beach-chair cleat. Only input Phase 1 waits on.
- [ ] If all three read tight: caliper the cleat-tab THICKNESS (only dim never measured).
- [ ] Post-fit: internal-taper grip tuning + parametric Fusion rebuild → Phase 2 holders (bottle/table/phone).
- [ ] Post-rebuild (if/when Jinn is rebuilt): reinstall uv/uvx; re-enable fusion in ~/.claude/.claude.json; verify .venv against the new base python; restart belfry daemons + jinn reverse-ssh tunnel.
