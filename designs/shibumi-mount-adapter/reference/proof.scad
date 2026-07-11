// Proof renders — cut sections through the actual STL to expose internal geometry.
// mode 0 = full, 1 = short-axis section (through the rails), 2 = long-axis section
mode = 0;
BIG = 300;
stl = "../output/shibumi-mount-adapter.stl";

intersection() {
    import(stl);
    if (mode == 1)                       // cut at Y=2, keep the mouth (-Y) half
        translate([-BIG/2, -BIG, -BIG/2]) cube([BIG, BIG + 2, BIG]);
    else if (mode == 2)                  // cut at X=0, keep -X half
        translate([-BIG, -BIG/2, -BIG/2]) cube([BIG, BIG, BIG]);
    else                                 // full
        translate([-BIG/2, -BIG/2, -BIG/2]) cube(BIG);
}
