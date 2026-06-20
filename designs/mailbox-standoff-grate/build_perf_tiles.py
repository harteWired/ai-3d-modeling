"""Mailbox-standoff-grate — FINAL perforated + hollow-outline two-color tiles.

Container-side, fully reproducible (shapely 2D booleans + trimesh/manifold 3D welds).
Supersedes the solid-plate two-color outputs in output/print2c/ (those were the
pre-perforation design). The locked look was approved on the M tile (output/tileperf-M.stl,
output/pf-*.stl); this script reproduces that treatment for all four tiles.

Per tile the geometry is built from EXISTING validated artifacts so the jigsaw mating
(teeth/notches, interference=0) and leg layout are inherited, not re-derived:
  - deck footprint  = outer boundary of output/tile-<id>.stl (turbine holes filled back in)
  - legs            = leg footprints sliced from output/tile-<id>.stl below the deck
  - glyph           = Arial-Black letter sliced from output/print2c/<id>-letter.stl
                      (H2 reuses the H glyph — same letter)
  - hole stamp      = the exact turbine-blade pinwheel polygon extracted from the
                      approved output/tileperf-M.stl, tiled on a 19 x 22 mm grid

Treatment (matches the approved M):
  - perforated field: hole stamp on a tile-centered 19(x) x 22(y) grid, kept clear of a
    3 mm frame border, a 7 mm margin around the letter, and 22 mm off the two seam edges
  - hollow-outline letter: ring = glyph - erode(glyph, 3.5 mm); flush in the deck void
  - two-color split: base = deck(- glyph void) + legs ; letter = ring (both full 4 mm deck)

Outputs (in-use orientation: deck z=0..4 on top, legs z=-15..4 — full height through the
deck, flush with the show face; letter color is only the z=3..4 cap):
  output/tileperf-<id>.stl                 single-color welded tile
  output/print2c/<id>-base.stl             tan base (deck + legs, glyph void)
  output/print2c/<id>-letter.stl           letter-color hollow-outline ring
Print-orientation flip + 3MF bundling is done by bundle_bicolor.py.
"""
import os, math
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import translate

OUT = os.path.join(os.path.dirname(__file__), "output")
DECK = 4.0      # deck thickness (mm)
LEG = 15.0      # leg drop (mm)
HW, HH = 59.4, 84.8         # tile half-width / half-height (deck, excl. teeth)
FRAME = 3.0                 # solid perimeter / seam-rail band around the lattice
RIB_W = 1.8                 # cross-hatch rib width
CELL = 15.0                 # diagonal rib spacing (intercept step; perp pitch = CELL/sqrt2)
LETTER_MARGIN = 1.5         # field hatch stops this far short of the letter
DRAIN_D = 3.2               # small drain-hole diameter inside the (mostly solid) letter
DRAIN_PITCH = 9.0           # drain-hole grid pitch inside the letter
DRAIN_EDGE = 3.0            # keep drain holes this far inside the letter edge
COLOR_T = 1.0               # letter-color cap depth (top ~5 layers); rest of letter is base color

# Tile center in assembly coords -> sign tells which edges are interior seams.
TILES = {
    "M":  dict(cx=-59.4, cy=84.8,  glyph="M"),
    "H":  dict(cx=59.4,  cy=84.8,  glyph="H"),
    "H2": dict(cx=-59.4, cy=-84.8, glyph="H"),
    "K":  dict(cx=59.4,  cy=-84.8, glyph="K"),
}


def slice_polys(stl, z):
    """Return shapely Polygons (with holes) from a horizontal slice, in WORLD XY.

    trimesh's default to_2D() reprojects into an auto best-fit plane frame (which
    translates/rotates per file); pass an explicit transform so the planar coords
    stay world (x, y).
    """
    m = trimesh.load(stl, process=False)
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return [], m
    T = trimesh.transformations.translation_matrix([0, 0, -z])  # plane -> XY, no rotation
    p2, _ = sec.to_2D(to_2D=T)
    return [Polygon(g.exterior, [r for r in g.interiors]) for g in p2.polygons_full], m


def deck_footprint(letter, cx, cy):
    """Outer deck boundary, turbine holes filled, recentered to the tile origin."""
    polys, _ = slice_polys(os.path.join(OUT, f"tile-{letter}.stl"), DECK / 2)
    outer = Polygon(max(polys, key=lambda g: g.area).exterior)   # drop interiors
    return translate(outer, -cx, -cy)


def leg_polys(letter, cx, cy):
    polys, _ = slice_polys(os.path.join(OUT, f"tile-{letter}.stl"), -LEG / 2)
    return [translate(p, -cx, -cy) for p in polys]


# Solid Arial-Black glyph sources (write-safe — never overwritten by this script).
GLYPH_SRC = {"M": "glyphM.stl", "H": "glyph-H.stl", "K": "glyph-K.stl"}


def glyph_poly(glyph_letter):
    """Arial-Black letter, recentered to the origin."""
    polys, _ = slice_polys(os.path.join(OUT, GLYPH_SRC[glyph_letter]), DECK / 2)
    g = unary_union(polys)
    minx, miny, maxx, maxy = g.bounds
    return translate(g, -(minx + maxx) / 2, -(miny + maxy) / 2)


