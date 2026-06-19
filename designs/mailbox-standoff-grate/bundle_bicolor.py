"""Bundle each tile's base + hollow-outline letter into a print-oriented 3MF.

Reads output/print2c/<id>-base.stl + <id>-letter.stl (in-use orientation: deck
z=0..4 on top, legs z=0..-15). Flips 180 deg about X so the deck sits on the bed
and the legs point up (no bridges), then writes a two-object 3MF that Bambu Studio
opens with the base and letter as separate objects (assign one filament to each).
"""
import os
import numpy as np
import trimesh

OUT = os.path.join(os.path.dirname(__file__), "output")
P2C = os.path.join(OUT, "print2c")
TILES = ["M", "H", "H2", "K"]


def print_orient(mesh):
    """Rotate 180 deg about X (deck -> bed, legs up), drop to z=0."""
    m = mesh.copy()
    R = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    m.apply_transform(R)
    m.apply_translation([0, 0, -m.bounds[0][2]])
    return m


def bundle(letter):
    base = print_orient(trimesh.load(os.path.join(P2C, f"{letter}-base.stl")))
    ring = print_orient(trimesh.load(os.path.join(P2C, f"{letter}-letter.stl")))
    scene = trimesh.Scene()
    scene.add_geometry(base, geom_name=f"{letter}_base", node_name=f"{letter}_base")
    scene.add_geometry(ring, geom_name=f"{letter}_letter", node_name=f"{letter}_letter")
    path = os.path.join(P2C, f"{letter}-bicolor.3mf")
    scene.export(path)
    return path, base.bounds, ring.is_watertight and base.is_watertight


if __name__ == "__main__":
    for L in TILES:
        path, b, wt = bundle(L)
        size = (b[1] - b[0]).round(1)
        print(f"{L:3s} -> {os.path.basename(path)}  bbox={size}  wt={wt}")
