# Battery Capsule Holder (Fusion) — v2 "zig-zag caterpillar"
# Clean-room iteration of the v1 filleted slab. Run via the Fusion MCP execute_code
# tool against an EMPTY active design. Units: Fusion API = cm (mm values are already
# in cm here, e.g. FAT_R 1.220 cm = 12.20 mm).
#
# v2 design: 6 teardrop sockets in a zig-zag chain (alternating +/-Y), each teardrop
# pointing nose-to-tail at the next so they nest; body = union of fat lobes + a zig-zag
# spine extruded as ONE profile set -> single caterpillar body; rounded head (eyes +
# antenna nubs) and tapered tail. Pitch/amplitude tuned (PITCH 22.3 / Y_AMP 10 mm) by a
# wall-distance optimizer to a 42-degree zig-zag spine at ~1.45 mm min inter-socket wall.
import adsk.core, adsk.fusion, math, traceback

app = adsk.core.Application.get()
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent

PITCH=2.23; Y_AMP=1.00; N=6           # cm
FAT_R=1.220; APEX_D=1.630             # teardrop pocket (12.20 / 16.30 mm)
LOBE_R=1.75; SPINE_R=1.00             # body lobe + zig-zag spine backstop
BODY_H=2.10; DEPTH=1.80               # 21 mm tall, 18 mm sockets, 3 mm floor
HEAD_R=2.05; TAIL_R=1.05

centers=[(i*PITCH,(Y_AMP if i%2==0 else -Y_AMP)) for i in range(N)]
dirs=[]
for i in range(N):
    if i<N-1: dx=centers[i+1][0]-centers[i][0]; dy=centers[i+1][1]-centers[i][1]
    else:     dx=centers[i][0]-centers[i-1][0]; dy=centers[i][1]-centers[i-1][1]
    m=math.hypot(dx,dy); dirs.append((dx/m,dy/m))

XY=root.xYConstructionPlane; P=adsk.core.Point3D.create
ex=root.features.extrudeFeatures

# --- 1) BODY: all lobe + spine circles in ONE sketch, extrude ALL profiles -> 1 body ---
bsk=root.sketches.add(XY); bc=bsk.sketchCurves.sketchCircles
def ac(cx,cy,r): bc.addByCenterRadius(P(cx,cy,0),r)
for c in centers: ac(c[0],c[1],LOBE_R)                                   # fat lobes
for i in range(N-1):                                                     # spine midpoints
    ac((centers[i][0]+centers[i+1][0])/2,(centers[i][1]+centers[i+1][1])/2,SPINE_R)
for c in centers: ac(c[0],c[1],SPINE_R)
hx=centers[0][0]-LOBE_R*0.85; hy=centers[0][1]; ac(hx,hy,HEAD_R)         # head lobe
tx=centers[-1][0]+dirs[-1][0]*LOBE_R*0.9; ty=centers[-1][1]+dirs[-1][1]*LOBE_R*0.9
ac(tx,ty,TAIL_R)                                                        # tail lobe
allp=adsk.core.ObjectCollection.create()
for k in range(bsk.profiles.count): allp.add(bsk.profiles.item(k))       # ALL profiles = full union
ei=ex.createInput(allp,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(BODY_H))
mb=ex.add(ei).bodies.item(0); mb.name="caterpillar_v2"
top_z=BODY_H

# --- 2) TEARDROP POCKETS: fitted spline (fat arc + apex), cut 18 mm from top ---
def td(cx,cy,ux,uy):
    sk=root.sketches.add(XY); pts=adsk.core.ObjectCollection.create()
    a0=math.atan2(uy,ux); st=a0+math.radians(50); en=a0+math.radians(310)
    for s in range(27):
        a=st+(en-st)*(s/26); pts.add(P(cx+FAT_R*math.cos(a),cy+FAT_R*math.sin(a),top_z))
    pts.add(P(cx+APEX_D*ux,cy+APEX_D*uy,top_z))
    f=pts.item(0); pts.add(P(f.x,f.y,top_z))
    sp=sk.sketchCurves.sketchFittedSplines.add(pts)
    try: sp.isClosed=True
    except: pass
    return sk
for i in range(N):
    sk=td(centers[i][0],centers[i][1],dirs[i][0],dirs[i][1])
    if sk.profiles.count==0: continue
    tp=sk.profiles.item(0); ta=tp.areaProperties().area
    for k in range(1,sk.profiles.count):
        a=sk.profiles.item(k).areaProperties().area
        if a>ta: ta=a; tp=sk.profiles.item(k)
    ci=ex.createInput(tp,adsk.fusion.FeatureOperations.CutFeatureOperation)
    ci.setDistanceExtent(False,adsk.core.ValueInput.createByReal(-DEPTH))
    try: ci.participantBodies=[mb]
    except: pass
    try: ex.add(ci)
    except: pass

# --- 3) lead-in chamfer at pocket rims (non-fatal) ---
try:
    ch=root.features.chamferFeatures; tf=None
    for f in mb.faces:
        if abs(f.boundingBox.minPoint.z-top_z)<1e-4 and abs(f.boundingBox.maxPoint.z-top_z)<1e-4: tf=f; break
    if tf:
        ec_=adsk.core.ObjectCollection.create()
        for e in tf.edges: ec_.add(e)
        ci2=ch.createInput2()
        ci2.chamferEdgeSets.addEqualDistanceChamferEdgeSet(ec_,adsk.core.ValueInput.createByReal(0.10),False)
        ch.add(ci2)
except: pass

# --- 4) head face: two eye dimples + two antenna nubs (non-fatal) ---
try:
    ns=root.sketches.add(XY); nc=ns.sketchCurves.sketchCircles
    nc.addByCenterRadius(P(hx-0.3,hy+0.7,top_z),0.18); nc.addByCenterRadius(P(hx-0.3,hy-0.7,top_z),0.18)
    nc.addByCenterRadius(P(hx-0.9,hy+0.4,top_z),0.10); nc.addByCenterRadius(P(hx-0.9,hy-0.4,top_z),0.10)
    for k in range(ns.profiles.count):
        ni=ex.createInput(ns.profiles.item(k),adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ni.setDistanceExtent(False,adsk.core.ValueInput.createByReal(0.35))
        try: ex.add(ni)
        except: pass
except: pass