def lattice(region):
    """Continuous 45-degree cross-hatch of ribs, clipped to `region`."""
    from shapely.geometry import LineString
    minx, miny, maxx, maxy = region.bounds
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    L = max(maxx - minx, maxy - miny) * 1.2
    n = int(2 * L / CELL) + 2
    ribs = []
    for k in range(-n, n + 1):
        c = k * CELL
        ribs.append(LineString([(cx - L, cy - L + c), (cx + L, cy + L + c)]).buffer(RIB_W / 2))
        ribs.append(LineString([(cx - L, cy + L + c), (cx + L, cy - L + c)]).buffer(RIB_W / 2))
    return unary_union(ribs).intersection(region)


def letter_drain(glyph):
    """Small drain holes on a staggered grid, kept inside the letter body."""
    region = glyph.buffer(-DRAIN_EDGE)
    if region.is_empty:
        return Polygon()
    minx, miny, maxx, maxy = glyph.bounds
    holes = []
    row = 0
    y = miny
    while y <= maxy:
        off = (DRAIN_PITCH / 2) if row % 2 else 0.0
        x = minx + off
        while x <= maxx:
            from shapely.geometry import Point
            disc = Point(x, y).buffer(DRAIN_D / 2)
            if region.contains(disc):
                holes.append(disc)
            x += DRAIN_PITCH
        y += DRAIN_PITCH
        row += 1
    return unary_union(holes) if holes else Polygon()


def as_polys(geom):
    if geom.is_empty:
        return []
    return list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]


def extrude(geom, height, z0=0.0):
    """Return a list of clean volume meshes, one per polygon component."""
    meshes = []
    for p in as_polys(geom):
        if p.area < 1e-6:
            continue
        m = trimesh.creation.extrude_polygon(p, height)
        if z0:
            m.apply_translation([0, 0, z0])
        meshes.append(m)
    return meshes


def union(parts):
    """Weld a flat list of volume meshes (manifold handles disjoint bodies)."""
    m = trimesh.boolean.union(parts, engine="manifold")
    m.merge_vertices()
    m.fix_normals()
    return m


def difference(target, cutters):
    return trimesh.boolean.difference([target] + cutters, engine="manifold")


def carve(base_2d, *cut_regions):
    """Extrude base_2d to deck thickness and subtract the given 2D cut regions."""
    solid = extrude(base_2d, DECK)
    solid = solid[0] if len(solid) == 1 else union(solid)
    cutters = []
    for r in cut_regions:
        if r is not None and not r.is_empty:
            cutters += extrude(r, DECK + 0.4, z0=-0.2)
    return difference(solid, cutters) if cutters else solid


def build_tile(letter):
    t = TILES[letter]
    fp = deck_footprint(letter, t["cx"], t["cy"])
    glyph = glyph_poly(t["glyph"])

    inner = fp.buffer(-FRAME)                       # lattice lives inside the frame band
    ribs = lattice(inner)                           # continuous cross-hatch mesh
    field_open = inner.difference(ribs).difference(glyph.buffer(LETTER_MARGIN))  # open diamonds
    drain = letter_drain(glyph)                     # small holes in the solid letter
    glyph_solid = glyph.difference(drain)           # the mostly-solid letter body (with drains)

    # Feet run the FULL height — from the floor (z=-LEG) up THROUGH the deck, flush with
    # the deck top (z=DECK). Printed deck-top-down, the foot ends land on the bed coplanar
    # with the deck face, so the whole tile is anchored flat (no elevated deck = no bridge).
    legs = extrude(unary_union(leg_polys(letter, t["cx"], t["cy"])), LEG + DECK, z0=-LEG)

    # Full one-piece deck: cross-hatch field + mostly-solid drain-holed letter (z 0..DECK).
    deck_single = carve(fp, field_open, drain)
    # Letter color lives only in the top COLOR_T mm (the show face) -> one filament change.
    color_cap = union(extrude(glyph_solid, COLOR_T, z0=DECK - COLOR_T))

    base = union([difference(deck_single, [color_cap])] + legs)   # base filament
    letter_mesh = color_cap                                       # 2nd filament (top cap only)
    single = union([deck_single] + legs)                          # one-color reference

    p2c = os.path.join(OUT, "print2c")
    base.export(os.path.join(p2c, f"{letter}-base.stl"))
    letter_mesh.export(os.path.join(p2c, f"{letter}-letter.stl"))
    single.export(os.path.join(OUT, f"tileperf-{letter}.stl"))
    open_pct = 100 * field_open.area / inner.area
    return dict(letter=letter, single_vol=single.volume / 1000,
                base_vol=base.volume / 1000, ring_vol=letter_mesh.volume / 1000,
                wt=single.is_watertight, holes=round(open_pct))


if __name__ == "__main__":
    for L in ["M", "H", "H2", "K"]:
        r = build_tile(L)
        print(f"{r['letter']:3s} single={r['single_vol']:5.1f}cc wt={r['wt']!s:5s} "
              f"base={r['base_vol']:5.1f}cc letter={r['ring_vol']:4.1f}cc field_open={r['holes']}%")
