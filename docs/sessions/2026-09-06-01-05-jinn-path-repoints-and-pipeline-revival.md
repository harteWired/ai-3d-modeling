---
date: 2026-09-06
project: 3d-printing
type: session-log
---

# 2026-09-06 — Jinn-era path repoints: the validate pipeline runs again

## Quick Reference
**Keywords:** dead paths, container-era paths, cli-anything-openscad, PATH resolution, validate.js, npm ci, uv venv, trimesh, blender absent, dated dead-notes, npm test node 24, STL non-reproducible, premise check, negative control
**Project:** 3d-printing
**Outcome:** `node bin/validate.js <design>` returns **PASSED / rc=0** for the first time on this host. Dependencies installed, one hardcoded container path repointed, six other dead-path sites triaged per-file. Two findings recorded below rather than fixed silently. No design geometry changed.

## What Was Done

The charter carried a gap note claiming the project code had never been copied to
this host. **It was false** — measured with a negative control, everything was
present. What was actually broken was different and underneath it.

### The real fault chain, in the order it surfaced

1. **Dependencies were never installed.** `node_modules/` and `.venv/` absent, so
   `validate.js` died on `MODULE_NOT_FOUND` for `node-stl`.
   Fixed: `npm ci` (lockfile-exact — the lock pinned one integrity-hashed package
   with zero transitive deps) and `uv venv` + `uv pip install -r requirements.txt`.
2. **With deps installed, a deeper fault appeared.** `lib/openscad.js` hardcoded a
   container path for `cli-anything-openscad`, so every render died `ENOENT` while
   the tool sat installed on `PATH`.

**The fix was deliberately not "point it at the new absolute path"** — that is the
same bug with a newer address, and breaks identically on the next move. It now
resolves through `PATH` with a `CLI_ANYTHING_OPENSCAD` override, so the shell's own
lookup does the work and a failure names the binary it could not find.

### Result

```
node bin/validate.js designs/battery-capsule-holder   ->   Validation PASSED  rc=0
```

Cross-validated three independent ways, which is why it is trustworthy rather than
merely green: `volume 46.401 cm³` from validate.js, **46,401 mm³** from trimesh
loading the STL, and **6,940 facets** from both the raw OpenSCAD render and the
trimesh face count.

### The cluster was not uniform — one sweep would have made two wrong edits

Seven sites matched the same dead-path pattern. They needed four different actions:

| site | action | why |
|---|---|---|
| `lib/openscad.js` | repoint + prove | the only real blocker |
| `designs/shibumi-mount-adapter/reference/draw_socket.py` | repoint + prove | output path was dead, so it could write nowhere |
| `bin/render-hero.js` | dated note only | **not broken** — its `existsSync` check already falls through to `PATH` |
| `scripts/render-{hero,part,assembly,in-use}.py` | dated notes | need Blender, which is **not installed here**; nothing could be proved |

Two traps in there worth remembering:

- **`draw_socket.py` binds `Path` to `matplotlib.path.Path`** (line 8), so the
  obvious `pathlib` fix would have broken it. Uses `os.path` deliberately.
- Its `socket-diagram.png` is **untracked and the only copy**. An
  `SOCKET_DIAGRAM_OUT` override was added so the run could be proved to `/tmp`
  with the existing artifact left byte-identical.

For the Blender scripts the correct self-locating `PROJECT` replacement is written
**into the note but left unapplied** — it cannot be verified without Blender, and
shipping an unprovable edit is how the next false note gets written.

### Two findings recorded, not silently patched

- **`npm test` was broken on Node 24** — the script ran `node --test test/`, and
  Node 24 treats a directory argument as a *file to execute*, throwing
  `Cannot find module`. **Fixed** to bare `node --test`, which auto-discovers;
  proved through `npm test` itself: 20 tests, 20 pass, rc=0.
  ⚠ That error nearly cost more than it should have: it reads as *"there is no test
  suite"*. There is — 4 files, 20 tests. Listing the directory settled it in one
  command where trusting the exception would have produced a false "missing" claim,
  which is the exact defect this whole piece of work existed to correct.
- ⚠ **Tracked STL outputs are not byte-reproducible.** Re-running the pipeline
  rewrote `designs/battery-capsule-holder/output/*.stl` with an **identical byte
  count** and roughly 6,000 reordered facet lines — same geometry, different facet
  order. Restored rather than committed. **Anyone running the pipeline will see a
  large phantom diff that contains no change.** Not yet addressed; the options are
  to stop tracking generated STLs, or to normalise facet order before writing.

## State At End

- `validate.js` passes end to end; `npm test` 20/20 via the documented command.
- Rendering, mesh analysis (trimesh) and validation all work. **Blender-dependent
  hero/assembly rendering does not** — the binary is absent, and those paths fail
  loudly by design.
- Design work untouched: `shibumi-beach-caddy-architecture` /
  `v3-rugged-cantilever` still **not passing** review.

## Next Action

`v3-rugged-cantilever` — it fails review and has never been diagnosed. The
validator it needs now actually runs, which it did not before today.
