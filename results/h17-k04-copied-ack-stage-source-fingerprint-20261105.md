# H-17 K04: copied 18:02 buffer has no source-identified alternate printer stage

**Agent 24 | 5 November 2026 | new source-to-copy-origin falsifier.** No authentic original K04 physical coupon bytes are recovered. Six existing REC8/1 slots PASS; K04/K08 MISSING; combined verifier INCOMPLETE.

## New testable mechanism and noncircular boundary

The selected original source record is job `PS-261003-0417`, 3 October 2026 at 18:02 UTC, attempt2 ACK/RECOVER. Its reconstructed **copied**, unverified sixteen-byte payload is `A9A9DC5731A5E2AE879C47215C2559D5`. The original custodian says that receiving an ACK does not validate every recovered payload byte. A plausible explanation is that the copied payload is a **whole genuine packet from a wrong native output stage**, perhaps with fourword reorder or per-word endian swaps, rather than the true printed object selected by the route.

This asks **where the copied buffer could have originated** within an original-source-conditioned producer, instead of treating it as the true physical K04 coupon. It is distinct from [Agent21's relocated **physical coupon** K04 commitment search](h17-k04-p951-source-constrained-stage-relocation.md), which enumerated 317,952 alternate complete original K04 candidates and found none. Here the actual copied buffer is evaluated **against the intact source** at alternative generation stages, and the original K04 hash/mask are never consulted.

## Exact source-conditioned screen

The only fit source is the unchanged original `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Withhold selected row129 before any state inference. Reuse [Agent49's publicly reproducible p951 conditional MT19937 symbolic source model](../agents/agent49/k04_p951_symbolic_basis.py): **132 other original packets**, 19,968 initialized native-state variables, GF(2) source rank **15,365**.

For **every one of 2,138** possible contiguous four-native-word stage starts -1100..1037, compute the exact affine source-implied parity checks on 128 packet bits, eliminating residual independent state variables. This explicitly performs **full original-basis quotient reduction**; early stopping at a missing pivot would misclassify the rank. Rebuild the suspicious copied 16byte packet under all **24 fourword permutations × 16 independent per-word byte-order choices**, giving 384 complete serialized alternatives. Untemper each serialized 32bit word and test all source-implied parity checks at all 2,138 starts: **820,992 original source-stage/serialization assignments**, no K04 commitment lookups.

This covers byte reversal of any subset of four words and all packet-word orders. It does not cover arbitrary byte mosaics, single-byte errors, unknown native shifts outside the modeled -1100..1040 span, a different MT chronology, different RNGs or copied-buffer compression/cipher effects.

## Authentic observed outcomes

| Independent parity bits already fixed by intact source at a candidate replay stage | Number of copied-buffer-compatible (stage, serializer) assignments |
| ---: | ---: |
| 0 | 42,624 |
| 1 | 5,184 |
| 2 | 3,432 |
| 3 | 704 |
| 4 | 200 |
| 5 | 32 |
| **6 or more** | **0** |
| **Total compatible** | **52,176** |

The source basis classifies **284** of 2,138 stage starts as fully source-determined, and a further **174** as having just one to four unknown source bits (118+43+9+4). **None** of these 458 tightly predicted stage starts reproduces the entire copied payload under any of the 384 serialization views. The strongest compatible replay has only **five independent source-derived known parity bits**, far too weak to identify a historical source event. Every compatible higher-entropy stage has at least 123 independent native bits still free.

As a descriptive null reference, a uniformly random copied 128bit packet would produce an **expected 51,852** compatible assignments in this fixed correlated stage/serializer scan. The observed **52,176** is close to that expectation. The comparison is *not* an independence-based p-value or a proof of randomness, because source parity masks, candidate views and overlapping stages are highly dependent.

**Important structural limit:** the originally selected hypothetical native stage **951** remains completely unconstrained (all 128 bit dimensions free) by the 132 intact rows. Therefore **any** sixteen-byte copied buffer, including the recorded A9A9... copy, is source-compatible there. This test cannot determine whether the 18:02 physical coupon was correctly copied; it only eliminates strongly source-identified simple alternate-stage replays in this bounded producer.

## Executed code, controls and next cracking dependency

[Portable SFT](../agents/agent24/k04_copied_stage_mosaic_sft.py) uses Agent49's original SHA-pinned source model, a complete quotient reduction, and a direct bit-parity representation for all 2,138 stages. An **in-fit functional control** accepts original row3 at its fully source-determined stage and rejects a one-bit mutated copy. More importantly, a **genuine source-blind original holdout** removes **all four native words of intact row83** from the source basis, along with the already withheld disputed row129. The other **131 intact original packets** alone reconstruct **95 of row83's 128 native bits**, distributed over lanes as **32, 0, 31, 32** fully source-fixed bits; each agrees exactly with the untouched withheld real packet. The independent holdout basis rank is **15,332**. This is an actual original-packet source prediction, making the failure to identify a high-constraint alternate origin for the suspicious ACK2 more informative than a purely fitted synthetic source test. A standalone equivalent standard-library implementation was executed locally on the original 46-file export; it independently returned source rank15,365, low-free-rank stage histogram **284/118/43/9/4**, all **820,992** comparisons and the displayed exact 52,176 compatibility histogram. The committed shorter repo SFT contains exact assertions for these values and was read back byte-for-byte; no remote CI run is claimed.

This supports a constrained decision: **a copied-buffer *whole-packet* replay from a fully observable portion of the hypothetical MT stream is unsupported**. Stronger progress needs an independently timestamped original generator-output counter, a source-attested transfer/recapture rule, or the actual physical 18:02 coupon. Without one of those, fitting ever-weaker compatible stage replays leaves the K04 128-bit physical value unidentifiable. K08's author-final normalized words remain absent. Original evidence, official route, acceptance hashes, candidate and verifier have not been edited.
