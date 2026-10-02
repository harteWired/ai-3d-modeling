# 2026-10-02 19:31 ET — credential guard: sync the access-key fix (59d2c77604b0)

Second guard sync today. Flagged by **wintermute-persona**: upstream `main` carries
a fix (#374, commit `5d3264a`) catching `AWS_SECRET_ACCESS_KEY` and every
`*_ACCESS_KEY=` — the authenticating half the guard previously missed. Verified,
fixed, proven. Guard now `59d2c77604b0`.

## ⚠ The sha I recorded as "final" this afternoon was stale within hours

The 17:50 session log and the agent memory note both named `24e03b743972` as
current — and persona had confirmed it "current and final" on the bus. Both were
correct when written. **Neither was wrong; both expired.** This is the
written-fact-expires-silently shape happening to the very note written to prevent
it, inside one working day. The lesson is not "the note was bad" — it is that a
recorded sha is a measurement with a timestamp, never a standing fact, and the
only thing that settles currency is re-running the comparison.

## ⛔ Did NOT use `--retrofit` — it would have downgraded this repo

persona's recommended deploy step was
`tools/agent-charters/agent-git-init.sh --retrofit`, and forge offered to run it.
**Reading it first was load-bearing.** Lines 347–349:

```sh
install -m 700 "$here/${_e%%|*}" "$dir/.git-hooks/${_e##*|}"
git -C "$dir" config core.hooksPath .git-hooks
```

On this repo that would:

1. create `.git-hooks/` — deliberately deleted here on 2026-09-06;
2. set a **relative** `core.hooksPath`, which resolves against *each working
   tree's own root*. `.git-hooks/` is gitignored, so `git worktree add` produces a
   tree with **no hooks at all**. Proved live in this repo: a credential-bearing
   file committed from a linked worktree at `rc=0` with zero guard output;
3. leave the three guards in `.git/hooks/` **present but inert** — the decoy shape
   that made three other repos misread as protected. A future reader hashing
   `.git/hooks/pre-commit-credentials` would be reading a file git no longer runs.

It also installs the guard as `pre-commit-credentials.sh` (with extension), where
this repo has `pre-commit-credentials` — so it would not even overwrite the stale
file, it would add a second copy beside it.

**So the fix is a one-file hand-copy, as before.** `core.hooksPath` confirmed
still unset and `.git-hooks/` confirmed still absent after the update.

This is not a defect in the installer — it is correct for the population it was
written for (repos using the `.git-hooks` + relative-path shape). It is wrong
*here*, and nothing in the installer could know that. Which is the argument for
reading a deploy step against your own repo's shape before running it, and for
not delegating it to an agent who cannot see that shape.

## Prove-RED first: the hole was real, and it failed reassuringly

Throwaway repo, same two payloads, old guard vs new:

```
OLD 24e03b743972 -> pre-commit: COMPLETE files=1 added_lines=4 findings=0   rc=0  PASSED
NEW 59d2c77604b0 -> BLOCKED: payload:1 + payload:2 generic_secret_assignment  rc=1  BLOCKED
```

`findings=0` at `rc=0` — the guard's own all-clear, on a staged AWS secret. Both
lines are caught by the `generic_secret_assignment` rule, not a dedicated AWS one.

## Five directions proven in this repo

| # | case | result |
|---|---|---|
| 1 | `AWS_SECRET_ACCESS_KEY=` + `*_ACCESS_KEY=` | ✅ BLOCKED rc=1 (the new fix) |
| 2 | anthropic key | ✅ BLOCKED rc=1 (pre-existing coverage intact) |
| 3 | **delete-only** | ✅ rc=0 `COMPLETE scanned=0 findings=0 (delete-only commit)` |
| 4 | **mixed delete + credential-add** | ✅ BLOCKED rc=1 |
| 5 | clean add, `ACCESS_KEY` as prose w/o assignment | ✅ rc=0, no false positive |

**3 is the regression check** — the delete-only fix synced at 17:50 had to survive
being overwritten by a newer revision, and did. **4 is still the load-bearing
case** for the same reason as before: the delete-only exemption must not become a
bypass, now re-proven against an access-key payload rather than an anthropic one.
**5 guards the other direction** — a rule matching `access[_-]?key` could plausibly
fire on prose; it does not, because it requires an assignment.

All values synthetic, matching the detector's pattern, never live credentials.
Nothing committed; tree clean and `package.json` unchanged after every case.

## State

- Guard `59d2c77604b0`, byte-identical to canonical, mode 700.
- Dispatcher `7ad2f357cae6` and charter guard `6986cbeeb94d` both **CURRENT** — the
  credential guard was the only stale artifact. The installer-side "depth +
  seed-verify" fixes persona mentioned live in `agent-git-init.sh`, which this repo
  does not use as an install path, so they do not apply here.
- Previous revisions retained: `.pre-commit-credentials.24e03b74.bak` and
  `.pre-commit-credentials.b1aaf0ef.bak`.
- `core.hooksPath` **unset**; no `.git-hooks/`.

Two syncs in one day, both found by a peer, neither by anything here. The
propagation gap is the actual defect; `fleet-timer@` + `audit-hooks.sh` is with
computer-use, with the caveat that `fleet-timer@.service` has `OnFailure=` empty.
