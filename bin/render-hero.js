#!/usr/bin/env node
/**
 * render-hero.js — Blender-driven hero renders for ship STLs.
 *
 * Picks the static Blender 4.x at /home/node/blender/blender (with OIDN denoiser)
 * if present; otherwise falls back to system `blender` (apt build, no denoiser).
 *
 * Usage:
 *   node bin/render-hero.js --stl PATH --out PATH [opts]
 *   node bin/render-hero.js --design designs/<name> [opts]    # all part STLs
 *
 * Options:
 *   --quality {draft,standard,hero}   Tier (default: standard)
 *   --angle NAME                      Camera preset (default: threequarter)
 *                                     (iso, front, back, right, left, top,
 *                                      front-threequarter, rear-threequarter,
 *                                      top-threequarter, threequarter)
 *   --preset PATH                     Override the default studio preset .py
 *                                     (auto-detects designs/<name>/id/render-preset.py
 *                                      when --design is used)
 *   --samples N                       Override quality's sample count
 *   --resolution WxH                  Override quality's resolution
 *   --engine CYCLES|BLENDER_EEVEE_NEXT  Override quality's engine
 *   --glb                             Also export GLB next to PNG (web 3D)
 */

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, join, resolve, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, "..");
const RENDER_SCRIPT = join(PROJECT_ROOT, "scripts", "render-hero.py");
const DEFAULT_PRESET = join(PROJECT_ROOT, "scad-lib", "blender-presets", "studio.py");
// Jinn-era preference, kept deliberately: this is NOT the bug lib/openscad.js had. The existsSync
// check means a missing path falls through to PATH rather than failing, so it degrades correctly.
// ⛔ Blender is not installed on this host at all (measured 2026-09-06) — neither branch resolves,
// and this exits with a loud ENOENT naming `blender`. That is the right behaviour; do not "fix" it
// by pointing at a path that does not exist either.
const STATIC_BLENDER = "/home/node/blender/blender";

function pickBlender() {
  if (existsSync(STATIC_BLENDER)) return STATIC_BLENDER;
  return "blender";
}

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const flag = argv[i];
    if (!flag.startsWith("--")) continue;
    const key = flag.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      args[key] = next;
      i++;
    } else {
      args[key] = true;
    }
  }
  return args;
}

function renderOne({ stl, out, preset, quality, angle, samples, resolution, engine, glb }) {
  if (!existsSync(stl)) {
    console.error(`ERROR: STL not found: ${stl}`);
    process.exit(1);
  }
  mkdirSync(dirname(resolve(out)), { recursive: true });

  const blenderArgs = [
    "--background",
    "--python", RENDER_SCRIPT,
    "--",
    "--stl", resolve(stl),
    "--out", resolve(out),
    "--preset", resolve(preset || DEFAULT_PRESET),
    "--quality", quality || "standard",
    "--angle", angle || "threequarter",
  ];
  if (samples !== undefined) blenderArgs.push("--samples", String(samples));
  if (resolution) blenderArgs.push("--resolution", resolution);
  if (engine) blenderArgs.push("--engine", engine);
  if (glb) blenderArgs.push("--glb", resolve(glb));

  const blender = pickBlender();
  console.log(`[render-hero] ${stl} -> ${out} (${quality || "standard"}, ${angle || "threequarter"}, ${blender === STATIC_BLENDER ? "static" : "system"})`);

  const start = Date.now();
  const result = spawnSync(blender, blenderArgs, { stdio: "inherit" });
  const elapsed = ((Date.now() - start) / 1000).toFixed(1);

  if (result.status !== 0) {
    console.error(`[render-hero] FAILED (${elapsed}s, exit ${result.status})`);
    process.exit(result.status || 1);
  }
  console.log(`[render-hero] OK (${elapsed}s)`);
}

function findDesignStls(designDir) {
  const outDir = join(designDir, "output");
  if (!existsSync(outDir)) return [];
  return readdirSync(outDir)
    .filter(f => f.endsWith(".stl"))
    .map(f => join(outDir, f));
}

function main() {
  const args = parseArgs(process.argv);

  if (args.design) {
    const designDir = resolve(args.design);
    const stls = findDesignStls(designDir);
    if (stls.length === 0) {
      console.error(`ERROR: no STLs in ${designDir}/output/`);
      process.exit(1);
    }
    const designPreset = join(designDir, "id", "render-preset.py");
    const preset = args.preset
      ? args.preset
      : existsSync(designPreset) ? designPreset : DEFAULT_PRESET;

    for (const stl of stls) {
      const name = basename(stl, ".stl");
      const out = join(designDir, "output", `${name}-hero.png`);
      const glbPath = args.glb ? join(designDir, "output", `${name}.glb`) : undefined;
      renderOne({
        stl, out, preset,
        quality: args.quality, angle: args.angle,
        samples: args.samples, resolution: args.resolution, engine: args.engine,
        glb: glbPath,
      });
    }
    return;
  }

  if (!args.stl || !args.out) {
    console.error("Usage: node bin/render-hero.js --stl PATH --out PATH [opts]");
    console.error("   or: node bin/render-hero.js --design designs/<name> [opts]");
    process.exit(1);
  }
  const glbPath = args.glb === true
    ? args.out.replace(/\.png$/i, ".glb")
    : (typeof args.glb === "string" ? args.glb : undefined);

  renderOne({
    stl: args.stl, out: args.out, preset: args.preset,
    quality: args.quality, angle: args.angle,
    samples: args.samples, resolution: args.resolution, engine: args.engine,
    glb: glbPath,
  });
}

main();
