"""
Generative loopwork: the rules in RULES.md (v3), read off the source photographs.

The unit act, from which everything else is a choice of target:

    U - make a bight in the working strand, pass it through an open loop, and
        let the new bight become the open loop.

L1 pass through the loop you just made            -> a chain
L2 two carried strands, alternating every stitch  -> the colour
L3 pass through an OLDER loop                     -> the chain joins itself
L4 pass through a wooden ring                     -> the ring is captured
L5 the same act at more than one gauge
L6 stop, cut, let the tails hang
L7 three-dimensionality is a consequence, not a step
L8 the act needs an open loop AND somewhere to put the bight. When the tip has
   nowhere to go the work is NOT over -- the loop is carried round to another
   open loop that does, leaving a float. The work is over only when no open
   loop anywhere has a free site. Cord is unlimited; size and the ending are
   outputs.

There are no knots in this file, because there are none in the piece.
"""
import math, json, argparse
from dataclasses import dataclass, asdict

import numpy as np

# L3 is the one rule the photographs cannot pin down, so it is switchable.
TARGETS = {
    "chain":   "never join; a pure 1-D chain (the L3-off control)",
    "ladder":  "join to the stitch a fixed period back -> a tube of that girth",
    "window":  "join to any stitch within the last N -> an irregular mesh",
    "nearest": "join to whatever loop is nearest in SPACE -> self-felting blob",
    "random":  "join to any earlier stitch at all -> long-range tangle",
}

@dataclass
class Ruleset:
    seed: int = 7

    # L8. The work stops only when no open loop anywhere has a free site --
    # which, measured, essentially never happens: the surface of a growing mass
    # outruns the filling of it. So in practice `max_stitches` is how much work
    # YOU decide to do. It is a budget, not a rule, and stats say which ended
    # the run so the two are never confused.
    max_stitches: int = 2200
    loop_capacity: int = 3           # bights one loop can admit (photos: 1-3
                                     # visible; 2-4 is the defensible range)
    clearance: float = 0.65          # a new bight needs a free site, as a
                                     # fraction of the stitch pitch
    tries: int = 30                  # directions tried at the tip before the
                                     # work is carried somewhere else
    probes: int = 40                 # directions tried at a candidate loop
                                     # before it is written off as full. Raise
                                     # it until the final size stops moving.
    turn: float = 0.5                # fraction of the tries that sample the
                                     # WHOLE sphere rather than a cone ahead of
                                     # the hand. Cord is flexible: the work can
                                     # be turned. 0 = the hand may only go
                                     # forward, which stops it early for a
                                     # reason the craft does not have.
    contact: float = 1.9             # the act happens AT THE EDGE of the work,
                                     # not off in space: of the free sites the
                                     # hand tries, it takes the one most in
                                     # contact with existing fabric. Radius as
                                     # a multiple of the stitch pitch. 0 = off,
                                     # which makes the work a travelling walk.

    # L2: the carried strands, alternating one stitch each
    strands: str = "KN"              # K black, N natural
    # L5: the source works stretches in heavy tan roving, not isolated heavy
    # stitches. A run of `heavy_run` stitches every `heavy_every`.
    heavy_every: int = 120           # 0 = single gauge only
    heavy_run: int = 14
    heavy_scale: float = 2.8

    # L3: what an older-loop join picks, and how often it happens
    target_policy: str = "window"
    join_rate: float = 0.34
    ladder_period: int = 13
    window: int = 26
    nearest_radius: float = 1.15

    # L4: capture a wooden ring every N stitches (0 = never)
    ring_every: int = 130            # SOURCE-DERIVED: 3 rings on a ~400-stitch
                                     # piece. Was 70, which is twice too often.
    ring_radius: float = 0.46
    ring_tube: float = 0.075
    ring_weight: float = 7.0         # rings are heavy; they pull the work down

    # L6: a strand runs out every N stitches; joining in a new one leaves
    # two ends hanging. This is where the fringe comes from.
    strand_runs_out: int = 14        # SOURCE-DERIVED. ~50-60 tails counted on a
                                     # ~400-stitch piece means a strand ran out
                                     # every ~14 stitches, which at 8.5 cm of
                                     # cord per stitch is a 1.2 m working
                                     # length -- a sane thing to cut.
                                     # 0 = endless cord: scales to huge pieces
                                     # but contradicts the source's fringe.
    tail_stitches: int = 13
    tail_jitter: float = 0.5

    # The hand does not work at one tension. In the source the same tan cord
    # runs as a tight dense cable in one place and as big open loops in another,
    # roughly a 2.5-3x range within one photograph. Tension drifts in runs, not
    # stitch by stitch.
    tension_var: float = 0.45        # fractional spread of stitch size, 0 = none
    tension_run: int = 28            # stitches before the hand changes tension

    # gauge. cord_mm is what ties the model to the world: everything else is
    # measured in cord diameters, so the real size of a piece follows from it.
    # The cord is 3-ply and its twist is visible. Measured off the source:
    # banding period 6-9 px against a cord 14-20 px across, so the ply repeats
    # every ~0.45 cord diameters.
    # OFF by default: at the measured period the ply repeats every 0.045 units
    # while the cord path is sampled every 0.088, so a lobed cross-section
    # cannot express it -- it aliases into facets, which look worse than a
    # smooth cord. Rendering it needs ~46 samples per bight instead of 12, or
    # procedural shading rather than geometry. Numbers kept because they are
    # measured; set ply=3 with a much finer path if you want it.
    ply: int = 0
    ply_depth: float = 0.17          # groove depth, as a fraction of the radius
    ply_period: float = 0.45         # ply repeat in cord diameters (MEASURED)
    cord_mm: float = 8.0             # real diameter of the cord, millimetres
    cord_radius: float = 0.050
    loop_a: float = 0.21             # bight half-length, along the chain
    loop_b: float = 0.125            # bight half-width

    # the hand
    wander: float = 0.75             # how much the working direction drifts
    hand: float = 0.22               # per-stitch noise

    # L7 happens AS the work grows, not after it. The maker adds each stitch to
    # fabric that has already settled under its own weight, so the solver is
    # interleaved with growth rather than run once at the end.
    repel_cut: float = 1.25           # volume exclusion radius, in loop_a. The
                                     # handling work showed this is a LOOP
                                     # length while the cord is far thinner, so
                                     # it acts as long-range inflation rather
                                     # than exclusion. Lower = denser, more
                                     # cord-like; the source is dense.
    tension_only: bool = True        # cord resists stretch, not compression
    simulate_carries: bool = True    # the float a carry lays is cord too
    settle_every: int = 25           # stitches between settling passes
    settle_iters: int = 7            # solver iterations per pass
    keyframes: int = 28              # configurations recorded for the animation

    # relaxation
    iters: int = 160
    gravity: float = 0.0005
    stiff_chain: float = 0.30
    stiff_link: float = 0.22
    repel: float = 0.055
    damping: float = 0.80
    max_step: float = 0.22
    rebuild_every: int = 30

