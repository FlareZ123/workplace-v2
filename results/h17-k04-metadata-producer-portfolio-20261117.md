# K04 metadata-producer portfolio: stage-free budget and finite joint writer

**Date:** 2026-11-17  
**Status:** Conditional negative; no K04 component recovered.

## Question

Can the 128 ordinary 16-byte spool payloads be one contiguous MT19937 stream of four little-endian 32-bit outputs per packet, with the recorded CLASS/DEST metadata produced by two CPython `randbelow(3)` calls in each inter-packet gap?

This note consolidates Agent17's stage-free draw-budget analysis with Agent6's finite joint-stage/category-writer search. They are complementary tests of the same narrow producer family, not independent proofs that every possible MT-based producer is impossible.

## Stage-free recurrence bound (Agent17; independently reproduced by Agent6)

Input is the supplied `evidence/print/spool-reconstruction.log`, whose SHA-256 is:

`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

Agent17's reproducible implementation is [`agents/agent17/k04_stagefree_metadata_gap_bound_sft.py`](../agents/agent17/k04_stagefree_metadata_gap_bound_sft.py).

I independently reran the implementation against the uploaded archive and separately repeated the calculation using **only the 128 ordinary rows (rows 0–127)**, excluding the selected ACK2 row and every late row:

- The ordinary-only 512-word set yields **23 exact MT19937 recurrence witnesses**.
- Difference constraints from those witnesses require at least **936 MT output positions** between the start of ordinary row 0 and ordinary row 127 when every one of the 127 gaps is allowed at least two hidden outputs.
- The 128 packets account for 508 known payload words across those gaps, leaving a lower bound of **428 hidden MT outputs**.
- Removing any one of the 23 ordinary-only recurrence witnesses lowers the bound only to **425**; removing any two lowers it only to **417**.
- The full 132-row intact set yields 25 witnesses and the same 428 lower bound.
- The **ordinary-only 23-witness graph** has no feasible assignment with every gap containing at least three hidden outputs. It does **not**, by itself, exclude all gaps in [2,5]. The **full 25-witness graph**, including the two late-row witnesses, additionally has no feasible assignment with every gap in [2,5]. The 428 lower bound and the minimum-three contradiction survive ordinary-only; the maximum-five contradiction depends on the late rows.

The positive control is substantive: a seeded CPython MT19937 stream with four payload words per row and three filler outputs in each ordinary gap produces 40 exact recurrence witnesses, recovers the exact stage offsets for every witness, and passes the difference-constraint consistency check. The untemper transform also round-trips one million random 32-bit values.

### Draw-budget implication

Two CPython `randbelow(3)` calls per gap make 254 rejection-sampling calls. Under the ideal independent-uniform-output approximation, each call consumes a geometric number of MT words with acceptance probability 3/4. The probability of consuming at least 428 words is approximately **7.18 × 10⁻¹³**.

This is a model-based likelihood, **not a formal impossibility proof**: MT outputs are deterministic once seeded, and the historical seed distribution is unknown. The deterministic result is the conditional 428-word lower bound; the probability quantifies how poorly the specific 254-call CPython sampler explains that bound under its usual random-output model.

## Finite stage/category-writer search (Agent6)

See [the 170-chronology joint category-producer result](h17-k04-170-chronology-joint-category-producer-20261117.md) and [the implementation](../agents/agent6/k04_one_root_joint_metadata_sft.py).

That search combined six p950–955 geometries and 164 one-root perturbations, then tested first-gap/any-gap consecutive `randbelow(3)` CLASS/DEST calls, both call orders, both row bindings, and all 36 static codebooks: **48,960 configurations**, zero fits to the first 95 ordinary headers. Its seeded synthetic positive control passed.

The two findings answer different questions:

1. The 170-chronology search rejects that finite set of stage geometries and static metadata mappings against the observed labels.
2. The stage-free graph does not choose a chronology or codebook; it shows that the required hidden-output budget is already an extreme tail for 254 CPython `randbelow(3)` calls, without relying on the p950–955 stage set.

## Interpretation and decision

- The result is conditional on the 16-byte payloads being four consecutive little-endian MT19937 outputs from one shared stream. The recurrence witnesses support that model, but do not authenticate the historical producer.
- The 428-word bound does **not** recover the missing PS-0417 coupon and does not prove that no other producer, call schedule, PRNG, or copy-stage relation exists.
- Do not continue enumerating nearby MT roots, static codebooks, or minor `randbelow(3)` chronology variants. Reopen this family only if a new source-indexed observable or independently grounded producer/call-schedule rule appears.
- K04 remains unresolved. The canonical candidate and acceptance commitments are unchanged.


## Selected PS-0417 row integrity check (Agent6, 17 November)

The selected ACK2 payload was tested as a **target observation**, not used to discover the source-only recurrence network. I included all 133 log rows, untempered each four-word packet in the same little-endian convention, and reran both the first-order MT recurrence search and the native second-order four-sum search:

- The first-order search still returns **25** exact witnesses; none contains any of the four words of row 129 (flat word indices 516–519). Rows 128 and 130 are also absent; the only late rows with first-order witnesses are 131 and 132.
- The second-order search still returns **15** quads in **10** groups; none includes row 129.
- Rows 128–130 are the three PS-0417 records: attempt 1 REQUESTED, attempt 2 ACK/RECOVER/bench (row 129), and attempt 3 REQUESTED. The latter is identified in the print-fleet note as a button press rather than a print. The surrounding late ACKs are PS-0448 (desk, row 131) and PS-0420 (bench, row 132).

This is not proof that row 129 is not a physical coupon: it could belong to a separate dispatch generator or simply lack a witness under these specific identities. It does mean the ACK2 payload is **not corroborated by the ordinary spool MT recurrence network**, and the entire PS-0417 attempt block is isolated from it. Combined with MAIL-16's warning that ACK is dispatch status, not media-integrity, the row-129 payload should be treated as a dispatch candidate—not as authenticated printed media. Directly XORing the row-129, row-131, or row-132 payload with the supplied K04 mask does not satisfy the K04 commitment.

**Research consequence:** prioritize a source-backed physical print/copy-stage record or a correction to the selector/mask. Do not spend further effort fitting the ordinary MT stream to row 129 unless a new source record links the PS-0417 dispatch transaction to the actual printed coupon.


## RECOVER-conditioned two-word interleaved call (Agent47)

[Agent47's reproducible report](h17-k04-recover-conditional-two-word-interleave-20261117.md) tests a source-indexed alternative to two consecutive metadata samplers: after an accepted CLASS=RECOVER, one additional operation consumes exactly two native MT outputs before DEST (or after CLASS when DEST is sampled first). The two filler words are unconstrained, so the model is an optimistic superset of any specific two-word call such as `random()` or `getrandbits(64)`.

The test uses the same 170 source-compatible p950–p955 / one-root chronologies, all 36 global CLASS/DEST codebook pairs, both sampler orders, both current/next-row bindings, and both first-hidden-word/any-start placements: **48,960 configurations**. It finds **0** fits to the first 95 ordinary gaps; the best still contradicts 24. Both planted CPython positive controls (CLASS-first and DEST-first) recover the planted codebooks/order with zero holdout errors.

This closes only the RECOVER-conditioned, exactly-two-word branch under those chronologies and static codebooks. It does not exclude other conditional classes, filler lengths, multiple/variable calls, multiple streams, or a different producer. Do not expand the branch without a new source rule.
