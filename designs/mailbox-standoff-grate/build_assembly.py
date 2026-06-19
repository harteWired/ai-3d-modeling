"""Mailbox-standoff-grate — 2x2 jigsaw assembly builder (Fusion 360 MCP).

Supersedes build_quadrant.py (which was the early ADDITIVE rib approach).
Final design is SUBTRACTIVE: a solid full-thickness plate with the swirl drainage
cut OUT as turbine-shaped through-holes (robust, full-width material between holes,
no thin arms). The letter is a bold solid region of the same plate, made prominent
by a narrow recessed U-channel groove tracing its outline.

Run each tile via mcp__fusion__execute_code in the MAIN session (modeler-fusion is
blind). Each call builds ONE tile in a FRESH doc (documents.add) to avoid the 30 s
timeout from stale-sketch clutter. Export each as tile-<id>.stl to the Windows path
C:\\Users\\aes\\Documents\\AI\\Claude Code in Container\\projects\\3d-printing\\...
which maps to designs/mailbox-standoff-grate/output/ in-container.

Coordinates: REAL assembly coords, mm (×0.1 → cm for the API). Assembly centered at
origin: X∈[-118.8,118.8] (237.6 wide), Y∈[-169.6,169.6] (339.2 deep). Deck z=0..4,
legs z=0..-15 (in-use orientation; flip 180° about X for printing → deck on bed,
legs up, no bridges).

Jigsaw: dovetail teeth (neck 8, head 13, depth 8 mm — re-entrant so they lock in
plane) along the two interior seams (X=0, Y=0). Ownership alternates; each tile UNIONs
its owned teeth and CUTs the neighbour's teeth + 0.2 mm clearance as notches. Teeth sit
on a 10 mm solid seam rail. Teeth placed at ±20 from center reinforce the 4-way junction;
holes are kept ≥22 mm off both seams so the center stays solid.

Per-tile params: (letter, body_name, cx, cy, vdir, hdir, vown, vnotch, hown, hnotch, legs)
  vdir = +1 if tile is LEFT of the vertical seam (teeth protrude +X), else -1
  hdir = -1 if tile is BACK of the horizontal seam (teeth protrude -Y), else +1
  legs: front-row legs are at |y|≤135 (≥30 mm behind the front wall at y=-169.6);
        outer legs ≥~20 mm inboard of the mailbox walls.

TILES = {
  # back-left  M : vseam Y>0 owns 20,100 / notch 60,140 ; hseam X<0 owns -20,-100 / notch -60
  'M' : ('M','quad_M', -59.4, 84.8, +1,-1, [20,100],[60,140], [-20,-100],[-60],
         [(-100,150),(-100,30),(-30,150),(-30,40)]),
  # back-right H : vseam owns 60,140 / notch 20,100 ; hseam X>0 owns 20,100 / notch 60
  'H' : ('H','quad_H',  59.4, 84.8, -1,-1, [60,140],[20,100], [20,100],[60],
         [(100,150),(100,30),(30,150),(30,40)]),
  # front-left H2 (letter H) : vseam Y<0 owns -20,-100 / notch -60,-140 ; hseam owns -60 / notch -20,-100
  'H2': ('H','quad_H2',-59.4,-84.8, +1,+1, [-20,-100],[-60,-140], [-60],[-20,-100],
         [(-100,-135),(-100,-30),(-30,-135),(-30,-40)]),
  # front-right K : vseam owns -60,-140 / notch -20,-100 ; hseam owns 60 / notch 20,100
  'K' : ('K','quad_K',  59.4,-84.8, -1,+1, [-60,-140],[-20,-100], [60],[20,100],
         [(100,-135),(100,-30),(30,-135),(30,-40)]),
}

Validated 2026-06-18: all 4 watertight; all 6 pairwise interference checks = 0;
assembly 237.6×339.2×19 mm; each print-oriented tile 126.8×177.6 mm (fits 256 bed);
~311 cm³ / ~386 g PLA total. Print review PASS WITH CONDITIONS (brim + slicer check).
"""
import adsk.core, adsk.fusion, math

