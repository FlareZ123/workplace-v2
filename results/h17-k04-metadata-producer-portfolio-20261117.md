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
- There is no feasible assignment in which every ordinary gap has at least three hidden outputs. With a minimum of two, there is also no feasible assignment in which every gap has at most five hidden outputs. Thus the gap pattern cannot be represented by a uniform 3-, 4-, or 5-output allowance.

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
