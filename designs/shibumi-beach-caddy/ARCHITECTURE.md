# Shibumi Beach Caddy — Architecture (Phase 2)

> Status: **v1 DRAFT BODY built + validated** (2026-07-25, WM#592). Yeti Ø96 = diameter
> CONFIRMED; unibody + depth-stack GREEN. The caddy body is now real parametric geometry
> (`shibumi-beach-caddy.scad`) — watertight, 140 × 178 × 110 mm, fits the X1C
> (`node bin/validate.js` PASS). The MOUNT is a parametric TBD placeholder pending the two
> load-path opens below. Renders: `output/caddy-draft-front.png`, `caddy-draft-back.png`.
> (Supersedes the swappable-single-item idea in the old mount-adapter `PHASE2-ARCHITECTURE.md`.)

## 1. The reframe
One caddy holds **phone + Kindle + Yeti together**, prefer **unibody**. Parameterized
**per person** (Matt = reference, Hana = later dimension swap).

## 2. Coupling — UNIBODY (integrate the socket)
For the swappable idea a dovetail made sense. For a heavy combined caddy it doesn't: a
full bottle puts ~1.5–2 N·m of overturning moment through the mount, and any separable
coupling becomes the failure point. So **integrate the Phase-1 capture socket directly
into the caddy back** — one print, no joint to fail. The only interface left is the cleat
capture itself.

Cost: Hana's caddy reprints the whole thing. Fine — it's parameterized, just re-slice.

## 3. Packaging — does one print hold all three?
Bambu X1C bed = 256 × 256 (diagonal 362). Modeled interior envelopes (raw dim + margin):

| Item | Interior W | Interior T | Hold height |
|---|---|---|---|
| Phone | 81 | 18 | ~95 (protrudes) |
| Kindle | 134 | 17 | ~100 (protrudes) |
| Bottle | Ø ~102 cradle | — | low cup + tall back |

**Layout studied:**
- **Inline (all 3 across width):** 81 + 134 + 102 + walls ≈ **325 mm** → exceeds the bed. ❌
- **Bottle beside slot-pack:** ~241 × 104 → fits but very wide, near plate edge. ⚠
- **Depth-stack, all within Kindle width (RECOMMENDED):** everything ≤ 134 wide; rows
  in depth = bottle 102 + Kindle 17 + phone 18 + walls ≈ **~150 mm deep × ~140 wide**.
  Comfortable fit, ~110–130 tall. ✅

Recommended footprint ≈ **140 × 150 × ~120 mm** — well inside the build volume.

## 4. Layout & ergonomics (RECOMMENDED, provisional)
Order from the chair outward: **[mount/back] → bottle cradle → Kindle slot → phone slot
→ [front]**. Rationale:
- **Heaviest item (bottle) nearest the mount** → shortest lever arm → least overturning
  moment. Also kept **low** (open cup + tall back wall the bottle leans into).
- Kindle + phone as **thin angled slots**, tilted back ~10–15° so gravity keeps them
  seated; tops protrude for one-handed grab.
- Open bottoms / drain slots so sand + water shed.

⚠ **Ergonomic caveat to check:** bottle nearest the chair means reaching slightly past
the slots to grab it. If that reads awkward on the real chair, alternative is bottle at a
front corner (worse lever arm) — a structure-vs-reach tradeoff to settle against the
actual chair. This is why chair geometry matters.

## 5. Structural reality (the big one) — STANDALONE CANTILEVER (v3, WM#1104)
Full Yeti (~1.2–1.5 kg) + Kindle (~0.2) + phone (~0.25) + caddy (~0.5) ≈ **2.5 kg**
hanging off a ~28 × 40 mm cleat socket. Estimated overturning moment **~1.5–2 N·m**.

**Directive change (Matt, 2026-07-28):** do **NOT** rely on backing against the chair leg.
The cleat protrudes awkwardly — backing the caddy against the leg forces it way back and
leaves it leaning, and the leg fit is a 3D skew that's hard to capture or describe. So the
**cleat-mount + gussets must carry the full cantilever standalone.** A leg brace, if it
ever happens, is an *optional* bonus once Matt supplies the leg-skew dims — never the
primary load path.

v3 geometry to earn that (all in `shibumi-beach-caddy.scad`, all base-down printable):
1. **External side buttress gussets** — long right-triangles down each side, tall at the
   root (mount junction) tapering to the base at the front, running **along the load
   path**. They deepen the cantilever section exactly where the bending is highest.
2. **Back-corner haunches** — solid fillets tying the base plate into the spine in the
   dead corners outboard of the bottle ring; spreads the peak-moment junction into
   distributed compression/shear instead of a sharp stress riser.
3. **Deeper root section** — base plate 4.0 → **5.5 mm**, spine 6.0 → **8.0 mm**.
4. **Bottle nearest + low** (§4) so the heaviest item has the shortest lever arm.
5. **Unibody** (§2) — no coupling to peel apart.
6. **Print orientation = base-down (as-used).** The peak tensile fiber (top of the
   section at the root) then runs fore-aft = **in-plane** with the horizontal layers, and
   the base↔spine weld is loaded in shear/compression, **not interlayer peel**. (Directly
   addresses Matt's layer-plane concern.) Underside gussets aren't used because the
   receptacle floors force base-down printing — literal underside webs would be below the
   bed; the stiffening is placed above/around the platform + at the back instead.

**Honest flag:** a single beach-chair cleat may still not be rated to hold a full bottle
purely in cantilever regardless of how stiff the *caddy* is — the limit could be the cleat
itself or the socket's grip on it. `strain-analyzer` runs next on this geometry to quantify
root stress + safety factor; escalate to FEA if the margin is tight (the gusseted junction
isn't a clean prism). If the cleat can't take it, options are a lighter fill guidance
(don't fill the Yeti on the caddy) or a second capture point — but the mechanical design
target stays: standalone.

## 6. Build order (once unblocked)
1. Confirm **Yeti Ø** + bottle oz (mass).
2. Get **chair photos** around the cleat → decide load path (frame rest? second point?).
3. Lock layout (§4) + `rail_height` from the Phase-1 A/B/C result (for the integrated socket).
4. Parametric model: per-person dims block → item envelopes → cradle/slots → integrated
   socket → drain features.
5. `strain-analyzer` pass on the bottle load case.
6. Massing/fit print (PLA) → then final in PETG/ASA.
7. Hana variant = swap her dims, re-slice.

## Blockers / flags
1. ✅ **Yeti diameter** — RESOLVED: Ø96 confirmed (WM#592).
2. ~~Chair geometry / frame rest~~ — **NO LONGER a blocker** (WM#1104): standalone-cantilever
   directive removes the frame-rest dependency. Chair-leg dims are now only needed for the
   *optional* future brace, not the primary design.
3. **Phase-1 A/B/C fit result** — still sets the integrated socket's `rail_height` (shared
   blocker); mount stays a parametric placeholder until then. ⛳
4. **`strain-analyzer` pass** on the v3 gusseted geometry — confirm the standalone root
   section is adequate for the bottle load case; FEA if the margin is tight. ⛳
5. Device **hold heights** (protrusion per item) — Matt's ergonomic call; current values placeholder.
6. Bottle **oz** for mass estimate (assumed ~36oz).