def build_tile(letter, name, cx, cy, vdir, hdir, vown, vnotch, hown, hnotch, legs):
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)   # fresh doc
    root = app.activeProduct.rootComponent
    xy = root.xYConstructionPlane
    extrudes = root.features.extrudeFeatures
    F = 0.1
    NB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    DECK, LEG, HW, HH, GR = 4.0, 15.0, 59.4, 84.8, 1.5
    T, NW, HEAD, CL = 8.0, 8.0, 13.0, 0.2

    def ext(prof, h, op): return extrudes.addSimple(prof, adsk.core.ValueInput.createByReal(h * F), op)
    def poly(pts, plane=None):
        s = root.sketches.add(plane or xy); L = s.sketchCurves.sketchLines; n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6: continue
            L.addByTwoPoints(adsk.core.Point3D.create(a[0]*F, a[1]*F, 0), adsk.core.Point3D.create(b[0]*F, b[1]*F, 0))
        return s.profiles.item(0) if s.profiles.count > 0 else None
    def rectp(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    def lin(a0, a1, n): return [a0 + (a1 - a0) * i / (n - 1) for i in range(n)]
    def vtooth(yc, xd, nw, hd, dp): return poly([(0, yc-nw/2), (xd*dp, yc-hd/2), (xd*dp, yc+hd/2), (0, yc+nw/2)])
    def htooth(xc, yd, nw, hd, dp): return poly([(xc-nw/2, 0), (xc-hd/2, yd*dp), (xc+hd/2, yd*dp), (xc+nw/2, 0)])
    def text_prof(s_text, h, bx0, by0, bx1, by1, plane=None):
        s = root.sketches.add(plane or xy); Tt = s.sketchTexts
        ti = Tt.createInput2(s_text, h * F)
        ti.setAsMultiLine(adsk.core.Point3D.create(bx0*F, by0*F, 0), adsk.core.Point3D.create(bx1*F, by1*F, 0),
            adsk.core.HorizontalAlignments.CenterHorizontalAlignment, adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
        try: ti.fontName = 'Arial Black'
        except: pass
        try: ti.isBold = True
        except: pass
        return Tt.add(ti)

    ext(rectp(cx-HW, cy-HH, cx+HW, cy+HH), DECK, NB)                       # solid plate
    xs = [cx-36, cx, cx+36]; ys = [cy-50, cy, cy+50]                       # swirl turbine holes
    base = math.radians(20); swl = math.radians(22); r0, r1 = 4.0, 16.0
    ih = math.radians(5); oh = math.radians(30)
    for hx in xs:
        for hy in ys:
            if abs(hx) < 22 or abs(hy) < 22: continue                     # keep seams/center solid
            for k in range(4):
                b = base + k * math.pi / 2
                inner = [(hx+r0*math.cos(a), hy+r0*math.sin(a)) for a in lin(b-ih, b+ih, 2)]
                oc = b + swl
                outer = [(hx+r1*math.cos(a), hy+r1*math.sin(a)) for a in lin(oc+oh, oc-oh, 6)]
                pr = poly(inner + outer)
                if pr: ext(pr, DECK, CUT)
    ext(rectp(0, cy-HH, -vdir*10, cy+HH), DECK, NB)                       # vertical seam rail
    ext(rectp(cx-HW, 0, cx+HW, -hdir*10), DECK, NB)                       # horizontal seam rail
    for yc in vown:                                                       # owned teeth
        p = vtooth(yc, vdir, NW, HEAD, T); p and ext(p, DECK, NB)
    for xc in hown:
        p = htooth(xc, hdir, NW, HEAD, T); p and ext(p, DECK, NB)
    ext(text_prof(letter, 86, cx-46, cy-44, cx+46, cy+44), DECK, NB)      # bold solid letter
    for yc in vnotch:                                                     # neighbour notches + clearance
        p = vtooth(yc, -vdir, NW+2*CL, HEAD+2*CL, T+CL); p and ext(p, DECK, CUT)
    for xc in hnotch:
        p = htooth(xc, -hdir, NW+2*CL, HEAD+2*CL, T+CL); p and ext(p, DECK, CUT)
    for (lx, ly) in legs:                                                 # legs (point -Z; flip for print)
        p = rectp(lx-6, ly-6, lx+6, ly+6); p and ext(p, -LEG, NB)
    bodies = root.bRepBodies; n = bodies.count                           # combine to one body
    if n >= 2:
        tgt = bodies.item(0); tools = adsk.core.ObjectCollection.create()
        for i in range(1, n): tools.add(bodies.item(i))
        ci = root.features.combineFeatures.createInput(tgt, tools)
        ci.operation = JOIN; ci.isKeepToolBodies = False; ci.isNewComponent = False
        root.features.combineFeatures.add(ci)
    try:                                                                  # U-channel letter outline (top face)
        pin = root.constructionPlanes.createInput()
        pin.setByOffset(xy, adsk.core.ValueInput.createByReal(DECK * F))
        pl = root.constructionPlanes.add(pin)
        ext(text_prof(letter, 86, cx-46, cy-44, cx+46, cy+44, pl), -GR, CUT)   # recess
        ext(text_prof(letter, 80, cx-43, cy-41, cx+43, cy+41, pl), -GR, JOIN)  # refill core flush
    except Exception:
        pass
    root.bRepBodies.item(0).name = name
    return root.bRepBodies.count

# build_tile('M','quad_M', -59.4,84.8, +1,-1, [20,100],[60,140], [-20,-100],[-60], [(-100,150),(-100,30),(-30,150),(-30,40)])
