# Measurements (predictions in PREDICTIONS.md, written first)

| # | prediction | result |
|---|---|---|
| P1 | seed changes form, not topology | **PASS on topology** — knots 435 and ends 174 identical across seeds; bbox moved 10%. **Prediction partly wrong**: I said centroid would move >1%, it moved 0.3%. Centroid is the wrong aggregate here — the anchors are pinned to the rings, so the mean barely moves whatever the sheet does. bbox is the discriminator; the centroid criterion is withdrawn, not rescued. |
| P2 | colour is geometrically inert | **PASS** — 70/174 ends recoloured (40.2%), lattice arrays bit-identical. First attempt at this measured per-material vertex *totals* and read 5.7%; that metric counts net imbalance, not reassignment, and would have read ~0% even if every cord swapped. Reading withdrawn and remeasured per cord. |
| P3 | slack is the only source of buckling | **PASS** — slack 1.38 -> 1.02 shrank bbox-y 3.39 -> 2.83 (-16%). |
| P4 | rows scales knot count | **PASS** — rows 14 -> 5 gave knots 435 -> 180 (2.4x). |
| P5 | CONTROL: render is downstream of the solve | **PASS** — two seeds, two different SVG md5s. Note `svg_segments` is *not* a health metric: it stayed 2344 across every perturbation because it counts topology. It also read 2394 during the run where the solver had produced all-NaN geometry. |
| P6 | CONTROL: R4 alternation is live code | **PASS** — `--no-alternate` changed knots 435 -> 456 and moved the bbox. Had it changed nothing, the net would not have been an ASK net. |

## Instrument floors
`check()` refuses to export on any non-finite lattice point, on a collapsed
bbox, or on fewer than 100 lattice points. This exists because the first working
run emitted a complete, plausible-looking SVG and a valid OBJ from geometry that
was entirely NaN — an empty picture and a dead solver render the same.
OBJ export is separately checked for face indices in range (0 out of 36832 bad).

## Not measured
Whether the inferred rules are the rules the maker actually used. Everything in
RULES.md is inferred from two photographs of an assembled object; R7 in
particular (slack as the source of three-dimensionality) is load-bearing and
unverifiable without handling the piece. The generator proves the rules are
*sufficient* to produce objects of this family. It does not prove they are the
ones that produced this one.

## Viewer checks

| check | result |
|---|---|
| materials bind | all four groups present with the colours from the `.mtl`: black `#17171a`, natural `#ede3cc`, roving `#c2a178`, wood `#d6b885`. Needed because an OBJ whose `usemtl` precedes its `o` silently loads single-coloured. |
| geometry is the generator's | GPU drew 36,832 triangles for piece_a and 61,584 for piece_b — equal to the counts the generator reported for each. The viewer is not showing a stand-in. |
| CONTROL: rings toggle is live | turning it off removes the tan circles and leaves the knotted bands. Had the picture not changed, the name-based group lookup would have been dead. |
| no horizontal scroll at 375px | confirmed; panel docks to the bottom edge. |

First render came out uniformly tan and looked like a material failure. It was
not: the black cord was loading correctly and was invisible against a near-black
stage. Fixed by lightening the stage, not by changing the cord colour — the
export is the honest colour and the renderer was the thing at fault.

---

# Second round — the growth engine

Everything above was measured against the engine that took ring count as an
input. That engine is gone. These numbers replace it; the old ones are kept
because the reasoning, and the two withdrawn readings, are the useful part.

Also changed in between: the solver was vectorised (0.74s from 10.2s, 13.7x).
The rewrite clamps the stored velocity rather than only the step taken from it,
which is a real behavioural change — geometry moved, e.g. bbox 3.44 -> 3.17 on
x at fixed parameters. Knot and end counts were unaffected. Flagging it because
it means the first round's bbox numbers are not comparable with these.

| # | prediction | result |
|---|---|---|
| G1 | budget up -> rings up | **PASS** — budget 60/100/160/240/320 gives 3/3/6/8/11 rings, monotonic. |
| G2 | more starting cords -> FEWER rings | **PASS** — at budget 160, 8/20/40/72 cords give 7/6/4/3 rings. Wide bands spend the budget faster, so they buy fewer generations. |
| G3 | bigger rings -> fewer splits | **PASS** — ring radius 0.22/0.34/0.5/0.7 gives 2/1/1/1 splits at 40 starting cords. Not zero at 0.7: 40 cords relax to 2.07 wide against a 1.96 capture arc, so it still just outgrows the ring. |
| G4 | CONTROL: with hand=0, seeds identical | **FAILED AS WRITTEN** — seeds still differed. My prediction was wrong, not the code: I had forgotten there is a *second* seeded input, the initial lattice jitter that breaks the relaxation's symmetry. Verified rather than assumed: with `hand=0, jitter=0` the structural lattice is bit-identical across seeds 1/2/3, and with either one non-zero it is not. So the seed enters in exactly two places and both are named. |
| G4b | hand>0 varies form, not structure | **PASS** — at hand=0.30 seeds 1 and 2 give bbox [3.00,2.79,2.83] vs [4.00,2.92,2.39] with identical ring, band and knot counts. The seed is the hand; the rules are the rules. |
| G5 | CONTROL: max_branch=1 kills branching | **PASS** — 40 starting cords give 4 rings / 1 split normally, 2 rings / 0 splits with branching forbidden. The branching code is live, and ring count really is downstream of it. |

## The one point of contact with the real object
20 starting cords on a budget of 80-100 produces 3 rings, which is what the
source piece has. That is one agreement on one integer, between two free
parameters I chose. It is consistent with the rules; it is not evidence for
them. I have no measurement of the real piece's cord length or cord count.

## Viewer checks (live generation)
| check | result |
|---|---|
| generation is live | `/api/generate` returns in 0.31-0.85s; round trip measured in-page at 321-954ms. The browser holds no generator — it draws what the one Python implementation returns, so the two cannot drift. |
| build animation is real | drawn cord vertices rise monotonically with progress: 2,520 / 26,040 / 47,040 / 58,590 at t = 0.1 / 0.42 / 0.75 / 1, and GPU triangles 5,240 -> 23,930. The reveal is a growing drawRange over triangles ordered along the cord, not a fade. |
| controls drive the generator | in-page: budget 100 -> 200 moved rings 3 -> 7; starting cords 20 -> 60 moved splits 1 -> 2. |
| random seed | produces a new object at the same ring count, per G4b. |

## Two instruments that lied, both reading as bad news
- A frustum check I wrote reported the object was **not in view** while it was
  being drawn the whole time; the camera matrices it read were stale. A
  screenshot settled it in one step. I had almost gone looking for a bug in
  `fit()` on the strength of it.
- Mid-build screenshots taken inside a single batch came back **identical**,
  which looked like the reveal was fake. The blob timestamps were 1ms apart:
  the batch captured both frames at the end rather than between the steps.
  Separate calls show the two states correctly.
Both of these point the same way as the NaN-SVG in round one: the failure mode
to plan for is the instrument quietly agreeing with you.

## Still not measured
Whether these are the maker's rules. R10 is now the load-bearing claim — that
rings appear because a band outgrows the ring that it left. It is forced by R9,
which is arithmetic on R2-R4, so the *mechanism* is sound. Whether the maker
gathered at that threshold, or simply gathered when the work felt too wide to
hold, no photograph can tell me.


---

# Third round — going back to the photographs

The first thing I should have done, done last. I had never magnified the source
images; I recognised cord, wooden rings and fringe, named it macrame from
memory, and built two engines and a viewer on top of that naming. Crops are in
`evidence/`.

| check | result |
|---|---|
| square knots present? | **NO.** Looked at 4 regions across both photos at 3-5x. A square knot cannot hide its filler pair, and there is no such structure anywhere. |
| what is there instead | a chain of loops — bight pulled through bight. `p1_chain_tight.jpg` shows it in rope with no ambiguity. |
| rings lark's-head mounted? | **NO.** All three rings are empty inside and held at a single point (`p2_lowleftring.jpg`, `p1_topring.jpg`, `p2_rightring.jpg`). No collar of mounted cord on any ring in either photograph. |
| colour mechanism | strict per-stitch alternation of two carried strands (`p2_colour_raw.jpg`), not a mount-time period over many cords. |

