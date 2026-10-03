# Is it still true to the source?

Short answer: **the rules are; two of the rates had drifted and are now fixed;
one thing you asked for is a deliberate departure and is off by default.**

Audited parameter by parameter rather than from memory. Every row is one of
three things and nothing is left unmarked.

## The rules themselves — unchanged

L1-L8 in RULES.md are exactly as read off the photographs, with the evidence
crops cited per rule. Nothing has been added to them to make the generator work
and nothing has been quietly dropped. The one rule the photographs cannot settle
(L3, which older loop a join passes through) is still a switch rather than a
decision I made silently.

## What had drifted, and is now corrected

| | was | now | why |
|---|---|---|---|
| `ring_every` | 70 | **130** | The source has 3 rings on a piece that measures ~20 cm, which is ~400 stitches at 8 mm cord. 70 would put 5-6 rings on it. |
| `strand_runs_out` | 0 (endless) | **14** | ~50-60 tails on ~400 stitches means a strand ran out every ~14 stitches. Independent check: at 8.5 cm of cord per stitch that is a **1.2 m working length**, which is a sane length to cut — the estimate is not circular. |
| `heavy_every` | 0 (off) | **120, in runs of 14** | The source plainly has heavy tan roving (L5), so having no second gauge at all was a silent failure to represent a rule. It also used to scatter *single* heavy stitches through a fine chain, which is not a thing cord does; it now works contiguous runs, the way you pick up rope and use it for a while. |

With these, 420 stitches gives **21.7 x 21.4 x 15.6 cm, 3 rings, 60 tail ends,
10% heavy in runs, 1.2 m strands** — against a source of ~20 cm, 3 rings, ~50-60
tails, a minority of roving.

## Added since, and why it is more faithful rather than less

**Settling interleaved with growth** (`settle_every`, `settle_iters`). The
previous engine grew the whole piece against a rigid scaffold and relaxed it
once at the end. Real fabric drapes as you work it, and you place each stitch
onto something that has already moved. This is a correction toward the source,
not a liberty: it makes the physics continuous rather than applied once. Its
side effect is that the form genuinely unfolds and twists as it is made.

## Handling is not generating

The browser now contains a solver, which is a change to a rule I set early on.
The distinction that makes it defensible: the generator makes the object, and
the browser only **handles** one that is already made. It cannot alter what was
generated — Reset restores it bit-exactly — and it uses the generator's own
constants, sent with the object, rather than a second physics invented for the
viewer. Validated against the Python solver on the same state: agreement within
2%.

## Source-derived (measured off the photographs)

`strands=KN` strict per-stitch alternation · `loop_capacity=3` loops carry up to
three strands and apertures close to slivers · `ring_every=130` · `strand_runs_out=14`
· `heavy_every/heavy_run` a minority worked in runs · `cord_mm=8` · `contact`
on, because the piece is one mass · `turn>0`, because cord is flexible ·
`loop_a:loop_b` 1.7:1, which is the bight proportion in the crops.

## Added from a second look at the photographs
`tension_var` / `tension_run` (L9): the same cord is worked 2.5-3x tighter in
some passages than others in `evidence/q_ring_meet.jpg`. Source-derived in kind;
the specific numbers (0.45 spread, runs of ~28) are fitted to look right, not
measured.

## Added: sprawl
`sprawl` is the probability that a stitch ignores the pull toward existing
fabric and takes the first free site. At 0 the work accretes into a mass, which
is what the source is; at 1 it travels and makes a rope. **Not source-derived**
— the source sits at 0 — but it is a dial on an existing rule (L8's "the act
happens at the edge of the work") rather than a new rule, and it is what lets
the same amount of work make something metres long. 800 stitches at 8 mm cord:
21 cm at sprawl 0, 345 cm at sprawl 1.

## Chosen by me — the photographs do not determine these

`target_policy`, `join_rate`, `window`, `ladder_period`, `nearest_radius` — L3
is explicitly undetermined and this is the switch · `wander`, `hand` — the
character of the hand · `clearance`, `tries`, `probes` — packing and search ·
`max_stitches` — a budget, and labelled one everywhere · `cord_radius`,
`ring_radius`, `ring_tube` · all solver constants (`iters`, `gravity`,
`stiff_*`, `repel`, `damping`, `max_step`, `rebuild_every`) · `ring_weight`,
which measurement showed is nearly inert anyway.

## Deliberate departures — available, not default

| | default | what it costs |
|---|---|---|
| `strand_runs_out 0` (endless cord) | **off** | This is the "very long cords" idea. It scales to huge pieces, but the source's fringe *is* the record of spent strands, so switching it off removes the single most visible feature of the object. The viewer labels it `endless (not the source)`. |
| `cord_mm` above ~10 | **8** | Honest as a *different piece in the same rules*, since gauge is a free choice of the maker. A 26 mm rope version is not less faithful, it is a rope version. |

## The honest summary
The rules are the source's as far as two photographs can establish them. The
rates now match the source's own measurable features on four counts (size, ring
count, tail count, strand length). What is *not* established remains what it
always was: which older loop L3 picks, how often, and whether the maker stopped
for any structural reason at all. Those need the maker, and you have said the
photographs are all there is — so they stay switches, and stay labelled.
