# Battery-capsule drawer organizer — 6 interlocked teardrop pockets.
# Clean-room independent Fusion 360 design (authored by an isolated agent that never
# saw the OpenSCAD solution). Run via the Fusion MCP `execute_code` tool against an
# empty active design. Units: Fusion API = cm; MM helper converts mm -> cm.
import adsk.core, adsk.fusion, math

MM = 0.1  # multiply mm by this to get cm

app = adsk.core.Application.get()
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent

# ---------- Parameters (mm) ----------
CAP_LONG   = 27.8     # teardrop long axis (fat->point)
CAP_NARROW = 23.7     # teardrop narrow axis
CLR        = 0.35     # per-side clearance (loose drop-in)
SOCKET_D   = 18.0     # socket depth (fixed requirement)
FLOOR      = 3.0      # solid floor under each socket
BODY_H     = SOCKET_D + FLOOR          # 21.0 total height
MARGIN     = 4.0      # outer wall / edge margin
BODY_FILLET= 3.0      # outer edge fillet
MOUTH_CHAM = 1.0      # 45-deg lead-in chamfer at pocket mouth
FOOT_DIA   = 15.0     # rubber-pad recess diameter
FOOT_DEPTH = 1.2      # rubber-pad recess depth

R      = CAP_NARROW / 2.0          # fat-end radius 11.85
x_apex = CAP_LONG - R              # 15.95 apex distance from fat center
Rp     = R + CLR                   # pocket fat radius 12.20
x_ap_p = x_apex + CLR              # pocket apex distance 16.30

# Pocket fat-circle centers (mm) + apex rotation (deg). rot=90 -> apex +Y; 270 -> -Y
PLACEMENTS = [
    (-24.0,   9.75,  90), (-24.0, -20.75,  90),
    ( 24.0,   9.75,  90), ( 24.0, -20.75,  90),
    (  0.0,  20.75, 270), (  0.0,  -9.75, 270),
]
BODY_X = 72.4 + 2 * MARGIN   # 80.4
BODY_Y = 65.9 + 2 * MARGIN   # 73.9

def P3(x_mm, y_mm, z_mm):
    return adsk.core.Point3D.create(x_mm * MM, y_mm * MM, z_mm * MM)

def teardrop_points(cx, cy, rot_deg, n_arc=28):
    d  = x_ap_p
    th = math.acos(Rp / d)
    rr = math.radians(rot_deg)
    cr, sr = math.cos(rr), math.sin(rr)
    pts = []
    a0, a1 = th, 2 * math.pi - th
    for i in range(n_arc + 1):
        a = a0 + (a1 - a0) * i / n_arc
        lx, ly = Rp * math.cos(a), Rp * math.sin(a)
        wx, wy = cx + (lx * cr - ly * sr), cy + (lx * sr + ly * cr)
        pts.append(P3(wx, wy, 0))
    lx, ly = d, 0.0
    wx, wy = cx + (lx * cr - ly * sr), cy + (lx * sr + ly * cr)
    pts.append(P3(wx, wy, 0))
    return pts

# 1) OUTER BODY — rounded-rectangle slab
xyPlane = root.xYConstructionPlane
sk_body = root.sketches.add(xyPlane)
hw, hh = BODY_X / 2.0, BODY_Y / 2.0
sk_body.sketchCurves.sketchLines.addCenterPointRectangle(P3(0, 0, 0), P3(hw, hh, 0))
prof = sk_body.profiles.item(0)
extrudes = root.features.extrudeFeatures
ext_in = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ext_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(BODY_H * MM))
body = extrudes.add(ext_in).bodies.item(0)
body.name = "OrganizerBody"