## What this costs
Rules R1, R2, R3, R4, R5, R7, R9 and R10 across v1 and v2 are refuted. The
measured results in rounds one and two are all still *true of the generator* —
the solver really is 13.7x faster, ring count really is downstream of the
budget, `--no-alternate` really does change the geometry. They were just
measurements of the wrong system. Every control I ran tested whether the code
did what I said; none of them could ever have tested whether the rules were the
object's rules. That is the gap, and it was open for three rounds.

The one thing that did close it was the user telling me to go and look.

## Failure shape
**Recognising a material is not identifying a structure.** Cord plus wooden
rings plus fringe reads as "macrame", and macrame supplies a confident
vocabulary — square knot, lark's head, sinnet, picot — that will generate
plausible rules indefinitely without ever touching the evidence. The two are
close enough that the substitution is invisible from the inside: everything I
built was internally consistent and well tested. The tell I ignored was that I
had never once looked at the source at magnification, while reporting
confidences as high as "high" on what the source contained.

---

# Fourth round — the loopwork engine (RULES.md v3)

First engine built on what the photographs actually show. Predictions in
PREDICTIONS.md (earlier rounds restored to PREDICTIONS-ARCHIVE.md after I
overwrote them — the rotation was botched and then repaired).

| # | prediction | result |
|---|---|---|
| N1 | CONTROL: policy=chain gives joins 0 and a high aspect | **joins 0 — PASS. Aspect — FAILED AS WRITTEN.** A pure chain comes out aspect 1.22, not elongated. The prediction was wrong, not the code: an unjoined chain is a *random walk*, which is isotropic in shape while still being topologically a path. Aspect cannot answer "is this a fabric". The aggregate that can is density: at 420 stitches, chain occupies 5,618 bbox units vs window's 47 and random's 9 — **13.4 vs 0.111 vs 0.022 units per stitch**, a 120x to 600x spread. Cycles say the same thing exactly: 0 vs 158. Aspect reading withdrawn. |
| N2 | CONTROL: join_rate=0 gives joins 0 under every policy | **PASS** — 0 for all five. |
| N3 | ring_every=0 gives rings 0 and moves the geometry | **PASS, but weakly.** Rings 5 -> 0, and the bbox moves only in z, 2.844 -> 2.655 (6.6%); x and y move under 0.2%. `ring_weight` is close to inert at the current gravity, which is itself deliberately tiny. It is a knob with very little authority and I am flagging it rather than quietly keeping it. Rings still matter structurally — they are threaded on the cord path regardless of weight. |
| N4 | L2 is presentational | **PASS** — strands='K' recolours every stitch and leaves the positions bit-identical. |
| N5 | the policies mean what they say | **PASS** — distance back over the joins each makes: ladder 12.9 (sd 1.0, max 13 — exactly the period, the sd is early stitches clamping at 0); window 13.2 (sd 7.3, max 26 — exactly the window); random 103.6 (sd 91.8, max 373); nearest 23.8 but unbounded in index. **Spatially**, at selection time: nearest 0.23 mean / 0.51 max, the tightest of all, against random's 0.63. Each policy does the thing its name claims. |
| N6 | seeds vary form, not counts | **PART FAILED.** Rings are identical across seeds (5 and 5 — ring capture is deterministic, every Nth stitch). Joins are **not**: 155 vs 141, because L3 fires on a probability per stitch. I wrote the prediction as if all counts were deterministic. Only the deterministic ones are. |

## An instrument that was defeated by the thing it measured
My first N5 run measured the spatial distance between a join and its target
*after* relaxation, and got 0.22-0.26 for every policy including random — i.e.
no discrimination at all. The link spring pulls every linked pair to the same
rest length by construction, so that measurement could only ever return the
rest length. It is the same error class as the NaN-SVG and the stale frustum:
an instrument that returns a clean, plausible number while measuring nothing.
Re-measured at selection time, before the solver touches it, the policies
separate cleanly.

## Viewer
Live generation 0.26-0.48s round trip. The build animation reveals in the
generator's own order — stitch by stitch, indexed by the stitch that made each
triangle — and drawn vertices rise 360 -> 155,910 monotonically across the
build, stitch 0 to stitch 420. Rings scale in at the stitch that captured them.

## What is now established, and what is not
Established: this engine implements L1-L7, the L3 policies are distinguishable
and mean what they claim, and ring capture, colour and gauge behave as the
rules say. None of that is evidence that these are the maker's rules. The
photographs establish the *vocabulary* — chain stitch, two carried strands,
rings captured on the path, tails from spent strands. They do not establish the
*policy*: which older loop he passes through, and how often. That is exactly
what the switch is for, and it is still the open question.


---

# Fifth round — L8, self-termination with unlimited cord

The question was what finishes a generation. The honest answer for the previous
engine was **nothing**: `stitches` was a loop bound I picked. L8 replaces it.
Predictions in PREDICTIONS.md.

| # | prediction | result |
|---|---|---|
| T1 | every policy ends "enclosed" | **FAILED.** `ladder` 372, `window` 727, `random` 1439 all enclose. `chain` and `nearest`-at-high-wander hit the safety bound with 0 and 5 joins. The prediction was wrong: **L8 only terminates work that folds back on itself.** Work that travels outward never meets its own fabric and runs forever. This is now stated as a limit of the rule rather than hidden. |
| T2 | size is emergent | **PASS** — 8 seeds at fixed parameters: 499, 848, 182, 354, 314, 425, 727, 1031. A 5.7x spread. |
| T3 | capacity up -> larger, monotonically | **PASS above 2, FAILED at 1 and above 5.** capacity 1 runs away (every loop fills instantly, joins are always refused, so it degenerates to a pure chain); 2 -> 198, 3 -> 727, 5 -> 1444, 8 -> 1444 identical because occupancy never exceeds 3, so capacity stops binding. |
| T4 | wander up -> larger | **PASS** — 0.3 -> 30, 0.75 -> 727, 1.3 and 2.0 -> safety bound. |
| T5 | CONTROL: no clearance, huge capacity -> must hit the safety bound | **PASS** — 2600, safety_bound. With nothing able to refuse the act, nothing stops it. L8 is what causes termination. |
| T6 | join_rate up -> smaller | **PASS in direction, not monotonic** — 0.0 runs away, 0.2 -> 1224, 0.4 -> 137, 0.7 -> 217. |

## The finding that matters most
**Final size is chaotic in the parameters.** Holding the seed and everything
else fixed and moving `clearance` alone: 0.66 -> 77, 0.70 -> 206, 0.71 -> 1372,
0.72 -> 727, 0.73 -> 381, 0.80 -> 197. Deterministic, reproducible, and not
predictable — a 0.01 change swings the result 20x, non-monotonically. These are
not size dials and must not be presented as any. If you want a size, you sample
seeds and keep what you like.

This was found by accident: the viewer produced 381 stitches where the CLI gave
727 on nominally identical settings. The cause was mundane — the clearance
slider's step grid (min 0.05, step 0.02) could not represent 0.72, so the
browser silently snapped it to 0.73. Fixed by changing the step. But chasing a
two-fold discrepancy is what exposed the sensitivity, which is a real property
of the system and not a bug.

## Ending is now reported, never assumed
`stats.ended` is `enclosed` or `safety_bound`, and the viewer says in words
which happened. A run that hit the bound did not finish and is not shown as if
it had.


## The act happens at the edge, and that is what makes it a mass
With L8's free-site test in place, the first self-terminating runs came out as
long ropes — bbox 19 x 4 x 48, aspect 11.2. I assumed gravity was hanging the
work and was about to tune it. Measured first: **aspect 11.03 at gravity
exactly zero.** The hypothesis was wrong and the cause was the growth, not the
relaxation. Avoiding your own fabric and nothing else is a self-avoiding walk,
and self-avoiding walks travel.

What the photographs say against that is simple and I had not used it: the piece
is *one mass*. So the act is performed against the work already made. Of the
free sites tried, take the one most in contact with existing fabric.

| contact radius | stitches | aspect | bbox |
|---|---|---|---|
| 0 (off) | 727 | 11.20 | 19.3 x 4.3 x 48.2 |
| 1.2 | 50 | 1.44 | 1.0 x 1.4 x 1.5 |
| 1.9 | 106 | 1.52 | 2.1 x 1.4 x 1.6 |
| 2.6 | 80 | 1.42 | 1.7 x 1.2 x 1.4 |

