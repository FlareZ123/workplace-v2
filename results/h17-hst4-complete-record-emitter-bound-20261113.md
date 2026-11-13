# HST-4 → PS-0300…0411 crosswalk: bounded complete-record emitter tests

**Status:** no validated bridge; no K04 candidate recovered.

## Question

Can the arithmetic association `PV seq + 200 = PS job suffix` be promoted from a locator to a record-level relationship capable of constraining the missing K04 coupon?

The test used the 112 PV records `seq=100…211` and the corresponding ordinary ACK jobs `PS-0300…PS-0411`. The association remains a hypothesis: `evidence/telemetry/export-readme.txt` describes retrieval order, acquisition timestamps and PV/unit as historian context; it does not define a seq↔job foreign key or a shared writer.

## Results

1. **Direct 16-byte record serialization:** for all 112 pairs, scanned every fixed byte offset in both endian orders for Unix timestamp (u32 and u64 seconds/milliseconds/nanoseconds), seq (u16/u64), value (float32/float64), and value-in-milli (u32). No field had a single fixed-offset match. This rejects the obvious fixed-layout timestamp/value/sequence serialization, not every conceivable codec.

2. **Standard CPython API calls in one post-job gap:** the p951 start positions give the following 112-gap histogram:

   | Gap words | Rows |
   |---:|---:|
   | 2 | 46 |
   | 3 | 25 |
   | 4 | 20 |
   | 5 | 6 |
   | 6 | 6 |
   | 7 | 2 |
   | 8 | 5 |
   | 9 | 1 |
   | 13 | 1 |

   A per-row emitter using `randrange(timestamp)`, `choice(tag)`, `choice(unit)`, `choice(quality)`, and `uniform(value)` needs at least six MT outputs (one per categorical/range draw and two for `random()/uniform()`) before rejection. **97/112** associated gaps are shorter than six words. A deterministic timestamp still leaves five minimum outputs and 91/112 gaps are shorter; even a one-word value draw plus deterministic timestamp needs four, while 71/112 gaps are shorter. Rejection sampling increases, never decreases, consumption. The single 1-word gap sometimes quoted for the whole spool is at job 0427, outside the 112-row seq+200 mapping.

3. **One-word packed record in a p951 gap:** tested a 29/30-bit record packing timestamp (7/8 bits), tag (2), value (17), unit (2), quality (1), in JSON field order. The bounded family covered two time bases, three value encodings, all 288 category codebooks, both bit directions and both spare-bit placements (6,912 layouts). Of the 112 rows, 96 have at least one completely unconstrained gap word; compatibility with such a word is vacuous. The remaining **16 rows have no unconstrained word in their associated gaps**, and none matched any layout. Neighboring-gap alignment also produced zero matches when at least 24 relevant bits were fixed.

4. **Complete CPython record calls across packet + gap:** because each ordinary packet supplies four words, also tested the natural full-record alternative across packet-plus-gap streams. The five calls were `randrange(110)`, `choice(4)`, `uniform(12,88)`, `choice(3)`, and `choice(2)), with variable rejection. All 120 field-call orders and all 288 category codebooks were tested against the 16 fully constrained rows, with starts at packet lanes 0–4 and the preceding-job alignment. No complete row matched.

5. **Payload-seeded per-row emitter:** tested `random.Random` seeded from each paired 16-byte payload as bytes, big-/little-endian integer, hex string, SHA-256 bytes, MD5 bytes, and route-mask-XOR bytes/integer. Across 120 call orders and three timestamp windows, no full 112-row fit survived the global category-code consistency check.

## Interpretation and limits

These tests close the obvious fixed struct, one-word packed record, standard per-field one-gap API emitter, packet-plus-gap CPython API emitter, and payload-seeded per-row API emitter under the stated seq+200 mapping and p951 source model. They do **not** prove that every possible custom multiword codec or global post-spool generator is impossible. The p951 state chronology and seq+200 association are themselves conditional, not authenticated source facts.

Do not use the 96 vacuous zero-mask compatibilities as positive evidence. Do not promote predicted PV values or missing seq212–227 into K04 donor bytes. Reopen only for a native HST writer/schema, authenticated seq↔job index, or a concrete predeclared multiword encoding that predicts complete unseen rows and corresponding spool objects.

## Reproduction anchors

- `agents/agent49/k04_p951_symbolic_basis.py` — pinned p951 start positions and source basis.
- `agents/agent50/k04_pv_postspool_chronology_sft.py` — forward p951 projection and prior scalar chronology work.
- `communications/agent43/20261113T094935Z_agent2-hst-emitter-no-source-schema.md`
- `communications/agent43/20261113T095751Z_agent2-hst-gap-budget-bound.md`
- `communications/agent43/20261113T100627Z_agent2-hst-packed-record-negative.md`

No source, candidate, verifier, or accepted component was modified.


## Target-causal LT-204 alignment follow-up

A targeted check of the two p951 causal gaps found a more specific but ultimately non-target-bearing fit:

- A (stages 328–331) lies in the post-job gap after PS-0343 and aligns with PV seq143 under +200.
- B (stages 724–727) lies in the post-job gap after PS-0396 and aligns with PV seq196.
- Both rows are LT-204 / GOOD, timestamped 21:13:42 and 21:13:48 UTC, within the K02 freeze window. The seq143 gap has seven words with its final two fixed; the seq196 gap has eight words with its first three fixed.
- A plausible tag → unit → quality → timestamp → value CPython schedule, with randrange(110) from 21:12:30 and uniform(12,88), fits both rows. It also has paths for the other two long-gap LT-204 rows (seq112 and seq166), leaving one trailing word in each gap. seq166 is wholly unconstrained; seq112 has multiple rejection paths. Thus only three rows provide meaningful checks, and the field/codebook schedule is not source-authenticated.
- I inserted accepted randbelow bits, safe common bits from rejected draws, and common-prefix constraints from both rounded uniform values into the p951 basis for seq112,143,166,196. Rank rose from 15,365 to 15,483, but the target at stages951–954 retained all 128 degrees of freedom.
- The eight selected K02 DIAG_WORD values as low-16 halves of A/B in natural order still leave 126 target degrees of freedom; high-16 variants conflict with PV high bits. This does not provide a bridge to K04.

Treat the alignment as an interesting diagnostic hypothesis only. It does not recover or constrain the K04 candidate under the current p951 model. Do not reopen without a source-backed LT-204 writer/codebook or a different relation that actually couples these gap outputs to the target.
