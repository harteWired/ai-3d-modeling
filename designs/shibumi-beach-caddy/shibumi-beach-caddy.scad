// Shibumi Beach Caddy — Phase 2 unibody body (v3 DRAFT, rugged-cantilever pass)
//
// One caddy holding phone + Kindle + Yeti, mounted to the beach chair via the
// Phase-1 capture socket (integrated = unibody, no separable coupling).
// Depth-stack layout, bottle nearest the mount (heaviest item, shortest lever arm).
//
// v3 rugged-cantilever pass (WM#1104, Matt): engineer the cleat-mount + gussets to
// carry the FULL cantilever load standalone — NO reliance on backing against the chair
// leg (cleat protrudes awkwardly + the leg fit is a hard-to-capture 3D skew). Added:
//   * external SIDE BUTTRESS GUSSETS — long triangular brackets down each side, tall at
//     the root (mount junction) tapering to the front, running along the load path.
//   * BACK-CORNER HAUNCHES tying the base plate into the spine in the dead corners
//     outboard of the bottle (distributes the peak-moment junction into shear/compression).
//   * thicker base plate + spine (deeper cantilever section at the root).
// PRINT ORIENTATION: base-down (as-used). The peak tensile fiber (top of the section at
// the root) then runs fore-aft = IN-PLANE with the horizontal layers, not across them;
// the gussets/haunches carry shear in-plane; the base↔spine weld is loaded in
// compression/shear, not interlayer peel. (Matt's layer-plane concern, addressed.)
//
// v2 robustness pass (WM, 2026-07-25): thicker bottle-cradle wall, slots back-tilted
// for retention, top edges chamfered / lead-in funnels for insertion.
// STILL DRAFT: MOUNT is a parametric placeholder (mount_tbd). Device HOLD HEIGHTS
// (how much of each device protrudes) are Matt's ergonomic call — current heights are
// placeholders. An OPTIONAL chair-leg brace can be added later IF Matt supplies the
// leg-skew dims — but the PRIMARY target here is standalone cantilever ruggedness.
//
// Coords: X = width, Y = depth (0 = chair/back, +Y = toward user), Z = up.
// Per-person: change the DEVICE block only (Matt now; Hana = swap the numbers).

include <fdm-pla.scad>
include <bambu-x1c.scad>
include <common.scad>

$fn = 72;   // draft; bump via -D for ship renders

// ============================================================================
// DEVICE DIMENSIONS (per person) — Matt reference (WM#584); Yeti Ø confirmed WM#592
// ============================================================================
phone_w  = 77;   phone_t  = 15;    // iPhone in case (t incl camera bump)
kindle_w = 130;  kindle_t = 14;
bottle_d = 96;                      // Yeti diameter (CONFIRMED)

// ============================================================================
// CLEARANCES + WALLS
// ============================================================================
w_clear      = 4;    // total width clearance (2/side) for slot items
t_clear      = 3;    // total thickness clearance for slot items
bottle_clear = 6;    // diameter clearance for the bottle cradle

wall        = 3.0;   // slot wall
cradle_wall = 4.5;   // bottle cradle wall — THICKER for the full-bottle load (v2)
base_t      = 5.5;   // floor thickness — deeper platform for the cantilever (v3, was 4.0)
spine_t     = 8.0;   // back structural spine — thicker root (v3, was 6.0)
gap         = 2.0;   // gap between receptacles

slot_tilt   = 5;     // deg — slots lean back toward the spine for retention (v2)
chamfer     = 1.4;   // top edge break / insertion lead-in (v2)

// interior envelopes
ph_W = phone_w  + w_clear;    ph_T = phone_t  + t_clear;    // 81 x 18
kn_W = kindle_w + w_clear;    kn_T = kindle_t + t_clear;    // 134 x 17
bo_ID = bottle_d + bottle_clear;                            // 102
bo_OD = bo_ID + 2*cradle_wall;                              // 111

// receptacle heights (HOLD — Matt's protrusion call; placeholders)
spine_h = 110;
bo_h    = 88;    // bottle cradle ring height
kn_h    = 100;   // kindle channel height
ph_h    = 92;    // phone channel height

caddy_w = kn_W + 2*wall;                                    // 140 (Kindle governs)

// ============================================================================
// DEPTH LAYOUT (cumulative from the back / chair side)
// ============================================================================
y_spine1 = spine_t;
bo_cy    = y_spine1 + bo_OD/2;
y_bo1    = y_spine1 + bo_OD;
y_k0     = y_bo1 + gap;
y_k1     = y_k0 + kn_T + 2*wall;
y_p0     = y_k1 + gap;
y_p1     = y_p0 + ph_T + 2*wall;
caddy_depth = y_p1;

// ============================================================================
// CANTILEVER GUSSETS (v3) — run along the load path (fore-aft), deepest at the root
// ============================================================================
gusset_t   = 6.0;              // side buttress gusset thickness (one per side, external)
                              // v3.1: 4.5 -> 6.0 to drop the mid-span fin's height:thickness
                              // ratio from ~15:1 to ~11:1 (print-reviewer flag — freestanding
                              // fin warp/ringing risk in PETG/ASA). Structurally still a bonus
                              // (strain SF=208 already treats the gussets as disconnected).
gusset_h   = 74;              // gusset height at the root (back / mount junction)
gusset_len = caddy_depth;     // runs the full depth, tapering to the base at the front
haunch     = 20;              // back-corner base<->spine haunch leg (fillets the junction)

// ============================================================================
// MOUNT PLACEHOLDER (parametric TBD)
// ============================================================================
mount_tbd  = true;
mount_w    = 28.2;   mount_h = 40.1;   mount_proj = 13;
mount_z0   = base_t + 25;   // vertical placement TBD (chair-dependent) — flagged