Growth changes from a travelling walk to surface accretion, and the form becomes
compact. It also makes termination routine rather than lucky: at the defaults,
**10 of 10 seeds self-terminate**, 48 to 170 stitches, median 116, aspect at
most 2.13. Size stays emergent and still chaotic in the parameters.


---

# Sixth round — why the self-terminating pieces are SMALL

Asked why the "potentially infinite" rule produces smaller objects than the
fixed-length engine did. Prediction written first: if termination is genuine
enclosure, size converges as the hand tries harder; if it is a search artifact,
size climbs with `tries`.

**It climbed**: tries 10/20/30/60/120/240/480 -> 24/161/167/131/320/468/865
stitches. No convergence. So the original termination was substantially an
artifact of how hard the search looked, not a property of the fabric.

Direct measurement at the moment of stopping, sampling 4000 directions where
the hand samples 30:

| | |
|---|---|
| free directions around the tip | **16.4% of the sphere** |
| median angle of those from the hand's heading | **105 degrees** — i.e. behind it |
| fraction within 60 degrees of the heading | 4.7% |
| free fraction inside the cone the hand searched | **0.1%** |
| loops still under capacity | 154 of 167 |

The work was stopping because the free space was *behind* it and it only looked
forward. Fixed with `turn`: a fraction of the tries sample the whole sphere
instead of a cone, because cord is flexible and the work can be turned.

I predicted this would make pieces substantially larger. **It did not** — sizes
at turn 0/0.25/0.5/0.75 are 167/223/134/127, and the tries-sensitivity remains
(134, 997, 186, 2600 at tries 30/60/120/240). What it did fix is whether the
ending is real: free directions at the tip at termination fall from **17.7% at
turn=0 to 0.0% at turn=0.5**. The ending is now genuine rather than a failure
to look.

## So why are they small
Because **the working tip traps itself long before the fabric fills.** At
termination ~92% of loops still have capacity and thousands of free sites sit
adjacent to them. A tip doing a self-avoiding walk through a mass it is itself
building gets walled in after a few hundred steps, no matter how much room the
object has elsewhere. The old engine's 420 was not a competing measurement of
anything — it was a number I typed.

Two different stopping conditions are available and they differ by orders of
magnitude:
- **tip trapped** (what is implemented): hundreds of stitches. Physical only for
  a maker who will not move the work.
- **fabric saturated** (not implemented): for a blob growing by accretion the
  surface goes as N^(2/3), so there is essentially always somewhere to work.
  This is the genuinely unbounded regime.

The craft is the second: you pull the working loop round to wherever there is
room. Implementing that means letting the working loop relocate to any open
loop with a free site when the tip is stuck, and stopping only when no open
loop anywhere has one.


---

# Seventh round — the carry, and the disappearance of the stopping condition

Change requested: when the tip is stuck, relocate the working loop to any open
loop with a free site, and stop only when none exists anywhere.

Implemented with a monotone optimisation: space only ever fills, so a loop that
fails a full `probes`-direction scan is written off permanently. That bounds the
total search to one thorough scan per loop.

| question | answer |
|---|---|
| does the work still stop? | **Almost never.** Across 8 settings — defaults, huge clearance, no contact, few probes, join-everything, nearest, chain-only — all ran to the budget. Only `loop_capacity=1` ever reached "saturated". |
| why | the surface of a growing mass outruns the filling of it. There is always somewhere left to work. |
| size now | 2200 stitches at the default budget against ~170 before, and compact: aspect 1.09, bbox 3.9 x 3.9 x 4.2, with 63 carries and 31 rings embedded. |
| is "saturated" trustworthy when it does fire? | **Only loosely.** In the `loop_capacity=1` case, `probes` 6/20/40/80/160 gives 242/333/249/574/507 stitches — no convergence. Saturation there is driven by capacity exhaustion, not by the direction scan, but the size it lands on is as chaotic as everything else in this system. |

## The result is that the stopping condition went away
Making L8 faithful to the craft removed it. That is the honest finding and it is
what the rules say once the artifact is taken out: **the rules do not end the
piece, the maker does.** `max_stitches` is now described everywhere as a budget
you choose, not a safety bound and not a rule, and `stats.ended` reports
`your budget` or `fabric saturated` so the two can never be confused again.

This is the third time in this project that a quantity I had treated as
determined turned out to be chosen. Ring count was the first, length the second,
and now length again on the far side of a mechanism that looked like it would
settle it.

## Performance
The relocation scan made growth 19.4s. Two fixes, both measured: a coarse second
grid for the contact ranking (343 cells per query down to 27), and replacing
`np.add.at` with `bincount` in the solver. Growth 19.4s -> 0.5s at 1500
stitches; full build 1.2s at 1500, 2.3s at 2500, 4.3s at 4000.


---

# Eighth round — endless cord, scale, and conveying volume

## Endless cord
`strand_runs_out` now defaults to 0: the cord never runs out, so the only tails
are at the very end. Consequence to be aware of — the source's dense fringe is a
by-product of *spent strands*, so switching it off makes the object less like
the source in exactly that respect. Set it to a few hundred to get a sparse
fringe back on a large piece.

## The scaling law, which is the real answer to "enormous"
A mass grows as the **cube root** of the work. Measured at 8 mm cord:

| stitches | size |
|---|---|
| 500 | 19 x 24 x 19 cm |
| 2,000 | 31 x 30 x 33 cm |
| 8,000 | 43 x 48 x 40 cm |

16x the work buys 2.2x the size. Reaching 2 m by stitch count alone would take
on the order of 700,000 stitches. **Gauge is the lever, not stitch count**: the
same 2,400 stitches at 26 mm rope is 100 x 109 x 114 cm, which is also how the
source's chunky roving reads so much bigger than its cotton at the same effort.
`cord_mm` is what ties the model to the world — everything else is measured in
cord diameters.

## Conveying spatiality
Four cues, in rough order of how much they do here:

1. **Measured occlusion, baked per vertex.** Not a lighting trick: for each
   stitch, count the neighbours within ~3 loop-lengths and rank-normalise. A
   buried stitch gets dark, a surface stitch stays light. Verified against the
   structure rather than by eye — mean shade of the innermost 15% of stitches is
   **0.40** against **0.92** for the outermost 15%. CONTROL: toggling it off
   visibly flattens the mass, so the vertex colours are doing the work and not
   the lighting.
2. **Cast shadow and a floor.** Grounds the object and gives it a place.
3. **Linear fog placed across the object** (near = d - 0.85r, far = d + 2.6r) so
   the near face stays fully lit and only the far side recedes. The first
   attempt used exponential fog and washed the entire mass into the background —
   a cue that destroys the thing it was meant to describe.
4. **A 10 cm floor grid and a size readout in centimetres.** Scale you can read
   without leaving the frame, which is what "enormous" actually needs.

All three rendering cues are on toggles, so each one's contribution can be seen
rather than asserted. The occlusion is also baked into the OBJ as vertex colours
(`v x y z r g b`, which Blender and MeshLab read) and into the SVG preview, so
the depth survives export.

## Performance
Occlusion on plain floats rather than numpy scalars: 1.07s -> 0.15s at 3,000
stitches. Solver iterations halved to 160 after measuring where the gain
plateaus (mean displacement still 4x the stitch pitch, aspect still rounds from
1.31 to 1.15). Build is now ~1.4s at 2,400 stitches and ~3s at 5,000. Growth
scales linearly; the solver does not, so very large pieces belong on the CLI.


---

# Ninth round — cord realism, depth of field, and a fidelity audit

## Two things in the render were not cord
1. **The cord passed through itself.** Consecutive bights were near-coplanar and
   separated by 0.085 against a cord diameter of 0.100 — so every loop
   intersected its neighbour. Found by arithmetic on the parameters, not by eye.
   Fixed by rotating each bight's plane 90 degrees about the chain axis, so
   consecutive loops thread through one another the way links do.
2. **Heavy gauge was scattered as single stitches** through a fine chain, which
   no cord does. Now worked in contiguous runs (14 stitches every 120, ~10% of
   the piece), which is how you pick up rope and use it for a while.

