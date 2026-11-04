# K04: selected-versus-alternative affine post-processor source holdouts

**Agent 11, 4 November 2026.** Read-only test of the 13:15 UTC Critic's alternative-stage proposal. The original six-pass candidate, official verifier, commitments and 46 evidence members remain unchanged. No K04/K08 recovery.

## Proposed selection-stage causal mechanism

Hypothesis: the output selected by a historical selector is a compact deterministic *post-processed* version of a preceding/draft 16-byte source block, and the same family of transforms can be applied across different file types.

Construct 18 concrete historical sets of alternative records, retaining the whole 16-byte source representation: original recorder node49/event82 series seq200..203 (older CRC-good), seq900..903 (CRC-bad), or seq990..993 (late CRC-good), all contrasted against selected seq300..303; RC-17 revision B (withdrawn) or D-draft against selected authorized C, ordered by DRAIN/ISOLATE/PURGE/VERIFY; transfer AX-7778 drill, AX-7781, or AX-7783 aborted against accepted AX-7782 (greatest attempted checkpoint for each seq0..7). Each source selected block is obtained from the original binary/text/JSONL, and the parser checks CRC statuses and the accepted K05 bytes; the printer export SHA256 is pinned.

**Frozen inference/holdout:** For every 3-family alternative selection and 8 shared byte/word views, fit a *single* two-parameter affine map on TWO original old→selected pairs, then predict the entire THIRD original 16-byte selected block. The evaluated maps are affine over GF(2^128) using polynomial x^128+x^7+x^2+x+1; affine modulo 2^128 (including solvable even first differences); independent four-lane affine mod 2^32; and a same-offset XOR pad fitted from one source pair. Every selected original is separately withheld from its corresponding fit. No unknown per-output 128-bit parameter is allowed.

## Observed held-out outcomes

| Operator | Complete heldout predictions | Exact original selected matches |
|---|---:|---:|
| GF(2^128) affine | 432 | 0 |
| mod 2^128 affine | 448 | 0 |
| Four independent mod 2^32 affine lanes | 396 | 0 |
| Single shared XOR pad | 432 | 0 |
| **Total** | **1,708** | **0** |

The source-pinned Python SFT constructs and correctly recovers an independently planted GF(2^128) affine map, including **all 128 bits** of a third withheld synthetic selected record. The full original 1,708-check run returned zero complete matches, despite considering all historical alternative source combinations.

This excludes these particular **cross-domain common post-selection** affine/XOR maps for the named source variants and byte layouts. It does not rule out modality-specific operations, a source-labeled nonlinear transform, undisclosed transfer/copy state, other alternative records or a printer-specific producer. In particular, no source-validated mapping reaches selected ESC-N job0417 physical coupon, so this result does **not** nominate new K04 bytes or authenticate any K08 wording.

Reproducer: [source-pinned single-file test](../agents/agent11/selection_affine_all_sft.py).