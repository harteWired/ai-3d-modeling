// Shibumi Beach Caddy — Phase 2 unibody body (v1 DRAFT)
//
// One caddy holding phone + Kindle + Yeti, mounted to the beach chair via the
// Phase-1 capture socket (integrated = unibody, no separable coupling).
// Depth-stack layout, bottle nearest the mount (heaviest item, shortest lever arm).
//
// DRAFT scope: the caddy BODY is real/parametric. The MOUNT is a parametric
// PLACEHOLDER (mount_tbd) pending (a) chair load-path decision and (b) the Phase-1
// A/B/C fit-test that sets the socket rail_height. See ARCHITECTURE.md.
//
// Coords: X = width, Y = depth (0 = chair/back, +Y = toward user), Z = up.
// Per-person: change the DEVICE block only (Matt now; Hana = swap the numbers).

include <fdm-pla.scad>
include <bambu-x1c.scad>
include <common.scad>

$fn = 64;   // draft; bump to 128 via -D for ship renders

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

wall    = 3.0;       // slot / cradle wall
base_t  = 4.0;       // floor thickness
spine_t = 6.0;       // back structural spine (thicker)
gap     = 2.0;       // gap between receptacles

// interior envelopes
ph_W = phone_w  + w_clear;    ph_T = phone_t  + t_clear;    // 81 x 18
kn_W = kindle_w + w_clear;    kn_T = kindle_t + t_clear;    // 134 x 17
bo_ID = bottle_d + bottle_clear;                            // 102
bo_OD = bo_ID + 2*wall;                                     // 108

// receptacle heights
spine_h = 110;
bo_h    = 88;    // bottle cradle ring height
kn_h    = 100;   // kindle channel height
ph_h    = 92;    // phone channel height

caddy_w = kn_W + 2*wall;                                    // 140 (Kindle governs)

// ============================================================================
// DEPTH LAYOUT (cumulative from the back / chair side)
// ============================================================================
y_spine1 = spine_t;                       // 6
bo_cy    = y_spine1 + bo_OD/2;            // 60   bottle center
y_bo1    = y_spine1 + bo_OD;              // 114
y_k0     = y_bo1 + gap;                   // 116  kindle channel outer-back
y_k1     = y_k0 + kn_T + 2*wall;         // 139
y_p0     = y_k1 + gap;                    // 141  phone channel outer-back
y_p1     = y_p0 + ph_T + 2*wall;         // 165
caddy_depth = y_p1;                       // 165

// ============================================================================
// MOUNT PLACEHOLDER (parametric TBD) — integrated capture socket on the spine back
// ============================================================================
mount_tbd     = true;    // draft placeholder until chair load-path + A/B/C known
mount_w       = 28.2;    // = Phase-1 socket backing X
mount_h       = 40.1;    // = Phase-1 socket backing Y (runs vertical here)
mount_proj    = 13;      // -Y projection (socket depth zone, placeholder)
mount_z0      = base_t + 25;   // vertical placement TBD (depends on chair) — flagged

// ============================================================================
// ASSERTIONS
// ============================================================================
assert(wall >= 0.8, "wall too thin");
assert(caddy_w <= 256 && caddy_depth <= 256, "exceeds X1C bed");

// ============================================================================
// HELPERS
// ============================================================================
module box(w, d, h) translate([-w/2, 0, 0]) cube([w, d, h]);

// open-top rectangular channel: outer tube minus inner void (void breaks the top)
module channel(inner_w, inner_t, y_back, h) {
    outer_w = inner_w + 2*wall;
    outer_d = inner_t + 2*wall;
    difference() {
        translate([0, y_back, 0]) box(outer_w, outer_d, h);
        // inner void, open at the top (extends above h)
        translate([0, y_back + wall, base_t]) box(inner_w, inner_t, h);
        // drain slots in the channel floor
        for (dx = [-inner_w/4, inner_w/4])
            translate([dx, y_back + outer_d/2, -1])
                cylinder(h = base_t + 2, d = 6);
    }
}

// ============================================================================
// BODY
// ============================================================================
module base_plate() {
    difference() {
        box(caddy_w, caddy_depth, base_t);
        // bottle drain hole (big, centered under the cradle)
        translate([0, bo_cy, -1]) cylinder(h = base_t + 2, d = 40);
    }
}

module back_spine() {
    box(caddy_w, spine_t, spine_h);
}

module bottle_cradle() {
    difference() {
        // ring
        translate([0, bo_cy, 0])
            difference() {
                cylinder(h = bo_h, d = bo_OD);
                translate([0, 0, base_t])
                    cylinder(h = bo_h, d = bo_ID);   // bore (keeps a cup floor)
            }
        // open the FRONT (+Y) into a C for grab + drainage
        translate([0, bo_cy + bo_ID*0.18, base_t + 6])
            box(bo_ID*0.78, bo_OD, bo_h);
        // cup floor drain
        translate([0, bo_cy, -1]) cylinder(h = base_t + 2, d = 30);
    }
}

module mount_placeholder() {
    if (mount_tbd)
        color("gray")
        translate([0, -mount_proj, mount_z0])
            box(mount_w, mount_proj + 1.5, mount_h);  // +1.5 overlaps spine (manifold-safe)
}

module caddy() {
    union() {
        base_plate();
        back_spine();
        bottle_cradle();
        channel(kn_W, kn_T, y_k0, kn_h);   // kindle
        channel(ph_W, ph_T, y_p0, ph_h);   // phone
        mount_placeholder();
    }
}

caddy();

// ============================================================================
// DIMENSION REPORT
// ============================================================================
report_dimensions(caddy_w, caddy_depth, max(spine_h, bo_h, kn_h, ph_h) + base_t,
                  "shibumi-beach-caddy");
echo(str("footprint W=", caddy_w, " D=", caddy_depth,
         "  | receptacles: bottle@y", bo_cy, " kindle@y", y_k0+wall, " phone@y", y_p0+wall));
