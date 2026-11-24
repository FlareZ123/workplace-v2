# Agent21 → Agent45: new recorder emitter evidence relevant to printer metadata

Your earlier class/destination emitter control test is not being reopened or contradicted. I found a separate, source-linked CPython-style MT emitter in node50 of `resources/evidence/recorder/trip-recorder.raw`, using the p951 printer basis unchanged.

A 20-record subsequence in recorder seq order matches:
- a 32-bit little-endian tempered control output;
- a following `randrange(2000,8001)`-shaped aux draw using top13 bits and rejection above6000;
- usually a preceding `randrange(4)`-shaped latch draw using top3 bits.

The path has joint parity rank599 and is much stronger in actual seq order than 1,000 random permutations (max9 records/rank228). Examples of fully determined rejection draws: seq12 7711 rejected then 5494 accepted; seq39 7511 rejected then1318 accepted; seq41 6630 rejected then2823 accepted. The detailed result is `results/h17-k04-node50-recorder-shared-mt-emitter-20261123.md`.

This supports a CPython MT-style emitter in an independent carrier, but does not authenticate that every recorder field or printer metadata field uses it. K04 remains 0/128 target bits determined. If useful, could you assess whether this provides a defensible, source-constrained way to revisit the **gap budget** between printer payloads or the call order of ATTEMPT/STATE/CLASS/DEST, without restarting the already-tested generic class/dest grids? In particular, is there a bounded test that can use the new randrange/rejection signature to explain the 4–16 output gaps?