# Fillet outer vertical + top edges (skip bottom for flat print)
fillet_edges = adsk.core.ObjectCollection.create()
top_z = BODY_H * MM
for e in body.edges:
    bb = e.boundingBox
    is_vertical = abs(bb.maxPoint.z - bb.minPoint.z) > (BODY_H * MM * 0.5)
    is_top = abs(bb.minPoint.z - top_z) < 1e-4 and abs(bb.maxPoint.z - top_z) < 1e-4
    if is_vertical or is_top:
        fillet_edges.add(e)
if fillet_edges.count > 0:
    fil_in = root.features.filletFeatures.createInput()
    fil_in.addConstantRadiusEdgeSet(fillet_edges, adsk.core.ValueInput.createByReal(BODY_FILLET * MM), True)
    try: root.features.filletFeatures.add(fil_in)
    except: pass

# 2) SIX TEARDROP POCKETS — cut from a top-offset plane downward
top_plane_in = root.constructionPlanes.createInput()
top_plane_in.setByOffset(xyPlane, adsk.core.ValueInput.createByReal(BODY_H * MM))
top_plane = root.constructionPlanes.add(top_plane_in)
sk_pock = root.sketches.add(top_plane)
sk_pock.name = "PocketProfiles"
for (cx, cy, rot) in PLACEMENTS:
    oc = adsk.core.ObjectCollection.create()
    for p in teardrop_points(cx, cy, rot):
        oc.add(p)
    spline = sk_pock.sketchCurves.sketchFittedSplines.add(oc)
    try: spline.isClosed = True
    except: sk_pock.sketchCurves.sketchLines.addByTwoPoints(spline.startSketchPoint, spline.endSketchPoint)
cut_done = 0
for i in range(sk_pock.profiles.count):
    cut_in = extrudes.createInput(sk_pock.profiles.item(i), adsk.fusion.FeatureOperations.CutFeatureOperation)
    cut_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-SOCKET_D * MM))
    try:
        extrudes.add(cut_in); cut_done += 1
    except: pass

# 3) POCKET-MOUTH CHAMFERS — 45-deg lead-in at interior top edges
top_face = None
for f in body.faces:
    bb = f.boundingBox
    if abs(bb.minPoint.z - top_z) < 1e-4 and abs(bb.maxPoint.z - top_z) < 1e-4:
        top_face = f; break
cham_edges = adsk.core.ObjectCollection.create()
if top_face is not None:
    px, py = BODY_X / 2.0 * MM, BODY_Y / 2.0 * MM
    for e in top_face.edges:
        bb = e.boundingBox
        near = (abs(abs(bb.minPoint.x) - px) < 0.5*MM or abs(abs(bb.maxPoint.x) - px) < 0.5*MM or
                abs(abs(bb.minPoint.y) - py) < 0.5*MM or abs(abs(bb.maxPoint.y) - py) < 0.5*MM)
        if not near: cham_edges.add(e)
if cham_edges.count > 0:
    try:
        cham_in = root.features.chamferFeatures.createInput(cham_edges, True)
        cham_in.setToEqualDistance(adsk.core.ValueInput.createByReal(MOUTH_CHAM * MM))
        root.features.chamferFeatures.add(cham_in)
    except: pass

# 4) NON-SLIP BASE — 4 recessed rubber-pad pockets on underside
inset = MARGIN + FOOT_DIA / 2.0 + 2.0
fx, fy = BODY_X / 2.0 - inset, BODY_Y / 2.0 - inset
sk_feet = root.sketches.add(xyPlane)
sk_feet.name = "FootRecesses"
for sx in (-1, 1):
    for sy in (-1, 1):
        sk_feet.sketchCurves.sketchCircles.addByCenterRadius(P3(sx*fx, sy*fy, 0), (FOOT_DIA/2.0)*MM)
for i in range(sk_feet.profiles.count):
    f_in = extrudes.createInput(sk_feet.profiles.item(i), adsk.fusion.FeatureOperations.CutFeatureOperation)
    f_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(FOOT_DEPTH * MM))
    try: extrudes.add(f_in)
    except: pass
