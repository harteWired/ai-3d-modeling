// Shibumi Mount Adapter — Phase 1: capture socket (attachment mechanism only)
//
// A slide-in CAPTURE SOCKET. A flat cleat blade (27.6 wide x 4.02 thick, reference
// only — NOT modeled) enters the OPEN mouth end (-Y) and slides in LENGTHWISE (+Y).
// The two long side-wall tops curl inward into LIPS that trap the blade's back face;
// two thin floor RAILS set the blade's seating height; a closed ARCH BRIDGE caps the
// far (+Y) end. Decorative sewing terraces + flange of the original are DROPPED.
//
// Coordinate system:
//   origin = socket FLOOR center
//   +Z up  = socket opens upward (cleat back captured under lips)
//   +Y     = long axis; -Y = OPEN MOUTH (cleat enters here), +Y = closed arch bridge
//   +X     = short axis
//
// v1 = FAITHFUL NOMINAL reproduction — NO internal taper (that is a later fit round).
// The inward lips are an undercut/overhang: see printability note in modeling report.

include <fdm-pla.scad>
include <bambu-x1c.scad>
include <common.scad>

// ============================================================================
// Render quality (draft during iteration; shipper bumps via -D)
// ============================================================================
$fn         = 100;   // draft; shipper bumps to 200 via -D
corner_pts  = 32;    // arc points on rounded corners; ship ~96 via -D

// ============================================================================
// PARAMETERS — every dimension is a top-level variable
// ============================================================================

// --- Backing plate (below the socket floor) ---
backing_x         = 28.2;   // short axis
backing_y         = 40.1;   // long axis
backing_thickness = 2.5;    // z below floor
backing_corner_r  = 3.0;    // rounded corners of the plate

// --- Outer socket footprint + walls ---
socket_outer_x    = 28.2;   // short axis, outer
socket_outer_y    = 40.1;   // long axis, outer
wall_base_thick   = 3.5;    // side-wall thickness at the base
standoff_height   = 10.0;   // floor (z=0) -> wall top
outer_corner_r    = 3.0;    // rounded outer corners of the socket body

// --- Inner cavity (open toward +Z) ---
cavity_x          = 21.2;   // short axis, inner (floor width)
cavity_y          = 33.0;   // long axis, inner (floor length)
cavity_corner_r   = 2.0;    // rounded inner corners

// --- Capture lips (top of the two LONG walls + the far arch end) ---
lip_overhang      = 2.1;    // inward overhang, per side (photo 10 = 2.12, measured)
lip_zone_height   = 3.0;    // lips occupy the TOP 3 mm of the walls
// => socket depth under the lip = standoff_height - lip_zone_height = 7.0

// --- Arch bridge (far +Y end) ---
arch_wall_thick   = 3.5;    // end-wall thickness at base (same as side walls)

// --- Variant label (shallow deboss on the flat backing outer face) ---
label        = "";     // e.g. "1"/"2"/"3" for fit-test variants; "" = none
label_size   = 13;     // mm cap height
label_depth  = 0.8;    // deboss depth into the backing

// --- Inverted-U floor tongue (two rails + rounded bridge at far end) ---
rail_width        = 2.15;   // each rail, in X
rail_height       = 3.0;    // above floor
rail_offset       = 4.5;    // gap from inner side wall to near edge of rail
central_slot      = 8.2;    // gap between the two rails
rail_corner_r     = 0.6;    // slight rounding on rail top edges (cosmetic)

// ============================================================================
// DERIVED
// ============================================================================
socket_depth      = standoff_height - lip_zone_height;   // 7.0, floor -> lip underside
lip_bottom_z      = socket_depth;                        // where the overhang starts
lip_top_z         = standoff_height;                     // wall top

// Rail center X positions (symmetric about X=0).
// From wall: inner cavity edge at cavity_x/2; rail near edge at cavity_x/2 - rail_offset.
rail_inner_x      = central_slot/2;                      // near edge (toward center)
rail_outer_x      = central_slot/2 + rail_width;         // far edge (toward wall)
rail_center_x     = (rail_inner_x + rail_outer_x) / 2;

// Rail run in Y: from mouth-side (rails do NOT reach the mouth) to far bridge.
// Anchor the inverted-U bridge at the far (+Y) cavity end; rails run back toward
// the mouth but stop short of it.
rail_y_far        = cavity_y/2;                          // far end (bridge, +Y)
rail_bridge_depth = rail_width + 2;                      // rounded bridge span in Y
rail_y_near       = -cavity_y/2 + 3;                     // near end (stops short of mouth)

// Total bbox
total_z           = backing_thickness + standoff_height;

// ============================================================================
// ASSERTIONS
// ============================================================================
assert(wall_base_thick >= MIN_WALL, str("Wall ", wall_base_thick, " < MIN_WALL ", MIN_WALL));
assert(wall_base_thick - lip_overhang >= 0.8,
    str("Lip residual wall ", wall_base_thick - lip_overhang, " too thin"));
assert(socket_depth > 0, "socket_depth must be positive");
assert(cavity_x + 2*wall_base_thick <= socket_outer_x + 0.01,
    str("cavity+walls ", cavity_x + 2*wall_base_thick, " != outer ", socket_outer_x));

// ============================================================================
// HELPERS
// ============================================================================

// A rounded rectangular prism centered in X/Y, base at z=0.
module rrect_prism(sx, sy, sz, r, fn=corner_pts) {
    linear_extrude(height=sz)
        offset(r=r) offset(r=-r)
            square([sx, sy], center=true);
}

