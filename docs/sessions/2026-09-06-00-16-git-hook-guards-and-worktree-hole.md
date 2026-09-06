---
date: 2026-09-06
project: 3d-printing
type: session-log
---

# 2026-09-06 — Git hook guards: chained install, the worktree hole, and hooksPath

## Quick Reference
**Keywords:** git hooks, pre-commit, core.hooksPath, hooksPath unset, .git-hooks, linked worktree, credential guard, charter guard, dispatcher, chained hooks, prove-RED, guard currency, stale guard, decoy hooks directory, public repo hygiene
**Project:** 3d-printing
**Outcome:** Infrastructure session, no design geometry. This repo moved from a relative `core.hooksPath=.git-hooks` (which left linked worktrees silently unguarded) to `hooksPath` **unset** with three chained guards in `.git/hooks`, verified behaviourally in five directions. One commit here (`46d0f11`, a `.gitignore` line). `shibumi-beach-caddy-architecture` / `v3-rugged-cantilever` untouched and still not passing review.

## What Was Done

A fleet-wide effort to add credential scanning to every agent repo's pre-commit
hook ran overnight; this repo was one of the participants. Nearly all of the work
was verification rather than authorship.

### The hook configuration changed here

**Before:** `core.hooksPath=.git-hooks`, one hook file (an older revision of the
charter guard), no credential scanning.

**After:** `core.hooksPath` **unset**; `.git/hooks/` holds a dispatcher plus two
guards (charter, credentials); `.git-hooks/` deleted.

Why unset, since it looks like "unconfigured":

- A **relative** `hooksPath` resolves against *each working tree's own root*, and
  `.git-hooks/` was gitignored — so `git worktree add` produced a tree with **no
  hooks at all**. Proved here: a file carrying a planted credential committed from
  a linked worktree at `rc=0` with zero guard output.
- **Unset** resolves through `git-common-dir`, which every linked worktree shares,
  so all worktrees are covered. Re-proved after the change: same commit blocked.
- Unset is only safe **after relocating the guards into `.git/hooks`**. Unsetting
  first would fall back to whatever already occupies that directory.
- `.git-hooks/` was **deleted, not left in place** — with `hooksPath` unset it
  would be inert, an obviously-present guard directory that git never reads.

Sequence used, and worth reusing: **relocate → verify by content → unset → prove →
delete the old directory → re-prove.**

### Verification

Every direction was proved by running it, never by reading configuration or
comparing hashes. Index reset between directions so a blocked commit could not
poison the next control.

| direction | result |
|---|---|
| clean commit | `rc=0`, `all 2 guard(s) passed` |
| planted credential | `rc=1`, blocked, zero value occurrences in output |
| symlinked `CLAUDE.md` | `rc=1`, refused, `HEAD` unchanged |
| symlink→file typechange carrying a credential | `rc=1`, blocked |
| commit from a linked worktree | `rc=1`, blocked, main `HEAD` unchanged |

Planted values were synthetic. Assert the guard's own `BLOCKED`/`REFUSING` line,
**not** the exit code — a non-zero exit can come from a missing directory or a
failed `cd` rather than from a guard firing.

### Things that cost time and are worth not rediscovering

- **A stale guard reads green.** The credential guard installed here was briefly
  an older revision missing a fix for a real bypass. It passed the clean-commit
  and planted-credential controls perfectly, because those test the paths that
  already worked. Guards are hand-copied and never self-update.
- **Re-running an installer is not free.** One revision of the fleet installer
  misclassified its own dispatcher and chained a copy of it as a member, producing
  unbounded recursion on every commit. Caught here before any commit was made.
- **A deleted working directory forges a green.** Running commands from a worktree
  that had just been removed returned `rc=128` for everything; the guard checks
  read as blocks *and* `git status --porcelain` failed, whose empty output is
  exactly what "clean" looks like. Four test results were fabricated until re-run
  from an absolute path. `cd` out before removing a worktree.

### Repo hygiene

- `46d0f11` — `.gitignore` entry for the hook installer's pre-state record. The
  comment was reworded before pushing so no internal tooling path is published;
  **this repo is public**, so anything committed here is world-readable.
- The pre-state record itself was moved out of the working tree entirely.
- `CLAUDE.md` here is a gitignored symlink. Testing the charter guard stages it
  with `git add -f`, and a later `git reset --hard` would **delete** it —
  untracked, ignored, silently. Unwind with `reset --soft` then `reset`, never
  `--hard`. Losing it costs the agent its instructions on the next session, not
  any file content.

### Not in this repo

Rationale that cannot live here — the repo is public and `.git/config` is
untracked — is recorded in agent memory (`git-hooks-unset-hookspath`,
`hook-guard-currency-is-not-presence`). Fleet-wide conventions were updated
centrally.

## State At End

- Guards current, five directions proven, tree clean, one worktree (main).
- `CLAUDE.md` symlink intact.
- Design work untouched: `shibumi-beach-caddy-architecture`, `v3-rugged-cantilever`
  still **not passing** review — unchanged from the start of this session.

## Next Action

Return to `v3-rugged-cantilever`: the geometry did not pass review and no
diagnosis has been done on why. Nothing in this session bears on it.
