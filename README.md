# Generative Loopwork

Objects generated from rules read off two photographs of a hand-worked piece of
cord. The page runs the generator in the browser — nothing to install.

**[Open the viewer](https://shibboleth88.github.io/generative-loopwork/)**

Make a piece, watch it being made stitch by stitch, then press **Handle it** and
drag the cord to pull it apart.

## The rules

The source contains no knots. At magnification it is a chain of loops that
captures wooden rings by passing through them. One act, repeated:

> Make a bight in the working strand, pass it through an open loop, and let the
> new bight become the open loop.

Everything else is a choice of what you pass it through.

| | |
|---|---|
| **L1** | through the loop you just made — a chain |
| **L2** | two carried strands, alternating every stitch; the two-tone pattern is a consequence, not a design |
| **L3** | through an *older* loop — the chain joins itself into a mesh. *Which* older loop is the one thing the photographs cannot settle, so it is a switch with five settings |
| **L4** | through a wooden ring — captured for good. This is why rings accumulate |
| **L5** | the same act at more than one gauge |
| **L6** | stop, cut, let the tails hang. The fringe is spent strands |
| **L7** | three-dimensionality is a consequence, not a step |
| **L8** | the act needs an open loop and somewhere to put the bight; when the tip has neither the work is carried elsewhere, leaving a float |
| **L9** | the hand works at a tension that drifts — the same cord runs 2.5–3× tighter in one passage than another |

Ring count, stitch count, size and tail count are **outputs**, not settings.
Sizes are real: everything is measured in cord diameters, so 8 mm cord puts a
typical piece around 19 cm across.

## Layout

- `index.html`, `gen.js` — the viewer and the generator, in JavaScript. This is
  what GitHub Pages serves.
- `src/loopwork.py` — the original generator, which also writes OBJ + MTL and an
  SVG preview. `python3 src/loopwork.py --out piece --max-stitches 600`
- `src/server.py` — a local server that runs the Python generator for the
  viewer, if you would rather generate there.
- `notes/` — how the rules were derived, what was measured, what was refuted,
  and which parameters are source-derived versus chosen.

The two implementations do not share a random stream, so a seed gives a
different piece of the same family in each. They were checked against each other
across five seeds: identical ring counts and loop capacity, joins and chain
spacing overlapping, mean bounding box within 3%.

## Not included

The source photographs and the magnified crops are not in this repository. They
are photographs of someone else's work. `notes/RULES.md` cites them by filename.
