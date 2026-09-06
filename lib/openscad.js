import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { unlink } from 'node:fs/promises';

const execFileAsync = promisify(execFile);

const SCAD_LIB_DIR = path.resolve(import.meta.dirname, '..', 'scad-lib');

// Resolved via PATH, overridable by env. Was hardcoded to
// /home/node/.cli-anything-venv/bin/cli-anything-openscad — a Jinn-container path that does not
// exist on this host, so every render failed with ENOENT while the tool sat installed on PATH.
// Deliberately NOT repointed to the new absolute path (the new host's absolute path): that recreates
// the same bug one host-move later. execFile does a PATH lookup for a bare name, and an ENOENT
// here names the binary it could not find.
const CLI = process.env.CLI_ANYTHING_OPENSCAD || 'cli-anything-openscad';

/**
 * Run the cli-anything-openscad CLI and parse JSON output.
 * Preserves stderr in error objects for caller diagnostics.
 */
export async function runCLI(args, timeout = 120_000) {
  let stdout, stderr;
  try {
    ({ stdout, stderr } = await execFileAsync(CLI, ['--json', ...args], { timeout }));
  } catch (err) {
    // execFile errors already have .stderr — rethrow as-is
    throw err;
  }

  try {
    return JSON.parse(stdout);
  } catch (parseErr) {
    const err = new Error(`CLI returned invalid JSON: ${stdout.slice(0, 200)}`);
    err.stderr = stderr;
    err.stdout = stdout;
    throw err;
  }
}

/**
 * Create a temporary project file for a SCAD source.
 * Uses a unique suffix to avoid races between concurrent renders.
 * @param {string} scadPath - path to .scad file
 * @returns {Promise<string>} project file path
 */
export async function createProject(scadPath) {
  const name = path.basename(scadPath, '.scad');
  const suffix = randomUUID().slice(0, 8);
  const projectFile = path.join(path.dirname(scadPath), `.${name}.${suffix}.cli-project.json`);

  await runCLI([
    'project', 'new',
    '-n', name,
    '-s', scadPath,
    '-o', projectFile,
    '-l', SCAD_LIB_DIR,
  ]);

  return projectFile;
}

/**
 * Clean up a temporary project file. Best-effort, non-throwing.
 */
async function cleanupProject(projectFile) {
  try { await unlink(projectFile); } catch {}
}

/**
 * Set multiple params on a project file concurrently.
 */
async function setParams(projectFile, params) {
  if (!params || Object.keys(params).length === 0) return;
  await Promise.all(
    Object.entries(params).map(([key, value]) =>
      runCLI(['-p', projectFile, 'params', 'set', key, String(value)], 10_000)
    )
  );
}

/**
 * Render an OpenSCAD file to STL.
 * @param {string} scadPath - path to .scad file
 * @param {string} outputPath - path for output .stl file
 * @param {Object} [params] - key/value pairs passed as -D overrides
 * @param {string} [projectFile] - reuse an existing project file
 * @returns {Promise<{echoes: Object[], dimensions: Object, stderr: string}>}
 */
export async function renderSTL(scadPath, outputPath, params = {}, projectFile) {
  const ownProject = !projectFile;
  if (ownProject) projectFile = await createProject(scadPath);

  try {
    await setParams(projectFile, params);
    const result = await runCLI(['-p', projectFile, 'render', 'stl', '-o', outputPath, '--overwrite']);

    return {
      echoes: result.data?.echoes ?? [],
      dimensions: result.data?.dimensions ?? {},
      stderr: (result.data?.warnings ?? []).join('\n'),
    };
  } finally {
    if (ownProject) await cleanupProject(projectFile);
  }
}

/**
 * Render an OpenSCAD file to PNG with specific camera angle.
 * @param {string} scadPath - path to .scad file
 * @param {string} outputPath - path for output .png file
 * @param {Object} options - rendering options
 * @param {string} options.camera - camera position "tx,ty,tz,rx,ry,rz,d"
 * @param {number[]} [options.size] - image size [width, height]
 * @param {Object} [options.params] - -D overrides
 * @param {string} [options.projectFile] - reuse an existing project file
 * @returns {Promise<{echoes: Object[], dimensions: Object, stderr: string}>}
 */
export async function renderPNG(scadPath, outputPath, options = {}) {
  const ownProject = !options.projectFile;
  let projectFile = options.projectFile;
  if (ownProject) projectFile = await createProject(scadPath);

  try {
    await setParams(projectFile, options.params);

    const args = ['-p', projectFile, 'render', 'png', '-o', outputPath, '--overwrite'];

    if (options.camera) {
      args.push('--camera', options.camera);
    }
    if (options.size) {
      args.push('--imgsize', `${options.size[0]}x${options.size[1]}`);
    }

    const result = await runCLI(args);

    return {
      echoes: result.data?.echoes ?? [],
      dimensions: result.data?.dimensions ?? {},
      stderr: (result.data?.warnings ?? []).join('\n'),
    };
  } finally {
    if (ownProject) await cleanupProject(projectFile);
  }
}
