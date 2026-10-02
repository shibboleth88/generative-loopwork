# ARCHIVE — predictions for the superseded engines, verbatim

Restored after I overwrote PREDICTIONS.md instead of rotating it. These are the
original texts as written, unedited. They concern engines built on a reading of
the source that RULES.md v3 refutes.

---

# Written before the runs below

P1  seed only: knots / working_ends IDENTICAL (topology is rule-determined),
    centroid moves > 1%. If topology moves, the seed is leaking into structure.
P2  colour_order KKNN -> KN: >25% of ends change colour, bbox IDENTICAL.
    R5 claims colour is mount-time and geometrically inert. If bbox moves,
    R5 is wrong as implemented.
P3  slack 1.38 -> 1.02: bbox shrinks on at least one axis by >5%. R7 claims
    slack is the only source of buckling.
P4  rows 14 -> 5: knot count falls roughly 2.5x.
P5  CONTROL for the renderer: two different seeds must give different SVG
    bytes. Identical bytes = the picture is not downstream of the solve.
P6  CONTROL for R4: disabling the alternation offset must change the geometry.
    If it does not, the alternation code is dead and the net is not an ASK net.

# Second round — written before the growth engine was measured

The engine changed twice since the runs above (the solver was vectorised with a
slightly different velocity clamp, and ring count became an output). Every
number in the first round is superseded; it is kept because the reasoning is
still the record of what I believed.

G1 cord_budget up -> rings up, monotonically. R11 says the budget is the only
   thing that ends growth.
G2 start_cords up at FIXED budget -> rings DOWN. Wider bands cost more cord per
   row, so the budget buys fewer generations. If rings go up, I have R9/R11
   backwards.
G3 ring_radius up -> capture arc up -> splits DOWN, possibly to zero. R10 says
   splitting is a width-vs-capture comparison and nothing else.
G4 CONTROL for the hand: with hand=0 the object must be bit-identical across
   seeds apart from fringe cuts. If seeds still differ structurally, something
   unintended is reading the RNG.
G5 CONTROL for R10: max_branch=1 forbids splitting. splits must go to 0 and the
   object must change. If it does not, the branching code is dead and rings are
   not emerging the way I claim.