// True rounded rect via minkowski-free offset on a square (cleaner corners).
module rrect(sx, sy, r, fn=corner_pts) {
    offset(r=r, $fn=fn) offset(r=-r, $fn=fn)
        square([sx, sy], center=true);
}

// ============================================================================
// SOCKET BODY (walls) — subtract cavity, then form lips
// ============================================================================

module socket_walls() {
    difference() {
        // Outer block, floor at z=0, top at standoff_height.
        linear_extrude(height=standoff_height)
            rrect(socket_outer_x, socket_outer_y, outer_corner_r);

        // --- Main cavity (full depth, straight walls up to the top) ---
        // Cut a through cavity from the floor up past the top so we can re-add lips.
        translate([0, 0, -0.01])
            linear_extrude(height=standoff_height + 0.02)
                rrect(cavity_x, cavity_y, cavity_corner_r);
    }
}

// The mouth must be fully open: cavity extends out through the -Y face.
// We build the wall body and cavity so the -Y end has NO wall and NO lip.
module socket_body() {
    difference() {
        socket_walls();
        // Extend the cavity opening out through the mouth face so no end wall
        // remains at -Y (lengthwise entry). Slightly over-wide to clear corners.
        translate([0, -socket_outer_y/2 - 0.02, -0.01])
            linear_extrude(height=standoff_height + 0.02)
                translate([-cavity_x/2, 0])
                    square([cavity_x, socket_outer_y/2 - cavity_y/2 + 0.03]);
    }
}

// ============================================================================
// CAPTURE LIPS
// The cavity above lip_bottom_z narrows by lip_overhang on each LONG side and
// on the FAR (+Y) arch end, but NOT on the mouth (-Y) side. We modeled the
// cavity full-width above; now ADD material back in the lip zone to form the
// inward overhang. Simpler: model lips as added inner ledges.
// ============================================================================

module capture_lips() {
    // Lip zone spans lip_bottom_z .. lip_top_z.
    // The lip is a ring that hugs the cavity but is inset by lip_overhang on the
    // two long sides and the far end. On the mouth side it is flush with the
    // cavity (no lip) so the opening stays clear.

    // The lip is a continuous inside border (a picture frame missing its mouth rail):
    // it runs down BOTH long walls straight to the mouth edge and wraps the far arch
    // end, and is OPEN at the -Y mouth. Built as (cavity outline) minus (an inset
    // outline whose mouth side is opened out past the cavity), so the two long-wall
    // lips terminate flush and straight at the mouth — no pinched/pointy remnant.
    inner_w = cavity_x - 2*lip_overhang;   // narrowed opening between the long-wall lips
    inner_l = cavity_y - 2*lip_overhang;   // inset that leaves the rounded far-end lip

    translate([0, 0, lip_bottom_z])
        linear_extrude(height=lip_zone_height + 0.01)
            difference() {
                // outer bound = the wall inner face (cavity outline, rounded)
                rrect(cavity_x, cavity_y, cavity_corner_r);
                union() {
                    // inset void — rounded corners give the far-end lip clean fillets
                    rrect(inner_w, inner_l, cavity_corner_r);
                    // open the mouth (-Y): a straight channel from the mouth edge inward,
                    // so the long-wall lips run contiguous & straight to the mouth (no band)
                    translate([-inner_w/2, -cavity_y/2 - 1])
                        square([inner_w, cavity_y/2 + 1]);
                }
            }
}

// ============================================================================
// FLOOR RAILS — inverted-U tongue (two rails + rounded far bridge)
// ============================================================================

module floor_rails() {
    // Two straight rails running in Y, plus a rounded bridge joining them at +Y.
    rail_len_y = rail_y_far - rail_y_near;
    rail_mid_y = (rail_y_far + rail_y_near) / 2;

    translate([0, 0, 0])
    linear_extrude(height=rail_height)
        offset(r=rail_corner_r, $fn=16) offset(r=-rail_corner_r, $fn=16)
        union() {
            // left rail
            translate([-rail_center_x, rail_mid_y])
                square([rail_width, rail_len_y], center=true);
            // right rail
            translate([ rail_center_x, rail_mid_y])
                square([rail_width, rail_len_y], center=true);
            // rounded bridge at far (+Y) end joining the two rails (closed U)
            translate([0, rail_y_far - rail_bridge_depth/2])
                square([2*rail_center_x + rail_width, rail_bridge_depth], center=true);
        }
}

// ============================================================================
// BACKING PLATE
// ============================================================================

module backing_plate() {
    translate([0, 0, -backing_thickness])
        linear_extrude(height=backing_thickness)
            rrect(backing_x, backing_y, backing_corner_r);
}

// ============================================================================
// ASSEMBLY — single manifold solid
// ============================================================================

// Shallow debossed numeral on the flat backing OUTER face (-Z), mirrored so it
// reads correctly when the backing is viewed face-on.
module label_cut() {
    if (label != "")
        translate([0, 0, -backing_thickness - 0.01])
            linear_extrude(height = label_depth + 0.01)
                mirror([1, 0, 0])
                    text(label, size = label_size, halign = "center", valign = "center",
                         font = "Liberation Sans:style=Bold", $fn = 32);
}

module shibumi_mount() {
    difference() {
        union() {
            backing_plate();
            socket_body();
            capture_lips();
            floor_rails();
        }
        label_cut();
    }
}

shibumi_mount();

// ============================================================================
// DIMENSION REPORT
// ============================================================================
report_dimensions(
    max(backing_x, socket_outer_x),
    max(backing_y, socket_outer_y),
    total_z,
    "shibumi-mount-adapter"
);
