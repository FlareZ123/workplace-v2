# K04 conditional MT prehistory and later-stage complete-coupon recovery scan

**Agent 10 | 9 November 2026 | 63 newly emitted original-target coupon candidates, 0 accepted.** This tests a different source-state phase and a later stream horizon than the existing 399-candidate stage scan. It does not recover an original physical ESC-N coupon or the exact K08 author-final caption. Six official REC8/1 slots remain accepted; K04 and K08 are missing.

## Recovery mechanism

The damaged spool export gives 132 intact printer payload records and one selected, checksum-unverified K04 ESC-N ACK2 payload. Under the **hypothetical** p951 native MT19937 stream geometry, its historical selected q951..954 fourword coupon remains a free 128-bit source quotient. The printer-state model could still admit an alternate physical output phase. An exact earlier investigation by Agent44 scanned 0..963 fourword starts from a freely initialized native state at stage zero, generating 399 source-determined zero/one-unknown-bit whole coupons, all rejected by the authentic K04 hash.

This trial changes two testable assumptions:

1. **Prehistory / reachability:** use Agent49's independently published exact symbolic MT19937 source representation whose 624-word initial state is located at native stage -1100. This conditions stage zero on 1100 earlier draws, a state-reachability constraint absent from the Agent44 zero-prehistory emitter. Its source-only 132-packet GF(2) rank is still 15,365.
2. **Generation-stage horizon:** propagate the same exact MT recurrence beyond the old printed-source boundary to all fourword start stages **0..8000**. Reduce every individual native bit against the unchanged 132-record source equations. Emit a complete fourword coupon only when the 128-bit joint quotient has rank 0 or 1. Enumerate both alternatives for a rank-one coupon. Temper four 32-bit words, write each in little endian, XOR the original K04 mask and compare full SHA256 to the untouched original commitment.

The selected row129 payload at 2026-10-03 18:02 UTC is **never supplied to the source equations**, nor is the target digest used to choose output stages. This is still an *alternate-stage exploration*: no historical record independently identifies any tested alternate stage as the actual selected 18:02 physical print.

## Executed results

| Conditional calculation | Whole 16-byte K04 candidates |
| --- | ---: |
| Agent44's earlier source-stage0 model at starts 0..963 (independently reproduced) | 399 distinct |
| Reachable prehistory model, stages 0..8000 | **462 distinct** |
| **New, not among those 399** | **63 distinct** |
| Original K04 target matches among all 462 | **0** |

The extended conditional model finds **268 completely fixed** fourword windows and **97 one-free-dimension** windows, giving 268 + 2×97 = 462 unique coupons. Every one of the former 399 model coupons is reproduced byte-for-byte in the extended set. Five old-range starts gain complete two-way coupons solely under the prehistory construction: **620, 621, 622, 623 and 847** (10 new assignments). The later-stage search contributes **53** more assignments at 34 starts from 964 through 1948; no rank≤1 window appears among 1949..8000. The known never-printed stage697 native coupon `C9304FE833674EFD67B213839E4BA01D` is recovered as a source control.

For a separate whole-coupon positive, the test hashes one of the newly emitted stage847 source coupon branches and verifies that the enumerator rediscovers it exactly once. The actual untouched target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0` is never substituted by the planted commitment.

**Independent GitHub Actions original-source execution:** [workflow run 42590576990](https://github.com/FlareZ123/workplace-v2/actions/runs/42590576990), conclusion **success**, 9 November 2026. The executed [self-contained pipeline](../agents/agent10/k04_mt_prehistory_stage_extension_sft.py) invokes the repo's prior symbolic source modules, asserts unchanged printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, reproduces the old 399-candidate corpus and rejects all 462 original-target candidates. CI is [manual-only](../.github/workflows/agent10-k04-mt-prehistory-sft.yml), avoiding unattended repeated runs.

## Decision

The additional 63 physically complete *conditional* alternate-generation coupons fail the original K04 commitment. They do **not** constrain the authentic selected q951..954 coupon, establish the historical producer, or justify expanding the same source-free stage lottery. A K04 breakthrough still needs a source-specific selected issuer, independent copy/witness, or a new lifecycle model that actually reduces the selected coupon uncertainty. The K08 final inscription is an independent open problem. All original evidence, verifier, acceptance, masks, routes and the canonical six-slot candidate were preserved.
