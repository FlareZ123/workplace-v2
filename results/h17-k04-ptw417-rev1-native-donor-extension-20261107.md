# K04: PTW-417 revision-1 blocks in the p951 native-eight-stage donor bridge

**Agent14 | 7 November 2026 | Bounded source-derived extension.** No authentic K04 coupon recovered. K01/K02/K03/K05/K06/K07 remain accepted; K04/K08 remain missing.

## Question

The four asset/inspector-annotated PTW-417 revision-1 receipts form a complete B,D,A,C 16-byte block. A fifth signed revision-1 bay-A receipt has the same closeout state but omits asset and inspector fields. These alternatives were not included in the earlier p951 native-eight-stage donor list. Does either revision-1 block, paired with any of the existing donor blocks, determine a complete K04 component under the same hypothetical p951 MT19937 model?

This is distinct from the past-gap two-donor inverse extension reported by Agent43. It tests the separate p951 native-stage projection at stages 328–331 and 724–727.

## Source and method

The script reads the original `seal-receipts.jsonl`, recovery route, acceptance commitment and spool source from the repository. It asserts the receipt SHA-256 `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`. The p951 basis uses the original spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, with the selected row129 omitted, source rank 15,365, and the eight independent native donor stages fixed by the existing model.

The two added blocks preserve the revision-1 alternatives separately:

- Asset/inspector-annotated B,D,A,C: `AD1D814B64B2EE4A7E73B4CC5CB72EE5`.
- Unannotated bay-A alternative in B,D,A,C order: `AD1D814B64B2EE4A574A92325CB72EE5`.

Each block was added to the existing 11-donor set, producing 13 distinct 16-byte donors. Every ordered pair of distinct donors was tested with all 64 independent per-donor representations: little/big 32-bit word byte order, forward/reversed word order, and native/inverse-tempered words. The resulting eight native words were projected to the four selected stages, the unchanged K04 route mask was applied, and the complete official SHA-256 slot commitment was checked.

The source-pinned SFT also asserts the revision/state/fitment/signature fields and B,D,A,C order from the original receipt rows. A synthetic whole-component commitment check confirms that the enumerated candidate set distinguishes one planted candidate.

## Result

**9,984 complete candidates; 9,984 distinct components; zero official K04 commitment matches.** The synthetic uniqueness control passed. No selected K04 bits were recovered.

The second CI run succeeded: [workflow run 42392777782](https://github.com/FlareZ123/workplace-v2/actions/runs/42392777782). The initial run failed immediately because the copied p951 wrapper passed `ROOT/resources` to a helper that itself appends `resources/evidence`; the SFT was corrected to pass the repository root, then rerun successfully. This path correction is local to the new Agent14 SFT; the related Agent12/Agent43 scripts should be checked by their owners before reuse.

## Scope and limitations

This is a finite negative for the two source-preserved PTW-417 revision-1 blocks, the 11 prior donors, the specified eight p951 native stages, and the stated 64 representations per ordered donor pair. The p951 printer chronology and the hypothesis that PTW serials are native MT state words remain unverified. The result does not authenticate a PTW-417-to-ESC-N relationship, choose between the two bay-A receipts, exclude other source fields or producer models, or establish the physical coupon. Do not repeat this exact donor/representation family without a new source relationship.

Reproduce with **python agents/agent14/k04_native_eight_donor_rev1_sft.py** or dispatch **.github/workflows/agent14-k04-native-rev1-donor-manual.yml**.