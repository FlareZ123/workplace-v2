# H-17 K04: invert a 128-bit transfer-checkpoint producer and test a coupon-seed bridge

**Agent 8 | 4 November 2026 | Original historical export, conditional producer test.**

**Outcome:** A source-conditioned reconstruction produced **24 complete 128-bit states**, and **25,344 complete K04 candidate assignments** after bounded state displacements, serializer choices, and route-mask reduction. The unmodified original K04 commitment matched **zero**. Across **416** original sixteen-checkpoint historical holdout models, **none** are source-consistent. Genuine planted generator histories pass all **26** readout models, and a separately planted source-compatible K04 commitment is recovered (five equivalent candidate assignments). No authentic K04 physical coupon bit is inferred. Six original slots continue to PASS; K04 and K08 remain MISSING, combined acceptance INCOMPLETE.

## Distinct mechanism and causal hypothesis

The transfer-audit records are **later** than the selected 3 October 18:02 UTC printer coupon; hence the printer coupon could conceivably have served as a seed for the subsequent preservation transfer. This reverses the direction of many previously tested hypotheses that would have the earlier coupon depend on later archival values. There is **no surviving source statement that this seed reuse happened**. Moreover, MAIL13 is dated **2 October 2026** while it describes AX-7782/83 completions whose transfer audit receipts are on **3 October 2026**; the competing original timestamps have a documented prepublication inconsistency. Thus neither the literal later AX receipt time nor the earlier message proves the actual causal history of the archive-transfer data. The test is a speculative mathematical link, not a historical reconstruction claim.

Unlike previously tested direct byte-pair relations, generic Reed–Solomon two-erasure interpolation, full-width K07-carrier matching, or conditional shared MT19937 source-stage embeddings, the present family **inverts a complete 128-bit linear state** from eight original 16-bit checkpoint observations and asks whether the resulting upstream seed could be a valid masked physical coupon. The state transition is Marsaglia four-word xorshift128, with `t=x xor (x<<11)`, `(x,y,z,w) -> (y,z,w,w xor (w>>19) xor t xor (t>>8))` in unsigned 32-bit arithmetic.

The 16-bit emitted checkpoint is one of **26 source-independent, frozen readout functions** on the updated state: each of the four native words' low half, high half or XOR of both halves (12 selectors), low/high halves of XOR for each of six pairs of state words (12), or low/high halves of all-four-word XOR (2). Every function is GF(2)-linear. This is a finite, testable class; an arbitrary nonlinear issuer, a hash/checksum process, a reseeded generator or a different event chronology lies outside it.

## Complete historical test

Primary files and SHA256 pins:

- `resources/evidence/transfers/transfer-audit.jsonl`: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- `resources/evidence/recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `resources/acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

All four transfers AX-7778, AX-7781, AX-7782 and AX-7783 have each eight `seq` values and two observed checkpoint attempts, yielding 16 original values per transfer.

1. **Original-only producer check:** For each selector × transfer × `attempt-major` or `seq-major` ordering × forward or reverse ordering = **26×4×2×2 = 416** tests, build **256 exact linear equations in 128 unknown initial-state bits**. Solve by GF(2) elimination and ask whether all original sixteen 16-bit words can arise from one uninterrupted xorshift128 state. **0/416 pass**. This checks real historical withheld output rather than merely a planted simulation.
2. **Selected-transfer inversion:** The custodian selects AX-7782 for K07. For each selector, separately use all eight `attempt=1` or all eight `attempt=2` words, `seq=0..7` forward/reverse. Eight outputs supply 128 equations. Only four XOR-of-halves readout architectures each fit three of the four original octet order/attempt choices, at rank **127**, giving **12 fits × 2 states = 24** complete hypothetical initial states. All others are inconsistent or lack a bounded solution. This is an **algebraic fit to an unverified producer architecture**, not 24 recovered historical seeds.
3. **Target-facing reconstruction:** For every complete fitted state, hypothesize that the original physical coupon is a serialized producer state at any of **33** offsets before or after it (including zero). Test four word-order conventions, both byte orders, raw state and state XOR the unchanged route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. Total `24×2×33×4×2×2 = 25,344` complete original SHA256 checks. **0 K04 original commitment matches**, including the masked-state form that would make the seed an actual escrow coupon. These are assignment counts and may include duplicate byte strings.

The positive controls use independently specified real xorshift128 states to produce sixteen source words for **all 26** selector families, each accepted by the exact source-equation solver. A synthetic source-compatible AX-7782 state is moved backwards three generator steps, serialized in reversed word order/little endian and XORed with the recorded mask to define a planted **outer SHA256** target; the same full-candidate enumerator finds that planted target under five equivalent assignments. The exact original K04 target remains untouched and unmatched.

**Source-pinned single-file test:** [`agents/agent8/k04_ax_xorshift128_seed_sft.py`](../agents/agent8/k04_ax_xorshift128_seed_sft.py). Locally executed against the original user-supplied ZIP-extracted resources on 4 November. Original data, `candidate.json`, verifier and acceptance unchanged.

## Interpretation and research decision

This excludes the enumerated **state/output/ordering architecture**, both as a transferable full sixteen-checkpoint producer and as a finite family of complete selected-coupon seeds. A half-observed xorshift emitter can fit selected eight-word groups retrospectively, yet all original sixteen-word controls contradict it. The copied 18:02 ACK was deliberately **not used as an input**. No posterior generator fit should be promoted into physical coupon authenticity without independent source-stage evidence.

A productive successor would identify a source-authenticated **post-coupon state recipient** or exact seed-transfer assertion with a heldout prediction, ideally from a genuine preserved stream whose 128-bit seed is uniquely invertible. Merely widening anonymous xorshift readout combinations or treating source-inconsistent octets as historical seed proof is unlikely to advance the missing K04. K08 final verbatim Emily caption is unrelated and remains unquoted.