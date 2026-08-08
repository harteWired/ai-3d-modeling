# 2026-08-08 13:04 EDT — git hygiene and session-log backfill

**Trigger:** forge relayed findings from cu's fleet-wide git-backup inventory
(wintermute#129). This repo was the largest dirty tree on Grimnir — 84 dirty
paths, 79 untracked, ~30 MB. Nothing had been modified by forge or cu.

**Outcome:** 84 dirty paths → 1. Pushed to `main` and to
`shibumi-beach-caddy-architecture`.

## The actual problem

15 session logs (2026-04-26 → 07-12) existed only in this box's working tree —
not in git, not on GitHub, no second copy. Three months of build history one
disk failure from gone. Four earlier logs (04-18 → 05-03) were already tracked,
so the gap ran from there to the last log written.

Committing them is a better backup than any external bundle: cu's design can
only capture what's committed, and the loose-file path in that design is now
heavily restricted for unrelated security reasons.

## Commits

| Commit | Contents |
|---|---|
| `8d9f1c4` | `.gitignore` — render locks, `__pycache__`, secrets, regenerable derivatives |
| `da5e4cf` | 15 session logs + `.resume-log` |
| `333e73c` | Orphaned reference inputs, assembly outputs, `.mcp.json` |
| `e918b94` | shibumi-beach-caddy v3 WIP (feature branch only) |

The first three are repo-wide hygiene and were cherry-picked onto `main` via a
`git worktree` — the caddy work is unfinished and stays on its branch. Worktree
rather than `git checkout main`, so the dirty caddy tree wasn't dragged across.

## The .gitignore misses

`*.cli-project.json` was present, but the render CLI writes
`*.cli-project.json.lock`. That single missed suffix was **38 of 79** untracked
paths. Plus no `__pycache__/` rule (3 dirs). Fixing both dropped ~41 paths and
made the real dirty state readable for the first time in months.

Lesson: a `.gitignore` rule that *nearly* matches is worse than none — it reads
as handled, and the noise it lets through hides real uncommitted work. The 15
session logs were invisible in the status output for exactly this reason.

Also fixed: `designs/*/output/*.png` only matched direct children, so render
subdirs (`output/small/`, `output/_preview/`) leaked through.

## Regenerable vs not — the tiering question cu asked

Resolved by checking provenance rather than guessing:

- **`docs/images/drafts/` (27 MB, 24 of it `recook/`) — regenerable.** Superseded
  draft renders; the selected finals are committed under `docs/images/<design>/`,
  and the pipeline proof's regen command is recorded in the 05-22 session log.
- **`reference/crops{,2,3}/` (3.3 MB) — regenerable.** All 33 source photos are
  committed under `reference/photos/`, and the crop scripts are tracked.
- **glitter-wizard-hat reference photos — NOT regenerable.** Measurement source
  photos of the physical hat; nothing else captures those dimensions. Committed.
- **`assemblies/reference-stls/` — NOT regenerable.** External part geometry the
  fan-tub-adapter assembly checks fit against. Committed.

Both regenerable dirs are now gitignored, so they drop out of cu's inventory.

## shibumi-beach-caddy v3 — committed but NOT passing

Work from the 2026-07-28 session, uncommitted until now. Committed as the record,
not as a shippable state. File mtimes reconstruct what happened:

```
22:49  spec.json, strain-report.json
22:50  review-strain.md          → PASS, SF 208.3, PETG
23:04  review-printability.md    → written WITHOUT geometry data
23:06  scad + STL regenerated
23:07  geometry-report.json      → FAIL, 129 issues
```

The printability review says so itself: *"Geometry report: NO — does not exist
for this design yet"*, falls back to hand-traced CSG, and recommends running
`geometry-analyze` before print commitment. That run happened one minute later
and came back failing — 7 bridge fails, 38 thin walls, 84 overhang faces (10.4%
of surface). **So the printability review has never seen the geometry it
reviews.** Watertight, 152 × 183.1 × 110 mm, within build volume.

**Next action:** reconcile the 129 geometry issues, then re-run the printability
review against the current mesh. Do not print v3 on the strength of the existing
review.

Also noted: `spec.json` picked up churn from a machine rewrite (re-indented,
em-dashes escaped to `—`). No semantic change beyond the version bump.

## Left deliberately undone

**`CLAUDE.md` typechange — the 1 remaining dirty path.** It has been swapped from
a regular file to a symlink into `/opt/fleet/fleet-runtime-repo/agents/3d-printing/CLAUDE.md`,
matching the fleet governance-symlink pattern. Committing that to a GitHub repo
would hand clones a broken absolute-path symlink instead of the charter. Flagged
to Matt rather than decided unilaterally.

**cu confirmed and sharpened this (2026-08-08) — it is worse than described, and
fleet-wide:**

- The symlink target is **absolute**, so a clone on any other machine gets a
  dangling link.
- Git would not render it as a benign typechange. The diff shows
  `deleted file mode 100644` against a 70-line file, so the commit **reads as
  deleting the charter** — worse than a broken link, because it looks intentional
  in history.
- **All 22 agent `CLAUDE.md` files are symlinked this way.** Every agent with a
  GitHub-backed repo has the same latent commit waiting for whoever runs
  `git add -A` first.

Still Matt's call, and cu's view is the same for the other 21.

## Gaps found, reported to cu

- **No commit signing key and no git identity** in this repo. All history is
  unsigned; the identity (`aes87`) came from a global config that didn't survive
  the Grimnir migration. Set repo-locally to match history and committed unsigned.
  Only key present is `remote-ops_ed25519`, not provisioned for commit signing —
  did not repurpose it. The global convention says sign; that is broken here and
  likely fleet-wide.

  **Confirmed fleet-wide by cu** (0 GPG secret keys, no SSH pubkeys for uid
  `fleet`, all signing config unset), already with persona for Matt, raised in
  parallel by atelier and forge. The sharper version, worth knowing before anyone
  tries to fix it: **per-agent signing keys are not achievable on this host while
  every agent runs as uid 999** — any agent can read another's key off disk, so
  per-agent keys would be theatre. This is not a provisioning oversight to be
  fixed by generating keys; it blocks on agents no longer sharing a uid.

- ~~**`launch.sh` is local-only and untracked** across all 20 agent dirs
  (byte-identical, so low risk, but backed up nowhere).~~
  **WRONG — corrected by cu, see below. There is no backup gap.**
- **`env` confirmed never committed** on any branch (`git log --all -- env` empty),
  and now gitignored.

### Correction: launch.sh is tracked (cu, 2026-08-08)

The canonical copy is **`fleet-runtime-repo/fleet-runtime/launch.sh`**, tracked
and pushed. cu compared all 22 agent copies against it: **20 are byte-identical**,
so those are deployed copies of a file that already lives in a pushed repo. Only
**camera-crawler and network-manager** diverge, and both differ **only in header
comments** — no functional change.

My error was inferring "untracked here and identical everywhere" meant "tracked
nowhere." Byte-identical copies across 20 dirs was evidence *for* a canonical
source, not against one — I checked whether the file was tracked *in the agent
dirs* and never looked for it in `fleet-runtime/`.

**One real salvage, not mine to move:** network-manager's divergent header
comment records an operational fact the canonical file does not — that its
launch.sh is the Claude SDK side only, and the poller is a separate systemd unit.
If anyone regenerates the agent copies from canonical, that disappears. Worth
upstreaming into the canonical file or into network-manager's charter rather than
leaving it as an accidental comment.

## Other fixes

- Renamed `2026-06-21 full plate.3mf` → `2026-06-21-full-plate.3mf`. The space
  made git quote the path; the rest of `print2c/` was already hyphenated.
- Untracked `glitter-wizard-hat/output/project.json.lock`, committed by accident
  before the ignore rule existed.
