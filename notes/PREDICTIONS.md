# Predictions for L8 — self-termination (written before the runs)

Earlier rounds in PREDICTIONS-ARCHIVE.md.

Cord is now unlimited. The only thing that can stop the act is the fabric: a
bight needs an open loop (one under `loop_capacity`) and a free site. So:

T1 Every policy must end by "enclosed", not on the safety bound. A run that
   hits `max_stitches` has not self-terminated and must not be reported as if
   it had.
T2 Size must be emergent: different seeds, same parameters -> different stitch
   counts. If the count is near-constant, L8 is a disguised fixed length.
T3 loop_capacity up -> larger pieces, monotonically. It is the direct measure
   of how much the fabric will accept.
T4 wander up -> larger pieces. Work that travels finds fresh space; work that
   stays put strangles itself.
T5 CONTROL: with clearance ~0 AND a huge loop_capacity, nothing can refuse the
   act, so the run MUST hit the safety bound. If it still ends "enclosed",
   something I have not accounted for is stopping it and my account of L8 is
   wrong.
T6 join_rate up -> smaller pieces. Joining consumes capacity and pulls the work
   back into itself instead of outward.

# What the handling work implies for GENERATION (written before the runs)

Three things learned by making the piece handleable apply to the generator,
which has none of them.

C1 CARRY FLOATS ARE NOT SIMULATED. `solve()` takes `carries` and never uses
   them — the cord that travels across the piece restrains nothing. Adding them
   must change the geometry. Expect modest compaction, strongest where carries
   span. If nothing changes, carries are not load-bearing and the claim that
   they are structure is wrong.

C2 THE SPRINGS ARE TWO-SIDED, SO SLACK CORD PUSHES. Cord is tension-only. A
   two-sided spring is a strut, and the generated form is partly being held open
   by struts rather than by cord. Tension-only should make the object MORE
   compact — smaller bbox at the same stitch count. If it comes out larger, I
   have the sign of the effect backwards.

C3 THE MODEL NEVER SETTLES. Measured before: per-block motion sits near 0.25
   for ever, and under gravity the piece creeps without limit. Both are expected
   symptoms of C2 plus a repulsion cutoff set to a loop-length rather than a
   cord diameter. With tension-only springs the continued-solving motion should
   DECAY rather than plateau. This is the one I am least sure of.

C4 CONTROL: with tension-only springs the made object should still be stable —
   if it collapses to a knot, exclusion is doing more work than I think.