// ============================================================================
// ASSERTIONS
// ============================================================================
assert(wall >= 0.8 && cradle_wall >= 0.8, "wall too thin");
assert(caddy_w + 2*gusset_t <= 256 && caddy_depth <= 256, "exceeds X1C bed");

// ============================================================================
// HELPERS
// ============================================================================
module box(w, d, h) translate([-w/2, 0, 0]) cube([w, d, h]);

// Open-top slot channel, back-tilted by `tilt` deg for retention. Built plunged
// below z=0 and flattened by the global z<0 trim so the print bottom is flat and
// the channel stays anchored to the base plate.
module channel(inner_w, inner_t, y_back, h, tilt) {
    outer_w = inner_w + 2*wall;
    outer_d = inner_t + 2*wall;
    plunge  = 22;
    translate([0, y_back, 0]) rotate([tilt, 0, 0])
        difference() {
            translate([0, 0, -plunge]) box(outer_w, outer_d, h + plunge);
            // straight slot void (floor kept at base_t), exits the top
            translate([0, wall, base_t]) box(inner_w, inner_t, h + plunge);
            // insertion lead-in funnel at the opening
            hull() {
                translate([0, wall, h - chamfer]) box(inner_w, inner_t, 0.01);
                translate([0, wall - chamfer, h + 3])
                    box(inner_w + 2*chamfer, inner_t + 2*chamfer, 0.01);
            }
            // floor drain slots
            for (dx = [-inner_w/4, inner_w/4])
                translate([dx, outer_d/2, -plunge - 1])
                    cylinder(h = base_t + plunge + 2, d = 6);
        }
}

// ============================================================================
// BODY PARTS
// ============================================================================
module base_plate() {
    difference() {
        box(caddy_w, caddy_depth, base_t);
        translate([0, bo_cy, -1]) cylinder(h = base_t + 2, d = 40);  // bottle drain
    }
}

module back_spine() {
    difference() {
        box(caddy_w, spine_t, spine_h);
        // chamfer the top two long edges of the spine
        for (yy = [0, spine_t])
            translate([-caddy_w/2 - 1, yy, spine_h])
                rotate([45, 0, 0])
                    cube([caddy_w + 2, chamfer*1.6, chamfer*1.6]);
    }
}

module bottle_cradle() {
    difference() {
        translate([0, bo_cy, 0])
            difference() {
                cylinder(h = bo_h, d = bo_OD);
                translate([0, 0, base_t]) cylinder(h = bo_h, d = bo_ID);   // bore
                // rim lead-in chamfer (eases bottle drop-in)
                translate([0, 0, bo_h - chamfer])
                    cylinder(h = chamfer + 1, d1 = bo_ID, d2 = bo_ID + 2*chamfer);
            }
        // open the FRONT (+Y) into a C for grab + drainage
        translate([0, bo_cy + bo_ID*0.18, base_t + 6]) box(bo_ID*0.78, bo_OD, bo_h);
        translate([0, bo_cy, -1]) cylinder(h = base_t + 2, d = 30);   // cup drain
    }
}

module mount_placeholder() {
    if (mount_tbd)
        color("gray")
        translate([0, -mount_proj, mount_z0]) box(mount_w, mount_proj + 1.5, mount_h);
}

// Long triangular side buttress: right triangle in the Y-Z plane (tall at the back /
// root, tapering to the base at the front), extruded `gt` thick in X. Prints base-down
// as a vertical fin → layers carry the load in-plane shear, not interlayer tension.
module side_gusset(x, gt) {
    translate([x, 0, 0])
        rotate([90, 0, 90])
            linear_extrude(gt)
                polygon([[0, 0], [gusset_len, 0], [0, gusset_h]]);
}

// Solid corner haunches that fillet the base<->spine junction in the two dead corners
// outboard of the bottle ring — converts the peak-moment junction into distributed
// compression/shear. Right triangle ramps from the base up the spine face.
module back_haunches() {
    x_in  = bo_OD/2 + 1;
    x_out = caddy_w/2;
    if (x_out - x_in > 1)
        for (sx = [-1, 1])
            translate([sx < 0 ? -x_out : x_in, 0, 0])
                rotate([90, 0, 90])
                    linear_extrude(x_out - x_in)
                        polygon([[0, 0], [haunch, 0], [0, haunch]]);
}

// ============================================================================
// ASSEMBLY  (global z<0 trim → flat printable bottom)
// ============================================================================
module caddy() {
    difference() {
        union() {
            base_plate();
            back_spine();
            bottle_cradle();
            channel(kn_W, kn_T, y_k0, kn_h, slot_tilt);   // kindle
            channel(ph_W, ph_T, y_p0, ph_h, slot_tilt);   // phone
            back_haunches();                              // v3 junction fillets
            side_gusset(-caddy_w/2 - gusset_t, gusset_t); // v3 left buttress
            side_gusset( caddy_w/2,            gusset_t); // v3 right buttress
            mount_placeholder();
        }
        translate([0, caddy_depth/2, -500]) cube([1000, 2000, 1000], center=true);
    }
}

caddy();

// ============================================================================
// DIMENSION REPORT
// ============================================================================
report_dimensions(caddy_w + 2*gusset_t, caddy_depth, max(spine_h, bo_h, kn_h, ph_h) + base_t,
                  "shibumi-beach-caddy");
echo(str("v3: gusset_h=", gusset_h, " gusset_t=", gusset_t, " haunch=", haunch,
         " base_t=", base_t, " spine_t=", spine_t,
         " | footprint W=", caddy_w + 2*gusset_t, " D=", caddy_depth));
