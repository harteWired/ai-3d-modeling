#!/usr/bin/env python3
"""Dimensioned reference drawing of the Shibumi mount capture-socket (as-understood).
Three panels: short-axis section, long-axis section, top-down plan. Units = mm."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, PathPatch
from matplotlib.path import Path

GREY = "#c9ccd1"
GREY_E = "#7c8085"
CLEAT = "#3a6ea5"
DIM = "#c0392b"

def dim(ax, x1, y1, x2, y2, text, off=0, tside="mid", fs=9):
    """simple dimension line with ticks + centered label"""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="<->", color=DIM, lw=1.1))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx, my + off, text, color=DIM, fontsize=fs, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))

def wall_with_lip(ax, x_out, direction, floor=0.0, wall_t=3.5, h=10.0, lip=2.0, lip_h=3.0):
    """draw one side wall as a filled polygon with an inward-curling lip at the top.
       direction=+1 wall on the left (lip points +x), -1 wall on the right."""
    xi = x_out + direction * wall_t          # inner face x
    xl = xi + direction * lip                 # lip inner edge (curls toward cavity)
    verts = [
        (x_out, floor), (x_out, floor + h),   # outer face up
        (xl, floor + h),                       # across the top (lip tip)
        (xl, floor + h - lip_h),               # down the lip inner face
        (xi, floor + h - lip_h),               # back out to main inner face (undercut ledge)
        (xi, floor),                           # main inner face down to floor
    ]
    ax.add_patch(plt.Polygon(verts, closed=True, fc=GREY, ec=GREY_E, lw=1.3))

fig = plt.figure(figsize=(9.2, 12.4), dpi=130)
fig.suptitle("Shibumi mount — capture socket (as-understood, 2026-07-11)\n"
             "measured = black, estimated = red-italic; cleat = blue (reference)",
             fontsize=12, y=0.985)

# ---------------- Panel A: SHORT-AXIS SECTION ----------------
axA = fig.add_axes([0.08, 0.68, 0.86, 0.25]); axA.set_aspect("equal"); axA.axis("off")
axA.set_title("A · SHORT-AXIS SECTION (across the 28.2 width)", fontsize=11, loc="left")
OW, IW, WT, H, LIP, LIPH = 28.2, 21.2, 3.5, 10.0, 2.0, 3.0
BACK = 2.5
# backing plate
axA.add_patch(Rectangle((0, -BACK), OW, BACK, fc=GREY, ec=GREY_E, lw=1.3))
# walls + lips
wall_with_lip(axA, 0, +1, 0, WT, H, LIP, LIPH)
wall_with_lip(axA, OW, -1, 0, WT, H, LIP, LIPH)
# two thin low rails (measured: rail 2.15 wide, 4.5 from wall, 8.2 slot between)
rw, slot, wallgap = 2.15, 8.2, 4.5
cx = OW / 2
rails_x = [WT + wallgap, OW - WT - wallgap - rw]
for rx in rails_x:
    axA.add_patch(Rectangle((rx, 0), rw, 3.0, fc=GREY, ec=GREY_E, lw=1.2))
# cleat blade (dashed, sitting in cavity, tucked under lips)
axA.add_patch(Rectangle((WT-LIP-0.3, 3.0), IW+2*LIP+0.6, 3.2, fc=CLEAT, ec="#22456a",
                        lw=1.0, alpha=0.30, ls="--"))
axA.text(cx, 4.6, "cleat blade\n(tucks under lips)", fontsize=7.5, ha="center", va="center",
         color="#22456a")
# dims
dim(axA, 0, 13.0, OW, 13.0, "28.2  outer", off=0.9)
dim(axA, WT, -4.6, OW-WT, -4.6, "21.2  inner cavity", off=-0.9)
dim(axA, 0, -1.2, WT, -1.2, "3.5", off=-1.0, fs=8)
dim(axA, OW+1.6, 0, OW+1.6, H, "10  standoff", off=0); axA.text(OW+2.2, H/2, "", )
dim(axA, -1.6, 0, -1.6, H-LIPH, "7  socket\ndepth", off=0)
dim(axA, WT, -2.0, rails_x[0], -2.0, "4.5", off=-0.9, fs=7.5)
dim(axA, rails_x[0], -2.0, rails_x[0]+rw, -2.0, "2.15", off=-2.0, fs=7)
dim(axA, rails_x[0]+rw, -2.0, rails_x[1], -2.0, "8.2  slot", off=-0.9, fs=8)
dim(axA, rails_x[1]+rw+0.2, 3.0, rails_x[1]+rw+0.2, 0, "~3 rail h", off=0, fs=7.5)
axA.annotate("~2 lip\noverhang", xy=(WT+LIP, H-1.2), xytext=(WT+5.5, H+2.2),
             fontsize=7.5, color=DIM, ha="center",
             arrowprops=dict(arrowstyle="->", color=DIM, lw=0.9))
axA.set_xlim(-7, OW+9); axA.set_ylim(-7.5, 16)

# ---------------- Panel B: LONG-AXIS SECTION ----------------
axB = fig.add_axes([0.08, 0.37, 0.86, 0.25]); axB.set_aspect("equal"); axB.axis("off")
axB.set_title("B · LONG-AXIS SECTION (along the 40.1 length; cut through a rail)", fontsize=11, loc="left")
OL, IL = 40.1, 33.0
# backing
axB.add_patch(Rectangle((0, -BACK), OL, BACK, fc=GREY, ec=GREY_E, lw=1.3))
# far-end arch wall (right) with inward lip
wall_with_lip(axB, OL, -1, 0, WT, H, LIP, LIPH)
# arch bridge crown (rounded) over the far end
crown = Path([(OL-WT-2, H-LIPH), (OL-WT-2, H+1.6), (OL, H+1.6), (OL, H-LIPH)],
             [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.LINETO])
# low threshold at open mouth (left) - short stub
axB.add_patch(Rectangle((0, 0), 2.0, 2.2, fc=GREY, ec=GREY_E, lw=1.1))
# rail running the length
axB.add_patch(Rectangle((3.5, 0), IL-3.5, 3.0, fc=GREY, ec=GREY_E, lw=1.2))
# cleat sliding in (dashed arrow + blade)
axB.add_patch(Rectangle((3.0, 3.2), 27.6, 3.0, fc=CLEAT, ec="#22456a", lw=1.0, alpha=0.30, ls="--"))
axB.annotate("", xy=(30.5, 7.6), xytext=(6, 7.6),
             arrowprops=dict(arrowstyle="->", color="#22456a", lw=1.4))
axB.text(16, 8.6, "cleat (27.6 wide) slides in end-on", fontsize=8, ha="center", color="#22456a")
axB.text(1.0, -3.6, "OPEN\nMOUTH", fontsize=8, ha="center", color="#333")
axB.text(OL-2, H+3.0, "ARCH\nBRIDGE\n(closed)", fontsize=8, ha="center", color="#333")
# dims
dim(axB, 0, 13.0, OL, 13.0, "40.1  loop outer length", off=0.9)
dim(axB, 3.5, -4.6, IL, -4.6, "33  inner cavity length", off=-0.9)
axB.set_xlim(-4, OL+6); axB.set_ylim(-7.5, 16)

# ---------------- Panel C: PLAN VIEW ----------------
axC = fig.add_axes([0.08, 0.045, 0.86, 0.27]); axC.set_aspect("equal"); axC.axis("off")
axC.set_title("C · TOP-DOWN PLAN (looking into the socket)", fontsize=11, loc="left")
# outer loop (rounded rect) via FancyBbox-ish: use Rectangle rounded
from matplotlib.patches import FancyBboxPatch
axC.add_patch(FancyBboxPatch((0, 0), OW, OL, boxstyle="round,pad=0,rounding_size=3.5",
                             fc=GREY, ec=GREY_E, lw=1.4))
# cavity (open through the walls) — white rounded rect
axC.add_patch(FancyBboxPatch((WT, WT), OW-2*WT, OL-2*WT, boxstyle="round,pad=0,rounding_size=2",
                             fc="white", ec=GREY_E, lw=1.1))
# arch (closed far end) — fill the top band grey again
axC.add_patch(Rectangle((WT, OL-WT-3.0), OW-2*WT, 3.0, fc=GREY, ec=GREY_E, lw=0.8))
axC.text(cx, OL-WT-1.5, "arch bridge", fontsize=7, ha="center", va="center", color="#333")
# mouth (open near end) — dashed to show opening
axC.plot([WT, OW-WT], [WT, WT], color="#22456a", lw=1.2, ls="--")
axC.text(cx, WT-1.6, "open mouth", fontsize=7, ha="center", va="center", color="#22456a")
# two thin rails running lengthwise (2.15 wide, 4.5 from each wall)
for rx in rails_x:
    axC.add_patch(Rectangle((rx, WT+1.5), rw, OL-2*WT-6, fc=GREY, ec=GREY_E, lw=1.0))
axC.text(cx, OL/2, "8.2\nslot", fontsize=7, ha="center", va="center", color="#555")
# cleat sliding in
axC.add_patch(Rectangle((cx-27.6/2, -6), 27.6, 10, fc=CLEAT, ec="#22456a", lw=1.0, alpha=0.28, ls="--"))
axC.annotate("", xy=(cx, 6), xytext=(cx, -7.5),
             arrowprops=dict(arrowstyle="->", color="#22456a", lw=1.5))
axC.text(cx+18, -3, "cleat 27.6 wide\nslides in", fontsize=8, ha="center", color="#22456a")
# dims
dim(axC, -2.2, 0, -2.2, OL, "40.1", off=0)
dim(axC, 0, OL+2.2, OW, OL+2.2, "28.2", off=0.8)
axC.set_xlim(-8, OW+22); axC.set_ylim(-9, OL+6)

# Was hardcoded to /workspace/projects/... — a Jinn-container path absent on this host, so this
# script could not write anywhere. Self-locating, with an env override used to prove the script
# without clobbering the existing (untracked, single-copy) socket-diagram.png. 2026-09-06.
# NB: `Path` here is matplotlib.path.Path (imported above), NOT pathlib — use os.path.
out = os.environ.get("SOCKET_DIAGRAM_OUT") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "socket-diagram.png"
)
fig.savefig(out, dpi=130, bbox_inches="tight", facecolor="white")
print("wrote", out)
