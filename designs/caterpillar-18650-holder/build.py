# Caterpillar 18650 Holder — derivative of the Caterpillar Capsule Holder for bare
# 18650 cells (button-top), inserted POSITIVE-SIDE-DOWN with a nipple indent in each
# socket floor for the positive button. Run via the Fusion MCP execute_code tool against
# an EMPTY active design. Units: Fusion API = cm (values below are cm; 0.96 cm = 9.6 mm).
#
# Geometry pattern note: every sub-sketch is on the XY plane with the target Z baked into
# the point coordinates (NOT on an offset construction plane — offset planes double-stack
# the Z). Bores/nipples/eyes cut downward from their baked Z; antenna nubs join upward and
# share the top face so they merge into the single body.
import adsk.core, adsk.fusion, math

app=adsk.core.Application.get(); design=adsk.fusion.Design.cast(app.activeProduct); root=design.rootComponent
P=adsk.core.Point3D.create

N=6
BORE_R=0.96            # 9.6 mm radius -> 19.2 mm bore (18650 ~18.4 mm + 0.4 mm/side, loose drop-in)
PITCH=1.525; Y_AMP=0.70  # zig-zag: adjacent centre dist 20.7 mm -> ~1.5 mm wall, ~42 deg spine
LOBE_R=1.26; HEAD_R=1.42; TAIL_R=1.00; SPINE_R=0.78
BODY_H=2.10; DEPTH=1.80; FLOOR_Z=BODY_H-DEPTH   # 21 mm body, 18 mm socket, 3 mm floor
NIP_R=0.35; NIP_DEPTH=0.18   # nipple indent: 7 mm dia x 1.8 mm deep (positive button clearance)
CHAMFER=0.10                 # 1 mm x 45 lead-in

centers=[(i*PITCH,(Y_AMP if i%2==0 else -Y_AMP)) for i in range(N)]
dirs=[]
for i in range(N):
    if i<N-1: dx=centers[i+1][0]-centers[i][0]; dy=centers[i+1][1]-centers[i][1]
    else:     dx=centers[i][0]-centers[i-1][0]; dy=centers[i][1]-centers[i-1][1]
    m=math.hypot(dx,dy); dirs.append((dx/m,dy/m))
XY=root.xYConstructionPlane; ex=root.features.extrudeFeatures

# 1) BODY — lobes + zig-zag spine + head + tail; extrude ALL profiles as ONE body
bsk=root.sketches.add(XY); bc=bsk.sketchCurves.sketchCircles
ac=lambda cx,cy,r,z=0: bc.addByCenterRadius(P(cx,cy,z),r)
for c in centers: ac(c[0],c[1],LOBE_R)
for i in range(N-1): ac((centers[i][0]+centers[i+1][0])/2,(centers[i][1]+centers[i+1][1])/2,SPINE_R)
for c in centers: ac(c[0],c[1],SPINE_R)
hx=centers[0][0]-LOBE_R*0.85; hy=centers[0][1]; ac(hx,hy,HEAD_R)
tx=centers[-1][0]+dirs[-1][0]*LOBE_R*0.9; ty=centers[-1][1]+dirs[-1][1]*LOBE_R*0.9; ac(tx,ty,TAIL_R)
allp=adsk.core.ObjectCollection.create()
for k in range(bsk.profiles.count): allp.add(bsk.profiles.item(k))
ei=ex.createInput(allp,adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
ei.setDistanceExtent(False,adsk.core.ValueInput.createByReal(BODY_H))
mb=ex.add(ei).bodies.item(0); mb.name="caterpillar_18650"

# 2) ROUND BORES — 18 mm deep, vertical walls (cut down from baked z=BODY_H)
for (cx,cy) in centers:
    sk=root.sketches.add(XY); sk.sketchCurves.sketchCircles.addByCenterRadius(P(cx,cy,BODY_H),BORE_R)
    ci=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
    ci.setDistanceExtent(False,adsk.core.ValueInput.createByReal(-DEPTH))
    try: ci.participantBodies=[mb]
    except: pass
    ex.add(ci)

# 3) NIPPLE INDENT — central recess in each socket floor for the positive button
for (cx,cy) in centers:
    sk=root.sketches.add(XY); sk.sketchCurves.sketchCircles.addByCenterRadius(P(cx,cy,FLOOR_Z),NIP_R)
    ci=ex.createInput(sk.profiles.item(0),adsk.fusion.FeatureOperations.CutFeatureOperation)
    ci.setDistanceExtent(False,adsk.core.ValueInput.createByReal(-NIP_DEPTH))
    try: ci.participantBodies=[mb]
    except: pass
    ex.add(ci)

# 4) lead-in chamfer on top face edges (non-fatal)
try:
    ch=root.features.chamferFeatures; tf=None
    for f in mb.faces:
        if abs(f.boundingBox.minPoint.z-BODY_H)<1e-4 and abs(f.boundingBox.maxPoint.z-BODY_H)<1e-4: tf=f; break
    if tf:
        ecol=adsk.core.ObjectCollection.create()
        for e in tf.edges: ecol.add(e)
        ci2=ch.createInput2(); ci2.chamferEdgeSets.addEqualDistanceChamferEdgeSet(ecol,adsk.core.ValueInput.createByReal(CHAMFER),False); ch.add(ci2)
except: pass

# 5) head face — eye dimples (cut) + antenna nubs (join, share top face -> merge)
try:
    es=root.sketches.add(XY); e=es.sketchCurves.sketchCircles
    e.addByCenterRadius(P(hx-0.3,hy+0.55,BODY_H),0.16); e.addByCenterRadius(P(hx-0.3,hy-0.55,BODY_H),0.16)
    for k in range(es.profiles.count):
        di=ex.createInput(es.profiles.item(k),adsk.fusion.FeatureOperations.CutFeatureOperation)
        di.setDistanceExtent(False,adsk.core.ValueInput.createByReal(-0.12))
        try: di.participantBodies=[mb]
        except: pass
        ex.add(di)
    ns=root.sketches.add(XY); n=ns.sketchCurves.sketchCircles
    n.addByCenterRadius(P(hx-0.8,hy+0.35,BODY_H),0.09); n.addByCenterRadius(P(hx-0.8,hy-0.35,BODY_H),0.09)
    for k in range(ns.profiles.count):
        ni=ex.createInput(ns.profiles.item(k),adsk.fusion.FeatureOperations.JoinFeatureOperation)
        ni.setDistanceExtent(False,adsk.core.ValueInput.createByReal(0.35))
        ex.add(ni)
except: pass
