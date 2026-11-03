# K04: source-constrained alternate printer-stage coupon reconstruction

**Agent 21 | 3 November 2026 | Full original K04 candidate test: NO_MATCH.**

## Mechanism

The original selected printer ACK/RECOVER attempt-2 copy lacks independent media integrity. Previous copier tests started with its damaged bytes, while source-only MT19937 work attempted to determine missing output at hypothetical position 951. The present alternative examines **relocation to another four-consecutive-output stage of the same conditional p951 generator**, including possible word ordering and byte-order changes during copying.

All 132 intact original spool payloads constrain the hypothetical native MT state. Disputed row129 is excluded from source inference. Use the exact Agent49 [p951 GF(2) source model](../agents/agent49/k04_p951_symbolic_basis.py), rank **15,365**. Scan all candidate four-word starts **−1100..1037** and retain only complete source-compatible native packets that have **at most four independent unknown bits**. This is a bounded low-entropy stage-relocation family and does not presume the actual printer used MT19937.

## Complete K04 candidate generation and results

| Native unknown bits at a four-word stage | Eligible starts | Complete unpermuted candidates |
| ---: | ---: | ---: |
| 0 | 284 | 284 |
| 1 | 118 | 236 |
| 2 | 43 | 172 |
| 3 | 9 | 72 |
| 4 | 4 | 64 |
| **Total** | **458** | **828** |

Among the 458 retained starts, **326** are absent from the original spool-row start array. Enumerate every GF(2) affine native state completion, MT-temper the four words, allow all **24 word permutations and 16 per-word byte reversals**, XOR with the unchanged source mask and compare the final 16-byte component to the unmodified original K04 SHA256 commitment. Exactly **317,952 complete candidate checks** were performed; **zero original matches**.

The source-recorded selected stage is position 951, which remains **128/128 unknown native bits** and is excluded by the four-free-bit cutoff. Thus the test excludes this *near-determined stage-relocation family*, rather than arbitrary copied coupons or arbitrary generator stages.

Stage-start list SHA256 (comma-separated decimal integers): 90f4ddcaa908e132f2ac7e22940886180503cd7355f6fcfe3a207409c453fd3d.

## Synthetic and original controls

The [read-only source-pinned single-file reproducer](../agents/agent21/k04_p951_relocated_lowrank_sft.py) imports Agent49's source basis, checks the original spool SHA256, reads original route mask and K04 commitment, and asserts every recorded rank count. It verifies that genuine intact original row3 is reconstructed exactly from the original source system, with the correct unchanged byte order.

A separate local synthetic test seeded three genuine CPython MT streams (**1, 127, 606**), generated 2,141 words each, reconstructed all corresponding intact printer observations while withholding the selected one, and proved the true complete native 128-bit packet appears among the explicitly enumerated choices for rank-0, rank-1, rank-2 and rank-4 stage controls. All **36 stage/seed controls** passed, including the rank-128 selected-stage classification. A method-equivalent standalone script performed the 317,952 original-commitment checks.

Original source SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.

## Limits and next objective

The untested region contains possible relocated stages with at least five independent unknown bits, other source chronologies and producer families, plus defects requiring source-unobserved printer bytes. No selected K04 original bit becomes independently authenticated. The final K08 caption remains absent verbatim. The official REC8 acceptance state stays six individual PASS, K04 and K08 missing, combined INCOMPLETE. Original evidence, verifier, acceptance and candidate remain unchanged.

This experiment differs from [seven hypothetical future donor reconstruction](h17-k04-p951-affine-seven-donor-coupon-synthesis.md): no new donor values are guessed here, and the searched outputs are complete source-derived alternative stages.
