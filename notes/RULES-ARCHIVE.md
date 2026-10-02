# ARCHIVE — superseded rule sets, kept verbatim

These are wrong. They are kept unedited because the corrections are the useful
part, and because a record that only ever contained true things teaches nothing
about how to be wrong. Where this file disagrees with RULES.md, RULES.md is
right and this records what was believed at the time.

Two versions are below in one document: v1 (ring count as an input) and v2
(ring count as an output of band width vs ring capture). Both were built on the
same mistaken reading — that the fabric is an alternating square-knot macrame
net — which v3 refutes from the photographs.

---

# Rules inferred from the piece

Read off the two photos only — the piece was not disassembled, so everything
below is an inference from visible surface, not a measurement. Confidence noted
per rule.

## Materials (observed)
- 3 visible wooden rings, equal diameter, unfinished beech/birch. (high)
- Two cord colours: black and natural/cream, 3-ply twisted cotton. (high)
- A third, much heavier tan material (roving / chunky single) worked by the
  same rules at a larger gauge. (high)

## The generative rules

**R1 — Rings are nodes, cord-bands are edges.**
Every band of cord begins at a ring and ends at a ring. Nothing floats. The
object is a graph whose vertices are rings and whose edges are knotted sheets.
(high — all three rings in photo 2 have cord passing *through* them, not just
hanging from them)

> **Correction, after the maker said rings were added *as a result of* the
> rules.** My first version had R1 continue "...and you choose how many rings
> there are". That was wrong, and it was the wrong shape of wrong: it made the
> most interesting output of the system into an input. Ring count is not
> chosen. It is produced, by R9-R11 below. The original claim is left standing
> above because the rest of it still holds — rings really are the nodes — and
> because the error is instructive: I had read the finished object as a plan
> rather than as a residue of a process.

**R2 — Mount by lark's head.**
Cords attach to a ring by folding in half over it, both legs pulled through the
bight. One mounted cord = two working ends. This is the dense wrapped collar
visible on the ring circumference. (high)

**R3 — Four cords make a square knot; the knot consumes four and yields four.**
Outer two are working cords, inner two are fillers. Cord count is conserved —
this is why the lattice never thins. (high)

**R4 — Alternate by two (ASK).**
The next row shifts the grouping by two cords: right pair of knot *k* joins left
pair of knot *k+1*. Repeat. This single offset rule is what produces the diamond
net and the open picot gaps seen in photo 2. (high — the lattice is
unambiguously an alternating square knot net)

**R5 — Colour is set at mount time, never at knot time.**
Cords are mounted in a repeating colour order (here: two black, two cream).
The checkerboard is *emergent* — R4 shuffles a periodic mounting sequence and
the diamonds come out two-tone. Nobody chose a colour per knot. (medium-high —
the pattern is consistent with period-4 mounting; a different period would read
differently and I can't rule out period-2 everywhere)

**R6 — Terminate into fringe.**
Cord not consumed by the net is left free, cut to an uneven schedule, ends
combed out. Fringe is residue, not design. (high)

**R7 — Close the band onto a second ring, shorter than the straight path.**
A band attached at both ends, with the rings held closer than the band's relaxed
length, cannot stay flat — it buckles into a saddle. This is the whole source of
the three-dimensionality. A flat wall hanging obeys R1–R6; only R7 makes it an
object. (medium — this is the most load-bearing inference and the one I am least
able to verify from photos)

**R8 — Same rules, more than one gauge.**
The chunky tan material is worked with R2–R4 at perhaps 4× cord diameter and
proportionally fewer knots. Scale is a free parameter of the system, not a
different system. (medium-high)

**R9 — A knotted band is wider than the ring it left.**
An alternating square-knot sheet relaxes to a width set by two things only: how
many cords are in it, and how big one knot is. Four working ends per knot, two
working ends per mounted cord, so the sheet is `n_cords/2` knots across, and
`width = n_cords/2 x knot_pitch`. A ring can only gather what fits on its
mounting arc, `arc_width x ring_radius`. Nothing keeps these two equal. (high —
this is arithmetic on R2/R3/R4, not a new observation)

**R10 — When the band outgrows the ring, it takes more than one ring.**
`k = ceil(band_width / capture_arc)`. If k is 2, the front splits in two, two
rings are mounted instead of one, and the object branches. *This is where rings
come from.* The maker did not decide on three rings; three rings is what 
happened. Each branch carries fewer cords, so it is narrower, so it usually
stops splitting — which is why the count stays small instead of running away.
(medium — the mechanism is forced by R9, but whether the maker gathered at
exactly this threshold, or just gathered when it felt too wide, I cannot tell)

**R11 — Stop when the cord runs out.**
The budget is the length of cord you have. Size, depth and ring count are all
outputs of it. (medium — the honest alternative is that the maker stopped when
it looked finished, which is not a rule I can implement)

## Why this matters

Under the old reading the system had a knob labelled "number of rings". Under
this one there is no such knob, and the ring count has to be *measured* off the
output. 20 starting cords against a budget of 80 produces exactly 3 rings, which
is what the source piece has — but see MEASUREMENTS.md, that is one point of
agreement and not a verified reconstruction.

## What is *not* a rule
- The fringe lengths are not periodic. Treated as noise, not structure.
- Ring placement looks hand-found rather than regular. The generator makes it
  regular on purpose, so you can see the rule; irregularity is a dial.