Tube cross-sections raised from 5 and 6 sides to 9: a 5-sided tube is visibly a
prism, not a cord.

## Depth of field
`BokehPass` with focus tracking the orbit target every frame. CONTROL: toggled
off, the distant fringe is uniformly sharp; on, it softens while the near cord
stays crisp. The toggle changes the image, so the pass is doing the work.

## Fidelity audit
Full table in FIDELITY.md. Summary: the rules were intact, two rates had drifted
(`ring_every` 70 against a source-implied 130; `strand_runs_out` 0 against a
source-implied 14), and one rule was silently unrepresented (`heavy_every=0`
meant L5's second gauge did not exist). All three corrected.

The strand estimate has an independent check that makes it non-circular: 14
stitches at 8.5 cm of cord per stitch is a **1.2 m working length**, which is a
plausible length to cut. Nothing forced that number to come out sane.

At the corrected defaults, 420 stitches gives 21.7 x 21.4 x 15.6 cm, 3 rings,
60 tail ends and 10% roving — against a source of ~20 cm, 3 rings, ~50-60 tails
and a minority of roving. Four measurable features, four matches.


---

# Tenth round — the form unfolding through its real configurations

Asked whether the overall form can unfold and twist to show its configurations
as it progresses. It could not: the animation revealed a *prefix of the final
positions*, so nothing ever moved. That was a quiet dishonesty in the thing most
likely to be believed — a build animation that shows no building.

## What changed
Settling is now interleaved with growth: every 25 stitches the solver runs 7
iterations over the work so far, the spatial index is rebuilt, and the next
stitch is placed against the settled fabric. 28 configurations are recorded and
sent as offsets from the final one.

## CONTROL: does the form actually move, or is it still a prefix?
Mean distance from the final configuration, measured in the engine:

| keyframe | mean distance from final |
|---|---|
| 42 stitches | 0.781 units = **3.2 stitch pitches** |
| 252 | 0.661 |
| 462 | 0.639 |
| 882 | 0.396 |
| final | **exactly 0** |

Monotone convergence, and the last keyframe is identically zero — so the
animation ends on the real object rather than near it.

In the browser, mean displacement of drawn vertices: **1.27 units with unfold
on, exactly 0.000 with it off**, at four different moments. The toggle is a real
control and the shader path is doing the work.

## An instrument that answered the wrong question
My first control compared the *bounding box* of drawn geometry with unfolding on
and off and found a 7% difference — which nearly had me conclude the effect was
marginal. A mass can writhe substantially while its extent barely changes; bbox
measures extent, and the question was displacement. Re-measured per vertex, the
effect is 5 stitch pitches. Third time in this project that an aggregate has
been asked a question it cannot answer.

## Implementation notes
The unfolding runs on the GPU: two keyframe offsets per vertex and one mix
uniform, injected into `MeshStandardMaterial` via `onBeforeCompile`. Only the
28 keyframe crossings touch CPU memory, and each bight is carried rigidly so
loop shape and normals stay correct. The camera now frames the whole excursion
rather than just the final form, because early configurations otherwise fall
out of shot. Responses are gzipped; 1.79 MB of keyframes at 2,200 stitches
compresses well enough to stay interactive.


---

# Eleventh round — the bights turn as well as travel

The unfolding carried each bight rigidly by its stitch's displacement but did
not rotate it, so at the scale of a single loop the motion was stiff.

## Done without enlarging the payload
The keyframe centres are already sent. The chain direction at a stitch follows
from its neighbours' centres, so the viewer derives it rather than being told.
Each bight is then rotated by the **minimal rotation** between its final chain
direction and the one it had at that moment. Minimal rotation, not a rebuilt
frame: it invents no twist, needs none of the generator's up-vector or parity
logic in the browser, and is exactly the identity at the final keyframe.

| control | result |
|---|---|
| final keyframe is exactly identity | **max offset 0.000000** — the animation lands on the object, not near it |
| rotation contributes beyond translation | mean rotational spread across a bight **0.0524 units = 25% of the bight's own half-length**, against a mean translation of 0.358 |
| the fast path matches the slow one | after hoisting the quaternion per stitch, both numbers are **bit-identical** to the naive version |

## An instrument defeated by its own sampling
My first attempt at the rotation control sampled the first 40 vertices of each
bight and reported a spread of 0.0156 — small enough that I nearly concluded
rotation barely mattered. Those 40 vertices are all from one short arc of the
loop, where a rotation about the loop's centre barely separates them. Sampled
across the whole bight instead, the figure is 0.0524, more than three times
larger. The reading was not wrong about the vertices it looked at; it was wrong
about which vertices to look at.

## Performance
The quaternion was being rebuilt per *vertex*. Hoisted to per stitch, with raw
typed-array access instead of attribute accessors: keyframe crossings went from
17-87 ms to **7.5-22 ms**. Frame rate during playback was not measured — the
browser pane was hidden at the time, which throttles the frame callback, and a
number taken then would have been meaningless.


---

# Twelfth round — frame rate: NOT MEASURED, and why

Asked to show the browser pane and measure fps. **Neither was possible from
here, and no number is reported.**

## Why the pane could not be shown
`get_layout` reports this session is not open in any window
(`{"views":[],"open_panes":[]}`), and the pane tool has no browser pane to
show. Fronting the tab succeeded but the pane stayed hidden, because the pane
is hidden at the application level, not the tab level.

## Three measurements, all withdrawn
| attempt | reported | why it was fiction |
|---|---|---|
| `setInterval(…,0)` counting ticks | "7 fps" | counts timer callbacks, not frames. Never was a frame rate. |
| `requestAnimationFrame` counting | "0 fps" | rAF is throttled to nothing while the page is hidden |
| timing `composer.render()` directly | "0.1 ms, 10000 fps" | WebGL calls queue asynchronously, so this times command submission, not drawing — and a hidden page does not draw at all |

The third is the instructive one: it returned a precise, confident, plausible
number from a canvas that rendered nothing.

## What the state actually is
Verified while hidden, with checks that do not need rendering:

    document.visibilityState  "hidden"
    context lost              false
    geometry                  898,344 vertices, all inside the draw range
    renderer.info.triangles   1        <- nothing was drawn

So the scene is intact and healthy; the browser simply does not render a hidden
page. This is the "enumerate the meanings of nothing" case exactly: *the thing
is broken*, *the thing is idle*, and *the observer never ran* render
identically as a near-zero number, and only the last one is true here.

## Correction to the eleventh round
The keyframe-crossing figure of 7.5-22 ms stands, but it measures the
**JavaScript** work only — typed-array maths and flagging the attributes dirty.
The GPU upload of those attributes happens at the next draw, which never
occurred. The real crossing cost is that figure plus an upload of ~10.8 MB of
attribute data, which has not been measured.

## What would settle it
The session open in a window with the Browser pane visible, then rAF frame
counting over a few seconds at a known canvas size, with and without the DoF
pass. Roughly 299,000 triangles of cord at 1200 stitches, canvas 1104x1622.


---

# Thirteenth round — frame rate, measured properly; and depth of field withdrawn

## Frame rate
Pane visible, `requestAnimationFrame` counting over 2.5 s, 304,634 triangles of
cord, canvas 1416 x 1622 at devicePixelRatio 2:

| | fps |
|---|---|
| with depth of field | **119.9** |
| without | **120.0** |

Both are pinned to the display's 120 Hz vsync cap, so these are a **floor**, not
a measure of headroom — the renderer is not the bottleneck and the cost of the
DoF pass is below the frame budget. I am not reporting headroom because vsync
makes it unmeasurable this way.

Frame times across a whole build, which is where the keyframe crossings land:

    frames 720   median 8.3 ms   p90 8.5   p99 12.6   worst 14.1
    frames over 16 ms: 0        frames over 33 ms: 0

So the crossings cost no dropped frames at all. The hitch I predicted in the
eleventh round does not occur; that prediction is withdrawn.

## Depth of field is now OFF by default
It was wrong for this subject and the reason is arithmetic, not taste:
`maxblur` 0.012 of a 1416 px canvas is **~17 px of blur**, applied to cord that
is only a few pixels across. The effect does not describe depth, it erases the
cord — the one thing several rounds of work went into getting right.

More fundamentally, depth of field is a property of a *camera*, not of an
object. A 25 cm piece seen whole sits entirely within the depth of field of any
ordinary lens or of the eye, so blurring parts of it reads as a rendering fault.
It stays as a toggle with `maxblur` reduced to 0.004 and a lower default
aperture, for a deliberately photographic look on a large piece, where it is
defensible. Off by default.

This also brings it back in line with the standing instruction that anything
making the cord less realistic should be removed.

## Framing corrected
The camera was fitted using the **largest single** keyframe excursion, which is
an outlier, and it pushed the camera to 24.8 units so the object sat small in
frame. Now the 90th percentile, capped at half the object's own radius: camera
distance 19.0, and the piece fills the shot.


---

# Fourteenth round — the motion shows the act, not just the result

The build animation revealed stitches in order and let the form settle, but it
did not show *making*. Two reasons, both measurable:

1. **Pace.** 55 stitches per second at speed 1, 82 at the default. An act that
   takes 12 ms cannot be seen. Base rate cut to 10/s, default speed 3, so
   roughly 30 stitches a second — about 4 frames per stitch at 120 Hz.
2. **Stitches arrived finished.** A bight appeared at full size in its final
   place. Nothing was ever pulled through anything.

## The act, drawn
Each stitch now starts as a small loop collapsed at the loop it is being pulled
**through** — the server sends that target per stitch, which the rules already
knew — and is drawn out to its own place at full size on a smoothstep. The
loop's own geometry is reused and only scaled and carried, so no new shape is
invented for the animation.

| control | result |
|---|---|
| at the start of formation the bight sits at its target | deviation **0.374 units = 1.55 stitch pitches** from its finished place |
| mid-formation it is between | 0.215 |
| at the end it is the finished stitch | **exactly 0.0000** — bit-identical to the pristine geometry |
| stitches behind the working point are untouched | **exactly 0.000000** at stitch 100 while working at stitch 300 |

The last two matter most: the animation lands exactly on the real object, and
the act is local — it disturbs nothing already made.

## Cost
Only the forming stitch's vertices are rewritten, about 650 of 898,344, and
only that slice is uploaded. `updateRange` is getter-only in three r160, so the
partial upload goes through `addUpdateRange()` with a fallback for older
versions; without that the whole 10.8 MB buffer would re-upload every frame.
Frame timing was **not measured** for this round — the browser pane was hidden
again by the time I got to it, and a number taken then would mean nothing.


---

# Fifteenth round — frame rate, measured with the pane visible

## Results
Canvas 1416 x 1622 at devicePixelRatio 2, display caps at 120 Hz. Triangle
counts are computed from the geometry's draw ranges, not from the renderer's
counter (see below).

| load | triangles | fps, no DoF | fps, with DoF |
|---|---|---|---|
| 1,200 stitches | 299,448 | **120.4** | **119.6** |
| 2,400 stitches | ~611,000 | **120.1** | — |
| 3,000 stitches | 755,334 | **95.4** | **77.5** |

So it holds the 120 Hz cap to roughly 600,000 triangles and falls to ~95 fps at
755,000. Depth of field costs nothing measurable while capped, and about 19% of
the frame rate once the scene is heavy enough to matter.

During playback, where each stitch's vertices are rewritten and uploaded:

    599 frames   median 8.3 ms   p99 9.4   worst 12.9
    frames over 16 ms: 0

The per-stitch formation work costs no dropped frames at all. The partial
upload is doing its job; a full-buffer upload would be 10.8 MB a frame.

## An instrument I could not explain, and stopped trusting
`renderer.info.render.triangles` began reporting **2** for a scene that a
screenshot plainly showed fully drawn, with 2,266,002 vertices inside the draw
ranges, no GL errors, no context loss, materials compiled, and every mesh
correctly rooted in the scene graph. Disabling frustum culling changed nothing;
an explicit `info.reset()` changed nothing.

I could not account for it. Most likely driving the renderer by hand alongside
the running animation loop desynchronised the counter, since `EffectComposer`
manages `info` resets itself — but I did not establish that, and I am not going
to assert it.

What matters is that it was the wrong instrument either way. The frame rates
above come from counting frames, which is independent of it, and the triangle
counts from summing draw ranges, which is also independent of it. **Every
triangle count previously quoted from `renderer.info` in this document should be
read as unverified**; the two that can be checked against draw ranges (299,448
against a reported 304,634 at 1,200 stitches) agree to within 2%.

The sequence is the familiar one: the counter returned a clean, specific,
plausible number — and this time its being obviously absurd is the only reason
I noticed.


---

# Sixteenth round — rhythm from the rules, and the carry as a gesture

## Rhythm
A hand is not a metronome, but rather than sprinkle noise on the playback the
timing is read off the rules. Each stitch gets ordinary unevenness, and the
pauses land on the things the rules say are events: threading a ring (L4),
joining a new strand when one runs out (L6), carrying the work to another open
loop (L8).

Measured over a 1,200-stitch piece:

| | |
|---|---|
| ordinary stitches | 1,026, duration 0.72 to 1.28, mean 1.00 |
| event stitches | 174, mean duration **3.70** |
| of which | 86 strand changes, 85 carries, 9 rings |

So about one stitch in seven is a pause, and the pauses take roughly 39% of the
build. That is not a stylistic choice: at `strand_runs_out` 14 the source itself
implies a pause every fourteen stitches.

## The carry, drawn
The float used to appear whole. Now the cord travels along its own path:
vertices past the frontier are held at the frontier, so it extends rather than
pops. On a carry stitch the work travels for the first 55% of the stitch's time
and the bight is made in the remaining 45% — the two halves of the actual
gesture.

| fraction through the carry | how far the cord has reached |
|---|---|
| 0.00 | 0.104 |
| 0.25 | 0.142 |
| 0.50 | 0.202 |
| 0.75 | 0.272 |
| 1.00 | **0.309** = its full length, exactly |
| after restore | deviation **0.000000** |

Monotone, lands exactly on the finished float, and leaves nothing behind. The
0.104 at fraction zero is the tube's own radius at its origin, not an error.

## A control that tested nothing
My first attempt at the table above looped over fractions calling `d.drawCarry`
— which was not exposed on the debug handle, so the call was `undefined` and did
nothing. Every row came back 0.3094, the full length, which I could have read as
"the carry is already fully drawn at every fraction" and concluded the feature
was broken. It was the identical-rows pattern, not suspicion of the instrument,
that made me look. Exposing the function and re-running gave the numbers above.


---

# Seventeenth round — handling the finished piece

Unfolding moved off the growth and onto the finished object. The keyframes are
gone (and with them ~85 KB to ~1.8 MB of payload); in their place the server
sends the **topology and the solver's own constants**, so the browser can move
the piece the way the generator would rather than inventing a second physics.

Per-stitch transforms now live in a texture read by the vertex shader, so
re-posing the whole piece costs n x 8 floats a frame instead of rewriting
900,000 vertices. That is what makes it interactive at all.

## CONTROL: does the browser solver agree with the generator's?
Switch handling on, touch nothing, and the piece should behave as the Python
solver would. It drifted — mean 1.315, max 3.014 units over 2.5 s. Rather than
assume my port was wrong, I ran the **Python** solver on from the same finished
state:

| | mean | max |
|---|---|---|
| Python, 600 further iterations | 1.3388 | 3.0038 |
| browser, 2.5 s of handling | 1.3152 | 3.0142 |

Within 2% on the mean and 0.3% on the max. Two independent implementations on
the same trajectory: the port is right, and **the object was never at
equilibrium**.

## The model has no static equilibrium
Continuing to solve, in Python, from the finished state:

    with gravity:  bbox z 3.26 -> 5.69 and still growing at 3,000 iterations
    without:       per-block motion sits at ~0.25 indefinitely, never decaying

The chain springs are extensible, so sustained gravity makes the piece creep
without limit — real cord does not. And even at zero gravity the tangle keeps
micro-rearranging rather than coming to rest. Both are properties of the model
that 160 iterations of generation were hiding.

Consequences, all of them deliberate:
- handling defaults to **no gravity** — the piece is in your hands, not hung.
  A slider hangs it if you want to watch it drape, with the creep that implies.
- handling damps harder than generation (0.55 against 0.80), so it calms.
- it still settles when you first pick it up: about 2.5 stitch pitches over ten
  seconds, decelerating. That is the object relaxing, not a bug, and Reset
  returns it exactly.

## Other controls
| check | result |
|---|---|
| a pull is strongest where you grab | mean displacement 1.156 near the grab, 0.915 mid, 0.737 far |
| Reset restores the made object | deviation **exactly 0.000000** with handling paused |
| hanging ends do not swing | tails take their stitch's translation but not its rotation; without that they splayed, which the first screenshot showed plainly |

## Two instruments that lied again
- The first agreement test reported drift of **exactly 0**, which I read as
  "not running" rather than "perfectly stable" — correctly, as it turned out:
  the server was stale and `handling` was undefined.
- The first pull test reported `farFromIt: 0` from a sample of **0 stitches**:
  nothing in a 3-unit object lies more than 3 units from anything. A mean over
  an empty set rendered as a confident zero.


---

# Eighteenth round — verifying the drag with actual pointer events

The handling solver had only ever been tested by setting the pin
programmatically. That proves the physics, not the interaction. Driving real
`PointerEvent`s at the canvas instead:

| check | result |
|---|---|
| a click picks the stitch under the cursor | `pickStitch(440,376)` returns 889, the stitch nearest that point |
| dragging moves it | grabbed stitch 887 travelled **4.164 units** (~17 stitch pitches) following the cursor |
| the piece responds | mean deformation **0.425** across all 1,200 stitches |
| the camera does not fight the drag | orbit camera moved **0.0000** during the drag; controls restored on release |
| plain release lets go | the pin is dropped |
| shift-release keeps it | the grabbed stitch stays pinned, and with gravity on the rest drapes from it |

A marker now shows what is being held, because without one you cannot tell
what you grabbed.

## Two false negatives in my own test, both from looking in the wrong place
- The first attempt searched for a stitch within NDC |x|,|y| < 0.25 and found
  none, so it clicked at (0,0) — over the UI panel. The object sits at NDC x
  0.22 to 0.65 because the camera is offset to clear the panel. The test
  reported no movement, which I could have read as "dragging is broken".
- The second recorded which stitches were pinned **immediately after
  pointerdown**, but pointerdown only sets the grab; the pin appears on the
  first move. It duly reported the grabbed stitch as 0 and its movement as 0.

In both cases the interaction was working and the measurement was pointed
somewhere else.


---

# Nineteenth round — the drag did not work for the user, and why

Reported as not working. Two causes, both real, neither visible in my own tests
because my tests called the handlers directly rather than going through the
browser's event path.

1. **It was behind a mode.** Nothing happened unless you first found and pressed
   "Handle it". That is not a bug in the code and it is a bug in the thing.
2. **OrbitControls saw the gesture first.** It attaches its `pointerdown` to the
   same canvas and was constructed earlier, so in the bubble phase it ran first
   and began an orbit. My handler then set `controls.enabled=false` mid-gesture,
   which is a race, not a fix.

## The fix
The grab handler is now registered in the **capture phase**, so it runs before
OrbitControls, and calls `stopPropagation()` when the click lands on cord — the
camera never sees it. If the click lands on empty space the handler does
nothing and the orbit works as before. Handling enables itself on the first
grab, so there is no mode to find. Pick radius widened from 48 to 70 px.

| check | result |
|---|---|
| handling is off until you grab | `handleOn` false, then **true** on pointerdown over cord |
| grabbing the cord moves it | stitch 870 travelled **3.82 units** following the cursor |
| the camera stays put while dragging cord | **0.0000** |
| dragging empty background orbits instead | camera moved **11.25**, **0** pins added |
| `pickStitch` agrees with what is drawn | scanning the canvas, it reports hits over x 380-660, y 180-480, which is where the object actually appears |

## My own test was the thing that hid it
Every earlier check dispatched synthetic events or set `pinned` directly. Both
bypass exactly the part that was broken — listener ordering and pointer capture
— so the feature tested green while being unusable. A synthetic
`PointerEvent` is not a pointer; it is a convenient fiction that happens to
exercise my code and not the browser's.


---

# Twentieth round — the jiggle, and a verification I could not complete

Reported: pressing Handling makes the whole piece jiggle on its own. That is a
defect, not a trade-off. The cause was already measured in the seventeenth
round and I left it in place: **this model has no static equilibrium**, so a
solver left running makes the object micro-rearrange for ever. Motion the
object does not have.

## The fix
The solver now sleeps. It runs only while you are dragging, for a short settling
window after you let go, and after a slider change — and it sleeps early once
the largest velocity falls below 1e-4 rather than merely running out of frames.
Enabling Handling explicitly sets the wake counter to zero, so pressing the
button does nothing at all until you touch the piece.

## NOT VERIFIED
I could not confirm any of this. The browser pane went hidden partway through,
which stops `requestAnimationFrame`, which stops the animation loop, which is
what runs the solver. Three readings taken after that point —

    "holds perfectly still"      max movement 0.000000
    "stops dead after settling"  creep 0.000000
    grabbed stitch moved         0.000

— are all consistent with the fix working and equally consistent with nothing
running at all, which is what was actually happening. The tell was `wake` stuck
at 180 after six seconds: the loop that decrements it had never executed.

Every one of those zeros is withdrawn. The code change is reasoned and small,
but it is unverified until the pane is visible and the drag is exercised again.
This is the fifth time in this project that a hidden pane has produced
confident zeros, and the first time I nearly reported them as a result.


---

# Twenty-first round — pulling it apart, measured with the pane visible

## The jiggle is gone
Pane visible, handling enabled, nothing touched: **max movement 0.000000** at
0.5 s, 1.5 s and 3 s, with the wake counter at 0 throughout. The sleep fix works.
(The twentieth round's identical zeros were taken from a hidden pane and proved
nothing; these are the real measurement.)

## Grabbing one stitch was the wrong gesture
A single pinned stitch draws one thread out of a tangle. The grab now takes
every stitch within a radius and moves them together — a handful rather than a
fingertip. At grip 0.75 that is **266 of 1,200 stitches**.

But a handful alone still only *carries* the piece: mean displacement 4.673
against a max of 5.724, i.e. almost everything moving together. Carrying is not
unfolding.

## Unfolding needs two hands, and that works
Shift-click anchors a handful in place; then drag another handful away.

| | mean displacement |
|---|---|
| anchored region (35 stitches) | **0.26** |
| pulled region (33 stitches) | **5.24** |
| separation | **4.98** |

The held part stays put while the other opens away from it, which is what
pulling something apart means. Both the panel text and the status line now say
so, because the gesture is not guessable.


---

# Twenty-second round — the cord now holds its bindings

The piece pulled like elastic because of three separate things, only one of
which I had named.

## 1. A bug: carry floats were claimed to be one stitch long
Every edge in the handling solver was given a nominal rest length — pitch for
chain and carry edges, `link_rest` for loops. But a **carry float spans a long
gap**, so calling it one pitch long meant it was already stretched **sevenfold
before anything was touched**, and the constraint spent itself fighting that
rather than holding the binding. Edge rest lengths are now the cord that
actually exists between those two stitches in the made object. Side effect worth
having: `madeObjectEdgeError` is now **exactly 0** — the made piece sits at rest.

## 2. The springs were soft, so cord stretched without limit
Added a position projection after each step: an edge may go slack but may not
exceed `give` x its rest length. `give` is a slider, default 1.02.

## 3. The grab teleported cord instead of pulling it
This was the real culprit. The grabbed handful was **hard-pinned to the
cursor**, so dragging commanded a separation the cord could not satisfy and
something had to give. A hand cannot do that. The handful is now drawn toward
the cursor by a finite force; hard pins are reserved for shift-anchored points,
which are your other hand holding still.

## What it does now
Anchor one end, pull the other, 1,901 edges:

| asked the grip to move | it reached |
|---|---|
| 1.0 | 0.57 |
| 3.0 | **0.58** |
| 3.5 | **0.39** (at the stiffer settings below) |

Pulling harder achieves nothing once the cord is taut, which is the behaviour
asked for. At `give` 1.30 the same pull reaches 1.31 and visibly stretches, so
the slider does what it says.

Final quality, two-handed pull, give 1.02:

    mean stretch 1.009   worst 1.077   edges over 5%: 4 of 1901
    width opens 2.65 -> 3.29

## Constraint iterations mattered far more than I assumed
| iterations | worst stretch | edges over 5% |
|---|---|---|
| 8 (the old default) | 1.402 | 105 |
| 24 | 1.15 | 20 |
| 60 | 1.056 | 1 |

Default raised to 40. The first time I ran this comparison it returned
**identical rows** for 8, 20 and 40 — because `constraintIters` was not exposed
on the debug handle, so my assignments did nothing and every run used 8. The
identical rows were the only tell; the numbers themselves looked perfectly
reasonable.

## Cost, and what is not measured
One solve step with 40 constraint passes measures **3.78 ms**, so the loop now
runs one step per frame rather than two. Frame rate while actually handling is
**not measured** — the pane went hidden again before I could count frames, and
a number taken then would be meaningless.


---

# Twenty-third round — it stays where you put it

Two further reports: still jiggling, and it should stay in the shape it is left
in. The first was partly my fault and partly real; the second exposed a physics
error.

## The jiggle I was shown was my own test state
A measurement earlier in the session had called `nudge(100000)`, leaving the
solver running for ever. That is what was on screen. Reloaded and measured with
the pane visible:

    handling OFF, untouched   max movement 0.000000 over 2 s
    handling ON,  untouched   max movement 0.000000 over 3 s

But there was a real one underneath: after a drag the piece kept moving for
about 1.5 s and then **froze because a timer expired**, not because it settled —
per-interval motion was 0.83, 0.50, 0.52 and still going when the window ran
out. Damping did not touch it (0.55, 0.30, 0.15 all behaved the same), which
ruled out momentum and pointed at a standing force.

## Two causes, both errors rather than trade-offs
1. **Repulsion was firing on the made object.** Its cutoff was a loop-length,
   and the finished piece has contacts far closer than that, so repulsion pushed
   outward while the inextensibility pulled back — a tug of war with no rest.
   The handling cutoff is now set just inside the closest contact the made
   object already has (measured: **0.0175**), so the made pose is a true rest.
2. **The springs were two-sided.** A slack edge pushed back. Cord does not do
   that: it resists being stretched and does nothing at all when slack. Springs
   are now **tension-only**, which is also why the piece would not stay put — a
   two-sided spring is a strut shoving the work back toward the shape it was
   made in.

With those, releasing freezes the solver outright rather than running a settle
window.

## Result
| after releasing the drag | movement |
|---|---|
| 0.5 s | **0.000000** |
| 1.5 s | **0.000000** |
| 3 s | **0.000000** |
| 5 s | **0.000000** |

and it is still **3.089 units** away from the made object — it kept the shape it
was pulled into rather than springing back. Reset pose restores the made object
exactly.


---

# Twenty-fourth round — what handling taught the generator

Predictions in PREDICTIONS.md (C1-C4).

## C1 — a bug: carry floats were never simulated
`solve()` took `carries` as a parameter and **never used it**. The cord a carry
lays across the piece restrained nothing; it was drawn and nothing more. Now an
edge, with its rest length recorded as the gap it was laid across at the moment
it was made. **PASS** — the geometry changes.

## C2 — the springs were struts
Cord is tension-only; a two-sided spring pushes when slack and holds the work
open. Clean A/B at 800 stitches, seed 3, everything else identical:

| | bbox volume | aspect |
|---|---|---|
| two-sided springs, carries ignored | 20.75 | 1.41 |
| tension-only only | **19.59** | **1.07** |

More compact and markedly more isotropic, as predicted. Caveat worth stating:
settling is interleaved with growth, so these flags change *which object gets
made*, not only how it relaxes — the comparison is between two objects, not two
relaxations of one.

## C3 — and now it settles
Earlier I reported the model never reaches equilibrium, then worried that
finding was an artifact of comparing unequal iteration blocks. Re-run with
**equal blocks of 200**:

    two-sided springs   0.522  0.538  0.513  0.483  0.486  0.475   (flat)
    tension-only cord   0.569  0.511  0.462  0.443  0.402  0.376   (-34%)

So the original claim was right for the old model, and tension-only cord fixes
it. **PASS.** C4 also holds: it does not collapse.

## The transfer I got WRONG, and how packing fraction caught it
I argued the repulsion cutoff should be the cord's diameter rather than a loop
length, since that is what exclusion means. Tested before changing it:

| exclusion | 400 stitches | packing fraction |
|---|---|---|
| cord diameter | 11 x 11 x 15 cm | **96%** |
| cord diameter, 1600 stitches | 21 x 15 x 29 cm | **76%** |
| loop length (then-current) | 17 x 18 x 23 cm | 24% |

Random packing of cylinders tops out near 50-60%. A cord-diameter cutoff packs
cord **denser than cord can physically pack**, so it is wrong — the repulsion
acts between stitch *centres*, and a stitch is a whole bight enclosing space.
The loop length was right in kind.

But 24-35% is loose for a piece whose apertures the photographs show closed to
slivers. Sweeping for a physical density:

    repel_cut 0.9 -> 68%   1.1 -> 38%   1.3 -> 41%   1.6 -> 27%   2.0 -> 22%

Default set to **1.25**, which lands around 43-51% — a dense hand-worked
textile. The source calibration survives it: 400 stitches still gives 3 rings,
58 tails and 1.2 m strands, now at a physically possible density rather than a
third of one.

## Summary
Two real improvements and one refuted idea, all from questions the handling work
raised: carries are now load-bearing, cord no longer acts as a strut, the model
converges, and the fabric is as dense as a real one. The refuted idea is the
useful one to remember — exclusion is between the things that occupy space, and
in this object that is the loop, not the fibre.


---

# Twenty-fifth round — back to the photographs: what the rules still miss

Asked whether the source shows more kinds of stitching and binding than the
model has. It does, and the clearest one is not a different knot.

## Tension is not constant, and the model assumed it was
`evidence/q_ring_meet.jpg` is decisive: the **same tan cord**, in one frame at
one scale, runs as a tight dense chain reading as a cable in the upper left and
as large open loops in the lower right. Measured by eye off that crop, the chain
rungs differ by roughly **2.5-3x**.

Every rule so far described what the act is and what it passes through, and
silently assumed one size for all of it. A single loop size makes an even
fabric; the source is conspicuously uneven.

Added as L9: a per-stitch size multiplier that drifts **in passages** rather
than stitch to stitch, since that is how it clusters in the photographs.

| | |
|---|---|
| tension range produced | 0.61 to 1.39 across 14 passages (2.3x) |
| spacing follows intent | correlation **0.833** between actual stitch spacing and the tension it was worked at |
| tight vs loose passages | mean spacing **0.189** against **0.296** |
| source calibration survives | 400 stitches still gives 3 rings, 58 tails, ~15-18 cm |

A bug caught on the way: the solver still used one rest length for every edge
while the stitches were now spaced by varying ones, so the springs were pulling
the tight passages open and the loose ones shut. Rest lengths now follow the
tension each stitch was worked at. The realised range (1.57x) is narrower than
the intended one (2.3x) because the solver still pulls toward a common
configuration — honest, and a place to improve.

## What I could NOT establish
`evidence/q_fringe_head.jpg` shows what may be a cord **wrapped around a
bundle** — a gathering collar, which would be a genuinely different binding.
I could not confirm it: at this resolution a cord wound round a bundle and the
helical ply of a 3-ply cotton cord are indistinguishable, and that region is
backlit to silhouette. Recorded in RULES.md as suspected, not implemented, not
counted as a rule. The same caution applies to whether the heavy tan "rope" is
one thick cord or several worked as one.

Neither is answerable by more processing of these two images. One photograph in
flat light from 30 cm would settle both.


---

# Twenty-sixth round — the suspected wrap, refuted

Asked to stop hedging and work it out. The region was backlit to silhouette, so
I lifted it: gamma 0.22 on luminance, renormalised, local contrast, unsharp
(`evidence/q_fringe_head_lifted.jpg`). 44% of that region sits below 0.15
luminance, which is why it read as a flat shape before.

That resolves a bight seen edge-on with a dark aperture, and below it a banded
tapering cylinder — the banding being what I had taken for wrapping turns.

## The discriminating measurement
Turns of a wrapping cord are spaced at that cord's diameter. The helical ply of
a single cord bands at a fraction of its diameter. Autocorrelation along the
feature, and along cords I can confirm are single hanging tails:

| | period |
|---|---|
| suspect feature | 7 px (7, 7, 7, 8, 8) |
| known single tail A | 9 px (5, 9, 10, 10) |
| known single tail B | 6 px (2, 6, 6, 6, 8, 9) |

Indistinguishable. And a wrap would require a wrapping cord ~7 px across, while
the finest cord measured anywhere in the piece is **14-20 px** — no such cord
exists in the object.

**Verdict: no wrapped collar, no additional binding.** The banding is the cord's
own ply. The feature is the head of the fringe: an open bight with plied cords
leaving it.

This belongs on the refuted list rather than the open one — it was killed by a
measurement, not by an argument, and the measurement is cheap to repeat.


---

# Twenty-seventh round — integrating the findings, and one that will not fit

Asked whether the new learnings about the source are actually being integrated.
Checked each.

| finding | integrated? |
|---|---|
| L9, tension drifts 2.5-3x in passages | **yes** — generator and viewer, with controls |
| carry floats are cord and must be simulated | **yes** |
| cord is tension-only, not a strut | **yes** |
| exclusion is loop-scale; density should be ~45% | **yes**, `repel_cut` 1.25 |
| suspected wrapped collar | refuted, nothing to integrate |
| **cord is 3-ply, period 0.45 diameters** | **NO — see below** |

## The one that does not fit
I measured the ply off the source (period 6-9 px against a cord 14-20 px across,
so ~0.45 cord diameters) and then did not use it. Implementing it as a lobed,
twisting cross-section made the cord look **worse** — faceted rather than plied.

The arithmetic says why, and I should have done it first:

    ply period                0.0450 units
    path sampled every        0.0881 units
    samples per ply period    0.51        (need >= 2 for anything at all)

The ply repeats twice per sample. It cannot be expressed by this mesh at all;
what appeared was aliasing. Showing it geometrically needs about **46 samples
per bight instead of 12** — a 4x geometry cost for a detail visible only at
extreme zoom.

Turned off by default, with the measured numbers kept in the ruleset. The right
way to render it is procedural shading in the fragment shader, where the
function is evaluated per pixel rather than per vertex, and that is a separate
piece of work. Recorded here rather than left as a silently disabled parameter,
because a measurement that cannot be used is still a measurement.

This also follows the standing instruction that anything making the cord less
realistic comes out: a faceted cord is further from the source than a smooth
one, whatever the facets were meant to represent.

## A slider bug of the same shape as before
`tension_run` defaults to 28 but the slider had a step of 5, so the browser
snapped it to 30 and the viewer silently generated something other than the
default. Step changed to 1. This is the third time a stepped slider has
misrepresented a default; worth a standing check.


---

# Twenty-eighth round — viewer controls

| control | measured |
|---|---|
| stop spinning | camera movement **0** across six consecutive 500 ms samples once stopped; label flips between "Stop spinning" and "Start spinning" |
| drag rotates | handling off, drag on the cord: camera moves 3.45, **0** stitches grabbed |
| drag pulls when handling is on | 59 stitches taken, piece moves **2.894**, camera moves **0** |
| zoom buttons | 18.86 -> 15.09 -> 12.07 closer, 15.09 further, 18.86 on Fit |
| wheel | 18.86 -> 17.74 |
| trackpad pinch (ctrl+wheel) | 17.74 -> 17.10 |

Dragging now rotates by default and only grabs while **Handle it** is on. Both
gestures cannot share a plain drag, and rotation is the one you want most of the
time.

## Three false alarms in my own testing, all mine
1. "Camera moved 22 units while stopped" — I began sampling the instant after
   the state changed, while OrbitControls' damping was still bleeding off the
   accumulated spin. Sampled properly it is 0.
2. "Grabbed 0 stitches" — I was counting `pinned`, but the grab now populates
   `goals`. Counting the right map gives 59.
3. "The piece moved 1.717 with nothing grabbed" — the build animation was still
   playing, and the grab handler correctly declines while it is. That was the
   reveal, not a drag.

None of the three was a defect in the viewer. All three looked like one.


---

# Twenty-ninth round — two fingers rotate while handling

While handling, a plain drag holds the cord, which left nothing to turn the
piece with. Two-finger trackpad movement now rotates instead of zooming; pinch
(ctrl+wheel) still zooms, and outside handling mode two fingers zoom as before.

| | camera distance | direction turned |
|---|---|---|
| handling OFF, two fingers | 2.026 -> 1.905 (zoomed) | 0.48 deg |
| **handling ON, two fingers** | 1.905 -> **1.905** (unchanged) | **29.9 deg** |
| handling ON, pinch | 1.905 -> 1.819 (zoomed) | 0 deg |

Each gesture does one thing and only that thing. Rotation runs at 0.005 rad per
pixel of wheel delta; that is a guess tuned on synthetic events rather than on a
real trackpad, so say if it feels fast or slow and I will change the constant.


---

# Thirtieth round — double-click switches what the mouse does

Inside handling the mouse now has two jobs and double-click swaps them. The
button says which: "Handle it — pulling" or "Handle it — turning".

| | grabbed | camera moved | piece moved |
|---|---|---|---|
| pulling | **59 stitches** | 0 | 1.402, and it stays there on release |
| turning | 0 | **3.677** | 0 |

Toggling, measured: pulling -> turning -> pulling, label following each time.

## Detected by timing, not by `dblclick`
The native `dblclick` event cannot be used here. The grab handler calls
`preventDefault()` on `pointerdown`, and per spec that suppresses the
compatibility mouse events — `mousedown`, `mouseup`, `click`, `dblclick` — that
a double-click is built from. So the handler detects it itself: two pointerdowns
within 350 ms and 8 px, which also lets it undo the grab the first click began.

Two-finger trackpad follows the sub-mode: it turns the piece while *pulling*
(where a drag is busy holding cord) and zooms while *turning* (where a drag
already rotates). Pinch zooms throughout.

## One zero that was mine again
The first pulling trial reported `pieceMoved: 0` — I had fired all the
pointermoves synchronously, so no frame ran between them and the solver never
stepped. With 30 ms between moves it reads 1.402.


---

# Thirty-first round — the rings, and making pieces much bigger

## The rings were wrong, measured two ways
Asked what happened to the large white rings in the source. They were in the
model all along, but rendered as mid-tan thin hoops. Measured off photo 2:

    ring colour         RGB (190,169,134)   cream cord (142,136,128)
    -> the rings are BRIGHTER than the cord; I had them darker and browner
    outer / cord         8.7   (model had 10.7)
    tube  / cord         2.4   (model had 1.5)

Corrected to `ring_radius` 0.315, `ring_tube` 0.12, wood `(0.98, 0.88, 0.71)`.
The net effect is a ring slightly smaller across but 2.6x thicker in section,
and pale rather than brown — which is why the source's rings dominate and mine
disappeared.

## How a piece gets much bigger: three routes, measured
**Gauge — linear and free.** 800 stitches: 8 mm cord gives 22 cm, 20 mm gives
55 cm, 40 mm gives 110 cm, 80 mm gives **220 cm**. Same build time.

**More work — cube root and expensive.** 500 stitches 15.8 cm (0.3 s), 1,500
24.0 cm (1.0 s), 4,500 35.2 cm (7.6 s). Nine times the work buys 2.2x the size.

**Sprawl — the big one.** I expected the L3 join policy to control this.
**Measured, it does not**: chain, ladder, window and random all land at 20-24 cm.
What controls it is whether the act must happen against existing fabric. But
`contact` turned out to be effectively binary — 0 sprawls, anything above 0.3
compacts — so a radius is the wrong control. Added `sprawl`, the probability of
ignoring the pull toward the fabric:

| sprawl | longest dimension, 800 stitches, 8 mm |
|---|---|
| 0.00 | 21 cm |
| 0.15 | 79 cm |
| 0.35 | 111 cm |
| 0.60 | 198 cm |
| 1.00 | 345 cm |

A 16x range in extent from identical work. The JS port gives 24-311 cm over the
same range: same family, different random stream, as expected.

Worth stating plainly: at 80 mm the model says 2.2 m, but nothing here knows
that 80 mm rope is extremely heavy. Gravity is a nudge and no part of this
simulates a structure collapsing under its own weight.