BLACK, NATURAL, HEAVY = "black", "natural", "heavy"
MATS = {BLACK: (0.085, 0.085, 0.095), NATURAL: (0.93, 0.89, 0.80),
        HEAVY: (0.76, 0.63, 0.47), "wood": (0.84, 0.72, 0.52)}

def norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else np.array([1.0, 0.0, 0.0])

# ---------------------------------------------------------------- U + L1-L4

def tension_of(R, n, seed):
    """Per-stitch size multiplier. Piecewise over runs, so the work tightens
    and loosens in passages the way a hand does rather than jittering."""
    rng = np.random.default_rng(seed + 991)
    t = np.ones(n)
    if R.tension_var <= 0:
        return t
    i = 0
    while i < n:
        run = max(4, int(rng.normal(R.tension_run, R.tension_run * 0.35)))
        lvl = 1.0 + R.tension_var * (rng.random() - 0.5) * 2.0
        t[i:i + run] = max(0.35, lvl)
        i += run
    return t

def work(R: Ruleset):
    """Apply the unit act until the fabric will not take it again.

    L8. Nothing here counts out a length of work. Each stitch needs two things,
    both of which the fabric can refuse: an open loop to pass through (one that
    has not already taken `loop_capacity` bights), and a free site to occupy
    (no existing loop already there). When no direction the hand tries offers
    both, the act cannot be performed and the work is finished.
    """
    rng = np.random.default_rng(R.seed)
    if R.target_policy not in TARGETS:
        raise SystemExit(f"unknown L3 target policy {R.target_policy!r}; "
                         f"choose from {sorted(TARGETS)}")

    cap = R.max_stitches
    P = np.zeros((cap, 3))
    target = np.arange(-1, cap - 1)
    joined = np.zeros(cap, bool)
    occ = np.zeros(cap, np.int32)        # bights passed through each loop
    rings, tails = [], []

    tens = tension_of(R, cap, R.seed)
    pitch = R.loop_a * 1.15
    clear = R.clearance * pitch
    cell = max(clear, 1e-6)
    ccell = max(R.contact * pitch, cell)   # coarse cells for the contact count
    grid, cgrid = {}, {}                   # two incremental spatial indices

    def key(p, c=None):
        c = c or cell
        return (int(p[0] // c), int(p[1] // c), int(p[2] // c))

    pts = {}                               # plain-float mirror of P. numpy
                                           # scalar indexing inside the hot
                                           # loop costs more than the maths.

    def add(i):
        grid.setdefault(key(P[i]), []).append(i)
        cgrid.setdefault(key(P[i], ccell), []).append(i)
        pts[i] = (float(P[i][0]), float(P[i][1]), float(P[i][2]))

    def contact_count(p):
        """how much fabric is near p. Coarse by design -- it only has to RANK
        candidate sites, so a cell count is enough and a radius test is not."""
        kx, ky, kz = key(p, ccell)
        t = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    t += len(cgrid.get((kx+dx, ky+dy, kz+dz), ()))
        return t

    def near(p, radius):
        """indices within `radius` of p, using the incremental cell index"""
        span = int(radius // cell) + 1
        kx, ky, kz = key(p)
        hit = []
        for dx in range(-span, span + 1):
            for dy in range(-span, span + 1):
                for dz in range(-span, span + 1):
                    for j in grid.get((kx+dx, ky+dy, kz+dz), ()):
                        if np.linalg.norm(P[j] - p) < radius:
                            hit.append(j)
        return hit

    c2 = clear * clear

    def free(p, exclude, scale=1.0):
        c2s = (clear * scale) ** 2
        px, py, pz = float(p[0]), float(p[1]), float(p[2])
        kx, ky, kz = int(px // cell), int(py // cell), int(pz // cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    b = grid.get((kx+dx, ky+dy, kz+dz))
                    if not b:
                        continue
                    for j in b:
                        if j in exclude:
                            continue
                        qx, qy, qz = pts[j]
                        ex, ey, ez = qx-px, qy-py, qz-pz
                        if ex*ex + ey*ey + ez*ez < c2s:
                            return False
        return True

    # a fixed spread of directions for probing a candidate loop, so writing a
    # loop off is a thorough test rather than a lucky one
    gold = np.pi * (3 - 5 ** 0.5)
    kk = np.arange(R.probes) + 0.5
    zz = 1 - 2 * kk / R.probes
    rr = np.sqrt(np.maximum(0.0, 1 - zz * zz))
    PROBE = np.stack([rr * np.cos(gold * kk), rr * np.sin(gold * kk), zz], axis=1)

    dead = np.zeros(cap, bool)       # loops with no free site left. Space only
                                     # ever fills, so this is monotone: once a
                                     # loop is written off it stays written off.
    carries = []                     # (from stitch, to stitch) floats

    def relocate(n):
        """L8. The tip is stuck, so carry the working loop somewhere it is not.
        Returns (target loop, position, direction) or None if the whole fabric
        is saturated."""
        live = np.where((~dead[:n]) & (occ[:n] < R.loop_capacity))[0]
        for j in rng.permutation(live):
            for d_ in PROBE:
                pos = P[j] + pitch * d_
                if free(pos, {int(j)}):
                    return int(j), pos, d_
            dead[j] = True
        return None

    def rebuild_index(upto):
        """settling moved every stitch, so the spatial index is stale"""
        grid.clear(); cgrid.clear(); pts.clear()
        for i in range(upto):
            add(i)

    link_rest = R.loop_a * 0.95
    vel = np.zeros((cap, 3))
    mass = np.ones(cap)
    keyframes = []
    kf_step = max(1, R.max_stitches // max(1, R.keyframes))

    add(0)
    d = np.array([1.0, 0.0, 0.0])
    n = 1
    ended = "safety_bound"

    while n < cap:
        placed = False
        base = d
        best = None                  # (contact count, position, dir, target)
        for attempt in range(R.tries):
            # the hand tries its current direction first, then casts wider,
            # and finally turns the work and looks anywhere at all
            if attempt >= R.tries * (1.0 - R.turn):
                dd = norm(rng.normal(size=3))
            else:
                spread = R.wander * (0.35 + 1.5 * attempt / max(1, R.tries - 1))
                dd = norm(base + spread * (rng.random(3) - 0.5) + np.array([0, 0, -0.012]))
            lp = pitch * tens[n]
            guess = P[n-1] + lp * dd + R.hand * lp * (rng.random(3) - 0.5)

            t = n - 1
            if n > 3 and rng.random() < R.join_rate:
                t = pick_target(R, rng, n, P, guess, occ)
            if occ[t] >= R.loop_capacity:                 # L8: loop is full
                if occ[n-1] >= R.loop_capacity:
                    continue
                t = n - 1
            pos = guess if t == n - 1 else 0.45 * guess + 0.55 * P[t]
            if not free(pos, exclude={n-1, t}, scale=tens[n]):   # L8: no room
                continue

            if R.contact <= 0:
                best = (0, pos, dd, t); break
            # of the sites that are free, prefer the one most in contact with
            # the fabric already made: the work grows on itself, not away
            c = contact_count(pos)
            if best is None or c > best[0]:
                best = (c, pos, dd, t)

        if best is not None:
            _, pos, dd, t = best
            P[n] = pos; target[n] = t; joined[n] = (t != n - 1)
            occ[t] += 1
            add(n); d = dd; placed = True

        if not placed:
            # the tip is walled in -- but the fabric is not. Carry the work
            # round to an open loop that still has room. The cord spans the
            # gap, which is a float and is drawn as one.
            got = relocate(n)
            if got is None:
                ended = "saturated"       # no open loop anywhere has a free site
                break
            t, pos, dd = got
            carries.append((n - 1, n, float(np.linalg.norm(pos - P[n - 1]))))
            P[n] = pos; target[n] = t; joined[n] = True
            occ[t] += 1
            add(n); d = dd

        if R.ring_every and n % R.ring_every == 0:
            rings.append(n)
        if R.strand_runs_out and n % R.strand_runs_out == 0:
            tails.append(n)
        n += 1

        # L7 as it happens: the work settles under its own weight while it is
        # still being made, so the next stitch goes onto fabric that has
        # already moved. This is why the form unfolds and twists as it grows
        # rather than being a rigid scaffold relaxed once at the end.
        if R.settle_every and n > 4 and n % R.settle_every == 0:
            mass[:n] = 1.0
            live_rings = [r for r in rings if r < n]
            if live_rings:
                mass[live_rings] = R.ring_weight
            solve(R, P, target, joined, carries, n, vel,
                  R.settle_iters, pitch, link_rest, mass, tens)
            rebuild_index(n)
        if n % kf_step == 0:
            keyframes.append((n, P[:n].astype(np.float32).copy()))

    P = P[:n]; target = target[:n]; joined = joined[:n]; occ = occ[:n]
    tails.append(n - 1)
    colour = np.array([BLACK if R.strands[i % len(R.strands)] == "K" else NATURAL
                       for i in range(n)], dtype=object)
    if R.heavy_every:                              # L5
        # contiguous runs: the maker picks up the rope and works with it for a
        # while. Scattering single heavy stitches through a fine chain was a
        # thing no cord does.
        for st in range(R.heavy_every, n, R.heavy_every):
            colour[st:min(n, st + R.heavy_run)] = HEAVY
    return dict(P=P, target=target, joined=joined, occ=occ, rings=rings,
                tails=tails, colour=colour, ended=ended, carries=carries,
                dead=int(dead[:n].sum()), keyframes=keyframes, vel=vel[:n],
                tens=tens[:n])

def pick_target(R, rng, i, P, guess, occ):
    """L3. The one rule the photographs cannot settle, so it is a policy.
    Every policy may only return a loop that still has room (L8)."""
    p = R.target_policy
    if p == "chain":
        return i - 1
    if p == "ladder":
        return max(0, i - R.ladder_period)
    if p == "window":
        lo = max(0, i - R.window)
        return int(rng.integers(lo, i - 1)) if i - 1 > lo else i - 1
    if p == "random":
        return int(rng.integers(0, i - 1))
    if p == "nearest":
        # nearest ALREADY-MADE loop in space. Excludes a run of sequential
        # neighbours, which are near only because they are adjacent -- joining
        # to those is L1 again, not L3.
        if i < 10:
            return i - 1
        dist = np.linalg.norm(P[:i - 6] - guess, axis=1)
        dist[occ[:i - 6] >= R.loop_capacity] = np.inf      # full loops refuse
        j = int(np.argmin(dist))
        return j if dist[j] < R.nearest_radius else i - 1
    return i - 1

# ---------------------------------------------------------------- L7: relax

def cell_pairs(P, cutoff):
    """Neighbour pairs via a cell hash. No scipy here, and N^2 every step is
    too slow to stay live, so this is rebuilt every `rebuild_every` iterations."""
    keys = np.floor(P / cutoff).astype(np.int64)
    buckets = {}
    for idx, k in enumerate(map(tuple, keys)):
        buckets.setdefault(k, []).append(idx)
    a, b = [], []
    for (x, y, z), members in buckets.items():
        near = []
        for dx in (0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if (dx, dy, dz) < (0, 0, 0):
                        continue
                    near += buckets.get((x + dx, y + dy, z + dz), ())
        for i in members:
            for j in near:
                if j > i:
                    a.append(i); b.append(j)
    if not a:
        return np.zeros(0, np.intp), np.zeros(0, np.intp)
    return np.array(a, np.intp), np.array(b, np.intp)

def scatter(F, idx, vals, n):
    """F[idx] += vals, accumulating duplicates. bincount is several times
    faster than np.add.at on arrays this size."""
    for k in range(3):
        F[:, k] += np.bincount(idx, weights=vals[:, k], minlength=n)

def solve(R, P, tgt, joined, carries, n, vel, iters, pitch, link_rest, mass, tens=None):
    """Run `iters` solver steps over the first n stitches. Used both for the
    settling passes during growth and for the final relaxation, so growth-time
    and final physics cannot drift apart."""
    ca, cb = np.arange(1, n), np.arange(0, n - 1)
    ja = np.arange(1, n)[joined[1:n]]
    jb = tgt[ja]
    # the float left by a carry is cord too, and it was not being simulated at
    # all: `carries` was passed in and never used. Its rest length is the gap it
    # was laid across, recorded when it was made.
    cc = ([(a, b, L) for (a, b, L) in carries if a < n and b < n]
          if R.simulate_carries else [])
    kа = np.array([c[1] for c in cc], np.intp) if cc else np.zeros(0, np.intp)
    kb = np.array([c[0] for c in cc], np.intp) if cc else np.zeros(0, np.intp)
    kr = np.array([c[2] for c in cc], float) if cc else np.zeros(0)
    ea = np.concatenate([ca, ja, kа]); eb = np.concatenate([cb, jb, kb])
    # rest length follows the tension the stitch was worked at, or the springs
    # fight the placement: pulling the tight passages open and the loose shut
    tt = np.ones(n) if tens is None else np.asarray(tens[:n])
    rest = np.concatenate([pitch * tt[ca], link_rest * tt[ja], kr])
    cutoff = R.loop_a * R.repel_cut
    pa = pb = np.zeros(0, np.intp)
    for it in range(iters):
        if it % R.rebuild_every == 0:
            pa, pb = cell_pairs(P[:n], cutoff)
        F = np.zeros((n, 3))
        d = P[ea] - P[eb]
        L = np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
        # TENSION ONLY: cord resists being stretched and does nothing when
        # slack. A two-sided spring is a strut holding the work open.
        ext = (np.maximum(0.0, L - rest[:, None]) if R.tension_only
               else (L - rest[:, None]))
        pull = ext / L * d
        scatter(F, ea, -R.stiff_chain * pull, n)
        scatter(F, eb,  R.stiff_chain * pull, n)
        if len(pa):
            d2 = P[pa] - P[pb]
            L2 = np.linalg.norm(d2, axis=1, keepdims=True) + 1e-9
            over = np.maximum(0.0, cutoff - L2)
            push = R.repel * over / L2 * d2
            scatter(F, pa,  push, n)
            scatter(F, pb, -push, n)
        F[:, 2] -= R.gravity * mass[:n]
        vel[:n] = R.damping * vel[:n] + F
        np.clip(vel[:n], -R.max_step * pitch, R.max_step * pitch, out=vel[:n])
        P[:n] += vel[:n]
        P[0] = 0.0

def relax(R, w):
    """Final settling. The work has been settling all along, so this is a
    finishing pass over the whole piece, not the first time physics is applied."""
    P = w["P"]
    n = len(P)
    pitch = R.loop_a * 1.15
    mass = np.ones(n)
    if w["rings"]:
        mass[[r for r in w["rings"] if r < n]] = R.ring_weight
    vel = np.zeros((n, 3))
    solve(R, P, w["target"], w["joined"], w["carries"], n, vel,
          R.iters, pitch, R.loop_a * 0.95, mass, w.get("tens"))
    w["keyframes"].append((n, P.astype(np.float32).copy()))
    return P

def check(w):
    """A silent NaN and an empty object render identically."""
    P = w["P"]
    if not np.isfinite(P).all():
        raise SystemExit("RELAX FAILED: %d non-finite stitches" % int((~np.isfinite(P)).sum()))
    bb = P.max(axis=0) - P.min(axis=0)
    if bb.min() < 1e-3:
        raise SystemExit("RELAX FAILED: degenerate bbox %s" % bb)
    if len(P) < 20:
        raise SystemExit("RELAX FAILED: only %d stitches" % len(P))
    return bb

def build(R: Ruleset):
    w = work(R)
    w["P"] = relax(R, w)
    check(w)
    return w


# ---------------------------------------------------------------- geometry
# A stitch is drawn as the bight it actually is: a closed loop of cord. Two
# consecutive bights overlap, so the chain reads as a chain. Alternate bights
# are offset to opposite faces, which is what a real chain does.

def frames(P, i, n):
    """chain tangent / fabric normal / lateral at stitch i"""
    a = P[max(0, i - 1)]; b = P[min(n - 1, i + 1)]
    T = norm(b - a)
    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(T, up)) > 0.92:
        up = np.array([1.0, 0.0, 0.0])
    Lv = norm(np.cross(T, up))
    N = np.cross(Lv, T)
    return T, Lv, N

def bight(R, P, i, n, seg=16, scale=1.0):
    """The closed curve of one stitch.

    Consecutive bights share the chain axis and have their planes at right
    angles, so they thread through one another the way links of a chain do.
    The previous version offset alternate loops sideways by less than a cord
    diameter, which meant the cord passed through itself -- the single most
    unrealistic thing in the render.
    """
    T, Lv, N = frames(P, i, n)
    X = Lv if i % 2 == 0 else N
    a = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    return (P[i][None, :] + R.loop_a * scale * np.cos(a)[:, None] * T[None, :]
                          + R.loop_b * scale * np.sin(a)[:, None] * X[None, :])

def tube(pts, radius, sides=12, closed=False, R=None):
    pts = np.asarray(pts, float)
    keep = [pts[0]]
    for p in pts[1:]:
        if np.linalg.norm(p - keep[-1]) > 1e-6:
            keep.append(p)
    pts = np.array(keep)
    if len(pts) < 3:
        return np.zeros((0, 3)), []
    T = np.gradient(pts, axis=0)
    T /= (np.linalg.norm(T, axis=1, keepdims=True) + 1e-9)
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(T[0], ref)) > 0.9:
        ref = np.array([1.0, 0.0, 0.0])
    Nv = norm(np.cross(T[0], ref))
    # arc length along the cord, so the ply twists at a fixed rate per length
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    nply = 0 if R is None else R.ply
    depth = 0.0 if R is None else R.ply_depth
    per = (1.0 if R is None else R.ply_period) * 2 * radius
    V, F = [], []
    for i, p in enumerate(pts):
        Nv = norm(Nv - np.dot(Nv, T[i]) * T[i])
        Bv = np.cross(T[i], Nv)
        phase = 2 * math.pi * arc[i] / per if per > 1e-9 else 0.0
        for s in range(sides):
            ang = 2 * math.pi * s / sides
            lobe = 1.0 + depth * math.cos(nply * ang - phase) if nply else 1.0
            V.append(p + radius * lobe * (math.cos(ang) * Nv + math.sin(ang) * Bv))
    rng_n = len(pts) if closed else len(pts) - 1
    for i in range(rng_n):
        j = (i + 1) % len(pts)
        for s in range(sides):
            s2 = (s + 1) % sides
            a_, b_, c_, d_ = i*sides+s, i*sides+s2, j*sides+s2, j*sides+s
            F += [(a_, b_, c_), (a_, c_, d_)]
    return np.array(V), F

def tail_paths(R, w):
    """L6: a strand runs out, you join a new one, two ends hang."""
    rng = np.random.default_rng(R.seed + 1)
    P, n = w["P"], len(w["P"])
    out = []
    pitch = R.loop_a * 1.15
    for s in w["tails"]:
        T, Lv, N = frames(P, min(s, n - 1), n)
        for side in (-1, 1):
            k = max(3, int(R.tail_stitches * (1 - R.tail_jitter * rng.random())))
            p = P[min(s, n - 1)].copy()
            d = norm(side * 0.5 * Lv + np.array([0, 0, -1.0]))
            path = [p.copy()]
            for _ in range(k):
                d = norm(d + 0.22 * (rng.random(3) - 0.5) + np.array([0, 0, -0.55]))
                p = p + pitch * 1.25 * d
                path.append(p.copy())
            out.append((np.array(path), w["colour"][min(s, n - 1)]))
    return out

def ring_frame(R, w, s):
    """L4: the ring is threaded ON the cord, so its place is the cord's place."""
    P, n = w["P"], len(w["P"])
    T, Lv, N = frames(P, s, n)
    return P[s], T

def carry_path(P, a, b, seg=9):
    """the float left when the work is carried to another open loop"""
    t = np.linspace(0, 1, seg)[:, None]
    mid = 0.5 * (P[a] + P[b]) + np.array([0, 0, -0.06]) * np.linalg.norm(P[b] - P[a])
    return (1 - t) ** 2 * P[a] + 2 * (1 - t) * t * mid + t ** 2 * P[b]

def pieces(R, w, shade=None):
    """everything to be drawn, grouped by material, each chunk carrying the
    measured shade of the stitch it belongs to"""
    P, n = w["P"], len(w["P"])
    sh = occlusion(R, w) if shade is None else shade
    g = {BLACK: [], NATURAL: [], HEAVY: [], "wood": []}
    for a, b, *_ in w["carries"]:
        col = w["colour"][b]
        rad = R.cord_radius * (R.heavy_scale if col == HEAVY else 1.0)
        g[col].append((carry_path(P, a, b), rad, False, float(sh[b])))
    for i in range(n):
        col = w["colour"][i]
        rad = R.cord_radius * (R.heavy_scale if col == HEAVY else 1.0)
        g[col].append((bight(R, P, i, n, scale=float(w["tens"][i])), rad, True, float(sh[i])))
    for (path, col), si in zip(tail_paths(R, w),
                               [s2 for s2 in w["tails"] for _ in (0, 1)]):
        rad = R.cord_radius * (R.heavy_scale if col == HEAVY else 1.0)
        g[col].append((path, rad, False, float(sh[min(si, n-1)])))
    for s in w["rings"]:
        c, axis = ring_frame(R, w, s)
        up = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(axis, up)) > 0.92:
            up = np.array([1.0, 0.0, 0.0])
        u = norm(np.cross(axis, up)); v = np.cross(axis, u)
        a = np.linspace(0, 2 * math.pi, 40, endpoint=False)
        circ = c[None, :] + R.ring_radius * (np.cos(a)[:, None] * u[None, :]
                                           + np.sin(a)[:, None] * v[None, :])
        g["wood"].append((circ, R.ring_tube, True, 1.0))
    return g

def export_obj(path, R, w):
    g = pieces(R, w)
    mtl = path.rsplit("/", 1)[-1].replace(".obj", ".mtl")
    nv = nf = 0
    with open(path, "w") as f:
        f.write(f"mtllib {mtl}\n")
        for name, chunks in g.items():
            if not chunks:
                continue
            f.write(f"o {name}\nusemtl {name}\n")
            base = MATS[name]
            for pts, rad, closed, sh in chunks:
                V, F = tube(pts, rad, closed=closed, R=R)
                cr, cg, cb = base[0]*sh, base[1]*sh, base[2]*sh
                for v in V:
                    f.write("v %.5f %.5f %.5f %.3f %.3f %.3f\n"
                            % (v[0], v[1], v[2], cr, cg, cb))
                for a_, b_, c_ in F:
                    f.write("f %d %d %d\n" % (a_+nv+1, b_+nv+1, c_+nv+1))
                nv += len(V); nf += len(F)
    with open(path.replace(".obj", ".mtl"), "w") as f:
        for name, c in MATS.items():
            f.write(("newmtl %s\nKd %.3f %.3f %.3f\nKs 0.04 0.04 0.04\nNs 10\n\n"
                     % (name, c[0], c[1], c[2])))
    return nv, nf

def export_svg(path, R, w, size=900, elev=0.34, azim=0.9):
    segs = []
    for name, chunks in pieces(R, w).items():
        base = MATS[name]
        for pts, rad, closed, sh in chunks:
            col = (base[0]*sh, base[1]*sh, base[2]*sh)
            idx = list(range(len(pts))) + ([0] if closed else [])
            for a_, b_ in zip(idx, idx[1:]):
                segs.append((pts[a_], pts[b_], col, rad))
    ca, sa = math.cos(azim), math.sin(azim)
    ce, se = math.cos(elev), math.sin(elev)
    def cam(p):
        x = ca*p[0] + sa*p[1]; y = -sa*p[0] + ca*p[1]; z = p[2]
        return np.array([y, ce*z - se*x, se*z + ce*x])
    proj = [(cam(a_), cam(b_), c_, r_) for a_, b_, c_, r_ in segs]
    xs = [p[0] for s in proj for p in (s[0], s[1])]
    ys = [p[1] for s in proj for p in (s[0], s[1])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sc = 0.9*size/max(x1-x0, y1-y0, 1e-9)
    def tx(p): return (size/2 + (p[0]-(x0+x1)/2)*sc, size/2 - (p[1]-(y0+y1)/2)*sc)
    proj.sort(key=lambda s: (s[0][2]+s[1][2])/2)
    dmin = min((s[0][2]+s[1][2])/2 for s in proj)
    dmax = max((s[0][2]+s[1][2])/2 for s in proj)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
           f'viewBox="0 0 {size} {size}"><rect width="100%" height="100%" fill="#4a443c"/>']
    for a_, b_, c_, r_ in proj:
        t = ((a_[2]+b_[2])/2 - dmin)/max(dmax-dmin, 1e-9)
        sh = 0.45 + 0.55*t
        col = "#%02x%02x%02x" % tuple(int(255*min(1, ch*sh)) for ch in c_)
        (ax, ay), (bx, by) = tx(a_), tx(b_)
        out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
                   f'stroke="{col}" stroke-width="{max(0.6, 2*r_*sc):.2f}" stroke-linecap="round"/>')
    out.append("</svg>")
    open(path, "w").write("\n".join(out))
    return len(proj)

def occlusion(R, w, radius=None, floor=0.42):
    """How buried each stitch is, from its own neighbourhood.

    This is not a lighting trick bolted on afterwards: it is a measurement of
    the object. A stitch with many neighbours is deep inside the mass and
    receives little light; one with few is on the surface. Returned as a
    multiplier in [floor, 1] to be baked into the cord colour, which is what
    makes a dense tangle read as a volume instead of a flat snarl.
    """
    P = w["P"]
    n = len(P)
    r = radius if radius else R.loop_a * 3.2
    cell = r
    grid = {}
    for i, p in enumerate(P):
        grid.setdefault((int(p[0]//cell), int(p[1]//cell), int(p[2]//cell)), []).append(i)
    pts = [(float(p[0]), float(p[1]), float(p[2])) for p in P]
    cnt = np.zeros(n)
    r2 = r * r
    for i in range(n):
        px, py, pz = pts[i]
        kx, ky, kz = int(px//cell), int(py//cell), int(pz//cell)
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    b = grid.get((kx+dx, ky+dy, kz+dz))
                    if not b:
                        continue
                    for j in b:
                        qx, qy, qz = pts[j]
                        ex, ey, ez = qx-px, qy-py, qz-pz
                        if ex*ex + ey*ey + ez*ez < r2:
                            c += 1
        cnt[i] = c - 1
    if n < 2 or cnt.max() <= 0:
        return np.ones(n)
    # rank-normalise: absolute counts depend on gauge, the ORDER does not
    order = cnt.argsort().argsort() / max(1, n - 1)
    return floor + (1 - floor) * (1 - order) ** 0.85

def stats(R, w):
    P = w["P"]
    bb = P.max(axis=0) - P.min(axis=0)
    return {"stitches": len(P),                   # OUTPUT: nobody set this
            "ended": w["ended"],                     # "saturated" or "safety_bound"
            "carries": len(w["carries"]),            # times the work was carried
            "dead_loops": w["dead"],                 # loops written off as full
            "max_occupancy": int(w["occ"].max()),
            "full_loops": int((w["occ"] >= R.loop_capacity).sum()),
            "joins": int(w["joined"].sum()),          # L3 fired this often
            "rings": len(w["rings"]),                 # L4 captures
            "tail_ends": 2 * len(w["tails"]),         # L6
            "policy": R.target_policy,
            "bbox": [round(float(v), 3) for v in bb],
            "cm_per_unit": round(R.cord_mm / 10.0 / (2 * R.cord_radius), 3),
            "size_cm": [round(float(v) * R.cord_mm / 10.0 / (2 * R.cord_radius), 1)
                        for v in bb],
            "aspect": round(float(bb.max()/max(bb.min(), 1e-9)), 2),
            # cord is ~1.07 bight-perimeters per stitch; stated in metres so the
            # strand length can be sanity-checked against what a person cuts
            "strand_m": (round(R.strand_runs_out * 1.069 * R.cord_mm / 10.0
                               / (2 * R.cord_radius) / 100.0, 2)
                         if R.strand_runs_out else None)}

def main():
    ap = argparse.ArgumentParser(description="generative loopwork (RULES.md v3)")
    d = Ruleset()
    for k, v in asdict(d).items():
        ap.add_argument("--" + k.replace("_", "-"), type=type(v), default=v)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    R = Ruleset(**{k: getattr(a, k) for k in asdict(d)})
    w = build(R)
    nv, nf = export_obj(a.out + ".obj", R, w)
    ns = export_svg(a.out + ".svg", R, w)
    s = stats(R, w); s.update({"verts": nv, "tris": nf, "svg_segments": ns})
    open(a.out + ".json", "w").write(json.dumps({"ruleset": asdict(R), "stats": s}, indent=2))
    print(json.dumps(s))

if __name__ == "__main__":
    main()
