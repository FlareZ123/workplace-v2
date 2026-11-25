# K04: complete AX-7782 retry history as a p951 future-donor source

**Agent 50 · 25 November 2026 · bounded candidate screen; no K04 recovery**

## Question

The earlier AX-7782 cross-stream screen used the committed attempt-2 checkpoint chain. This test asks whether the **full retry history**—attempts 1 and 2 for all eight chunks—could provide a source-derived block of future MT19937 words, alone or combined with a different retained source block.

This is deliberately exploratory. The transfer audit does not attest a common transfer/printer generator, and AX-7782's object-version time and Bundle06 inclusion remain unverified. The 20:55:10Z commit timestamp is not treated as proof that the object was created then or that it post-dates the selected printer event.

## Source and model

- The selected PS-261003-0417 ACK2 payload is withheld before decoding. The original spool SHA-256, transfer-audit SHA-256, route SHA-256 and acceptance SHA-256 are pinned.
- AX-7782 contributes 16 two-byte checkpoint fields: attempts 1 and 2 for sequences 0–7. The bytes are preserved as recorded.
- Two explicit orderings are tested: sequence-major (each chunk's attempt 1 then attempt 2) and attempt-major (all attempt-1 chunks then all attempt-2 chunks). Adjacent halfwords are paired into eight 32-bit words. Both halfword-pair orientations, 32-bit endiannesses, word orderings, and native-versus-untempered interpretations are covered: 32 AX donor presentations.
- The conditional p951 seven-donor affine inverse uses seven future native words at positions **1179, 1180, 1181, 1347, 1348, 1574 and 1575**.
- The existing seven seeded full-stream positive controls were rerun: 7/7 exact withheld-coupon reconstructions passed.
- To avoid reusing the attempt-2 chain as an independent source, its K07raw block is **not** included among the second source blocks. The five distinct blocks are WN14 ink groups, selected K02 telemetry preimage, PTW-417 serial suffixes, K05 recorder controls, and K06 RC-17 service-order footer strips.

## Complete-candidate results

| Construction | Presentations | Distinct 16-byte components | K04 commitment hits |
|---|---:|---:|---:|
| AX retry-history block alone (eight words, omit one) | 512 | 484 | 0 |
| AX three-word window + other four-word source block, or AX four-word window + other three-word source block | 40,960 | 38,720 | 0 |
| **Combined** | **41,472** | **39,204** | **0** |

Every candidate was serialized through the unchanged p951 inverse, XORed with the original route mask, and checked against the complete original K04 SHA-256 commitment. Candidate bytes and derived component hashes are not printed or persisted.

## Interpretation and limits

This closes only the explicit retry-history-as-eight-word-block construction and the enumerated two-source combinations. It does not establish that checkpoint fields are MT outputs, that the transfer and printer shared a generator, or that AX-7782 contains the missing profile-refresh material. The p951 chronology itself remains a conditional model, not an authenticated printer firmware history. No selected K04 bits were recovered.

The previous 199,424-candidate aligned printer/transfer arithmetic and byte-mixing screen remains a separate bounded negative. This test is not an expansion of those arithmetic operations: it uses the previously untested attempt-1 checkpoint history as an input to the seven-donor inverse.

**Decision unchanged:** the next target-bearing source is still the native PS-0417 attempt-2 queue/job manifest, complete spool/driver image, physical ESC-N coupon and handoff witness, or a separately authenticated profile-refresh source object. Do not widen this into arbitrary retry permutations or treat AX-7782 as a K04/K08 carrier without an original manifest/object-version link.

## Reproduction

Run `python agents/agent50/k04_ax7782_retry_history_donor_sft.py` from the repository root. The script imports the existing p951 affine inverse, re-runs its synthetic full-stream controls, pins the original source files, withholds the selected ACK2 payload, and reports aggregate counts only. It does not modify evidence, acceptance, verifier or canonical candidate.


## Reproduction checkpoint — 2026-11-25T05:32:45Z

The source-pinned script was run independently in GitHub Actions workflow run 45554228396 and completed successfully. Seven seeded full-coupon controls passed. The committed assertions held:

- AX-only: 512 presentations, 484 distinct components.
- AX-three cross-source: 15,360 presentations.
- AX-four cross-source: 25,600 presentations (the loop includes both first/last three-word source selections and both output endiannesses).
- Cross-source total: 40,960 presentations, 38,720 distinct components.
- Combined total: 41,472 presentations, 39,204 distinct components.
- Original K04 commitment matches: 0.

This resolves the arithmetic objection raised in Agent16's 2026-11-25 broadcast: its 28,160 estimate omitted the AX-four first/last source-pick factor. The script and aggregate output are now independently reproducible; the result is still negative. The historical AX-7782-to-printer producer relationship remains unauthenticated, and the selected ACK2 payload was not decoded.
