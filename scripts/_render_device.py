"""Configure Cycles compute device — picks the best available backend,
falls back cleanly when no GPU is present.

This module is shared by every Blender render harness in `scripts/`. It exists
because hardcoding `scene.cycles.device = "CPU"` leaves a 4090 idle on dev
boxes while still letting CI / GPU-less laptops Just Work.

Resolution order
----------------
1. **`CYCLES_DEVICE` env var** (highest priority — explicit user override):
   - `"CPU"` → force CPU
   - `"GPU"` → use the best auto-detected backend, fall back to CPU if none
   - `"OPTIX"` / `"CUDA"` / `"HIP"` / `"METAL"` / `"ONEAPI"` → force that
     specific backend; fall back to CPU if Blender can't enumerate any device
     of that type
2. **Auto-detect** (default): probe backends in preference order
   `OPTIX → CUDA → HIP → METAL → ONEAPI`; first one with a working device wins.
3. **CPU fallback** if nothing GPU-shaped is available.

Logs a single `[render-device]` line so the user can see what got picked.

Public API
----------
- `configure_cycles_device(scene) -> dict`
  Returns `{"mode": "GPU"|"CPU", "backend": str, "devices": [str], "reason": str}`.
  Safe to call before `scene.render.engine` is set — only touches Cycles state
  when needed.
"""

import os


_BACKEND_PREFERENCE = ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI")
_VALID_BACKENDS = set(_BACKEND_PREFERENCE) | {"NONE", "CPU", "GPU"}


def _enable_backend(prefs, backend):
    """Try to switch Cycles to a specific backend and enable its devices.

    Returns a list of device names that got enabled, or [] on failure.
    """
    try:
        prefs.compute_device_type = backend
    except (TypeError, ValueError):
        return []

    try:
        prefs.refresh_devices()
    except Exception:
        pass

    enabled = []
    for d in prefs.devices:
        if d.type == backend:
            d.use = True
            enabled.append(d.name)
        elif d.type == "CPU":
            d.use = False
    return enabled


def configure_cycles_device(scene):
    """Pick the best Cycles compute device for this scene.

    Honors $CYCLES_DEVICE override, falls back to CPU on any failure. Always
    prints a one-line summary so the user can confirm what's actually running.
    """
    try:
        import bpy
    except ImportError:
        return {"mode": "CPU", "backend": "NONE", "devices": [], "reason": "bpy unavailable"}

    override_raw = os.environ.get("CYCLES_DEVICE", "").strip().upper()
    override = override_raw if override_raw in _VALID_BACKENDS else None
    if override_raw and not override:
        print(f"[render-device] Ignoring invalid CYCLES_DEVICE={override_raw!r}")

    if override == "CPU":
        scene.cycles.device = "CPU"
        print("[render-device] Forced CPU via CYCLES_DEVICE=CPU")
        return {"mode": "CPU", "backend": "NONE", "devices": [], "reason": "env override"}

    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except (KeyError, AttributeError):
        scene.cycles.device = "CPU"
        print("[render-device] Cycles addon prefs unavailable — using CPU")
        return {"mode": "CPU", "backend": "NONE", "devices": [], "reason": "no cycles prefs"}

    if override and override not in ("GPU", "CPU"):
        candidates = [override]
    elif override == "GPU" or override is None:
        candidates = list(_BACKEND_PREFERENCE)
    else:
        candidates = []

    for backend in candidates:
        devices = _enable_backend(prefs, backend)
        if devices:
            scene.cycles.device = "GPU"
            print(f"[render-device] GPU via {backend}: {', '.join(devices)}")
            return {"mode": "GPU", "backend": backend, "devices": devices, "reason": "auto"}

    scene.cycles.device = "CPU"
    if override and override != "CPU":
        reason = f"requested {override} unavailable"
        print(f"[render-device] {override} requested but no devices found — falling back to CPU")
    else:
        reason = "no GPU devices found"
        print("[render-device] No GPU backend available — using CPU")
    return {"mode": "CPU", "backend": "NONE", "devices": [], "reason": reason}
