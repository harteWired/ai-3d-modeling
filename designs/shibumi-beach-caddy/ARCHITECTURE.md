# Shibumi Beach Caddy — Architecture (Phase 2)

> Status: **v0 architecture / massing.** Packaging + structural reasoning locked here;
> real geometry waits on two opens (Yeti Ø, chair load path). Written 2026-07-25 from
> WM#584/585. Supersedes the swappable-single-item idea in the old mount-adapter
> `PHASE2-ARCHITECTURE.md`.

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

## 5. Structural reality (the big one)
Full Yeti (~1.2–1.5 kg) + Kindle (~0.2) + phone (~0.25) + caddy (~0.5) ≈ **2.5 kg**
hanging off a ~28 × 40 mm cleat socket. Estimated overturning moment **~1.5–2 N·m**.

That is a lot for a small plastic slide-on clip. Mitigations, in priority:
1. **Bear on the chair frame.** The caddy should rest/brace against the chair leg or arm
   so vertical load + moment flow into the chair, and the cleat mainly *locates* it.
   **Requires chair geometry.**
2. **Bottle nearest + low** (see §4) to minimize its lever arm.
3. **Unibody** (§2) — no coupling to peel apart.
4. Possible second contact / brace against the leg if #1 isn't enough.

Honest flag: a single beach-chair cleat may not be rated to hold a full bottle purely in
cantilever. We need to see the chair to decide whether one mount + a frame rest is enough,
or whether a second mount / strap is warranted. `strain-analyzer` runs once geometry +
load path are real.

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
1. **Yeti diameter** — 96 mm dia assumed (Matt said "radius"); + bottle oz for mass. ⛳
2. **Chair geometry / load path** — photos around the cleat; can it rest on the frame? ⛳
3. **Phase-1 A/B/C fit result** — sets the integrated socket's `rail_height` (shared blocker). ⛳
4. Confirm **unibody + depth-stack layout** before cutting real geometry.
