// Shibumi Beach Caddy — MASSING STUDY (not final geometry)
// Purpose: prove all three items pack into one printable body and visualize the
// recommended layout. Depth-stack, bottle nearest the mount. Translucent "ghosts"
// show the phone/Kindle/Yeti envelopes inside their receptacles.
//
// Coords: X = width, Y = depth (0 = chair/back, +Y = toward user/front), Z = up.

$fn = 80;

// ---- Per-person device dims (Matt reference, WM#584) ----
phone_w = 77;  phone_h = 156; phone_t = 15;   // iPhone in case (h,t are floors/bump)
kindle_w = 130; kindle_h = 176; kindle_t = 14;
bottle_d = 96;                                  // Yeti — ASSUMED diameter (flag)

// ---- Margins ----
w_clear = 4;    t_clear = 3;    bottle_clear = 6;

// interior envelopes
ph_W = phone_w + w_clear;   ph_T = phone_t + t_clear;      // 81 x 18
kn_W = kindle_w + w_clear;  kn_T = kindle_t + t_clear;     // 134 x 17
bo_D = bottle_d + bottle_clear;                            // 102 cradle ID

// ---- Structure params ----
wall = 3;
base_t = 3;
back_wall_t = 5;
spine_h = 120;      // back spine wall
slot_h = 100;       // phone/kindle slot wall height
cup_h  = 65;        // bottle cradle ring height
gap = 3;

caddy_w = kn_W + 2*wall;   // 140, Kindle governs width

// ---- Cumulative depth layout (from back/chair) ----
y_back1   = back_wall_t;                         // 5
y_bo0     = y_back1;
y_bo1     = y_bo0 + bo_D;                         // 107  (bottle cradle row)
y_kslot0  = y_bo1 + gap;                          // 110
y_kslot1  = y_kslot0 + kn_T + 2*wall;            // 133  (kindle slot row, incl walls)
y_pslot0  = y_kslot1 + gap;                       // 136
y_pslot1  = y_pslot0 + ph_T + 2*wall;            // 160  (phone slot row, incl walls)
caddy_depth = y_pslot1;                           // 160

bo_cx = 0;
bo_cy = (y_bo0 + y_bo1)/2;                        // bottle center depth

module box(w,d,h) translate([-w/2,0,0]) cube([w,d,h]);

// ---------- CADDY (opaque) ----------
color([0.80,0.75,0.62]) {
  // base tray
  translate([0,0,0]) box(caddy_w, caddy_depth, base_t);

  // back spine wall (structural; tablets lean on it; socket integrates on its back)
  translate([0,0,base_t]) box(caddy_w, back_wall_t, spine_h);

  // integrated capture-socket pad on the back face (faces chair, -Y)
  color([0.55,0.55,0.58])
    translate([0,-13,base_t+spine_h/2-20]) box(28.2, 13, 40.1);

  // bottle cradle: C-ring open toward the front (+Y), low cup
  translate([bo_cx,bo_cy,base_t])
    difference() {
      cylinder(h=cup_h, d=bo_D+2*wall);
      translate([0,0,-0.1]) cylinder(h=cup_h+0.2, d=bo_D);         // bore
      translate([-bo_D/2, 0, -0.1]) cube([bo_D, bo_D, cup_h+0.2]); // open front half
    }

  // kindle slot: two cross-width walls
  translate([0,y_kslot0,base_t])          box(kn_W+2*wall, wall, slot_h);
  translate([0,y_kslot1-wall,base_t])     box(kn_W+2*wall, wall, slot_h);

  // phone slot: two cross-width walls
  translate([0,y_pslot0,base_t])          box(ph_W+2*wall, wall, slot_h);
  translate([0,y_pslot1-wall,base_t])     box(ph_W+2*wall, wall, slot_h);
}

// ---------- ITEM GHOSTS (translucent) ----------
// bottle
color([0.30,0.55,0.95,0.35])
  translate([bo_cx,bo_cy,base_t]) cylinder(h=150, d=bottle_d);
// kindle
color([0.30,0.85,0.55,0.35])
  translate([0, y_kslot0+wall, base_t]) box(kindle_w, kindle_t, kindle_h);
// phone
color([0.95,0.55,0.30,0.35])
  translate([0, y_pslot0+wall, base_t]) box(phone_w, phone_t, phone_h);

echo(str("MASSING footprint  W=", caddy_w, "  D=", caddy_depth, "  (bed 256x256)"));
echo(str("tallest ghost = kindle ", kindle_h, "  spine_h=", spine_h));
