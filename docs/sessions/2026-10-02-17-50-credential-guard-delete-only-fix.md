# 2026-10-02 17:50 ET — credential guard: sync the delete-only fix

Flagged by **wintermute-persona** over belfry: this repo's active
`.git/hooks/pre-commit-credentials` was the pre-2026-09-07 revision and
false-blocks **deletion-only** commits. Verified, fixed, and proven here.
Originally found by **web-design-pipeline**, who hit it on a real takedown.

## What was wrong

A commit whose staged set is *entirely deletions* tripped the guard's vacuity
check — the filtered (scannable) set is legitimately empty, which the old code
read as "a status class is being skipped" and refused to pass. A deletion cannot
add a credential, so this was a false positive on every page takedown, revert or
cleanup.

Reproduced in this repo against the stale guard (`git rm --cached package.json`,
hook run directly, index restored):

```
D	package.json
pre-commit: BLOCKED: scope mismatch: filtered set is EMPTY but git reports 1 staged path(s).
pre-commit: guard 'pre-commit-credentials' FAILED (exit 1)
rc=1
```

**Correction to the report, in this repo's favour:** persona's heads-up said the
failure is swallowed by `|| true` and so may go unnoticed. Not here — the
dispatcher `.git/hooks/pre-commit` contains **no `|| true`** (grepped), and the
block printed loudly at `rc=1`. The silent-removal symptom described does not
apply to this install.

## Currency check — only one of three guards was stale

```
pre-commit             CURRENT
pre-commit-charter     CURRENT
pre-commit-credentials STALE  mine=b1aaf0efb533  canonical=24e03b743972
```

Canonical source verified to be the **committed** version, not someone's
uncommitted edit in the shared tree: `git status --porcelain` clean on that
path, `git show HEAD:…| sha256sum` = `24e03b743972`, last touched by
`349ddc4 2026-09-07 Matt  guard: a delete-only commit is legitimately vacuous,
not a scope mismatch (#305)`.

## What changed

- Old guard backed up to `.git/hooks/.pre-commit-credentials.b1aaf0ef.bak`
  (untracked, not a hook name git will run) — the evidence survives the update.
- Copied `fleet-runtime-repo/tools/agent-charters/git-hooks/pre-commit-credentials.sh`
  → `.git/hooks/pre-commit-credentials`, `chmod 700` to match its siblings.
- Installed sha `24e03b743972`, byte-identical to canonical.

`core.hooksPath` remains **UNSET** and no `.git-hooks/` directory was created —
see `docs/sessions/2026-09-06-00-16-git-hook-guards-and-worktree-hole.md` for why
that shape is deliberate.

## Proven behaviourally, five directions

A matching hash says the bytes arrived, not that the guard fires. Each case was
staged in this repo (or, for the typechange, a throwaway repo with this exact
guard installed), the hook chain invoked directly, and the index restored.

| # | case | before (b1aaf0ef) | after (24e03b74) |
|---|---|---|---|
| 1 | deletion-only | ⛔ false-block rc=1 | ✅ rc=0, `COMPLETE scanned=0 findings=0 (delete-only commit)` |
| 2 | planted credential | ✅ BLOCKED rc=1 | ✅ BLOCKED rc=1 |
| 3 | clean add | — | ✅ rc=0, `COMPLETE files=1 added_lines=2 findings=0` |
| 4 | **delete + credential-add mixed** | — | ✅ BLOCKED rc=1 |
| 5 | symlink→file typechange w/ credential | ✅ BLOCKED rc=1 | ✅ BLOCKED rc=1 |

**Case 4 is the one worth having run.** The fix exempts an all-deletions staged
set from scanning; the risk it introduces is a deletion *paired* with a
credential-bearing add being waved through on the same exemption. It is not —
the mixed set still blocks.

**Case 5 shows the delta is narrow.** The `T`-status bypass fixed here on
2026-09-06 is present in *both* revisions, so the only behavioural difference
between `b1aaf0ef` and `24e03b74` is the delete-only case. No regression.

All planted values were synthetic strings matching the detector's pattern, never
live credentials, and nothing was committed; `git status --porcelain` is clean and
`package.json` hashes unchanged after every test.

## Durable note

Guards here are still **hand-copied** and still do not self-update — nothing
propagates a `fleet-runtime-repo` fix into this repo, and nothing triggers
`audit-hooks.sh`. This update exists because a peer happened to look. The
currency check is in the agent memory note `hook-guard-currency-is-not-presence`,
whose recorded sha has been bumped to `24e03b743972`.
