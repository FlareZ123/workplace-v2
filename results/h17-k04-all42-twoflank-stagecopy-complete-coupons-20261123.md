# K04: source-consistent two-flank REQUESTED stage-copy generates three additional complete coupons

**Agent 31 | 23 November 2026 | Original K04 commitment NO_MATCH.** The historical K04 physical coupon is still missing; this reports an **exact original-source-compatible complete-value producer**, not a recovered ACK2 or authenticated print job. Original REC8/1 remains six individual PASS and combined INCOMPLETE.

## New target-bearing hypothesis

The original spool retains, for the exact selected job PS-261003-0417:

- **18:01 RECOVER/REQUESTED attempt1**, payload `CD3E4F216ADB2FB180DA2AA90B33F7A4`;
- **18:02 RECOVER/ACK attempt2**, selected by route but its **copied payload withheld entirely**;
- **18:03 RECOVER/REQUESTED attempt3**, payload `44D53DFC29D7943A95D89371DA58EC64`, expressly unacknowledged.

In the [all-42 original 528-word MT source-compatible chronology](h17-k04-all42-full-source-alternative-chronology-20261123.md), row128 starts at native stage951, omitted selected row129 at952, row130 at957 and row131 at961. Source-derived recurrence identities link the row128 group **[12,43,66,96,128]** and row130/131 group **[13,44,67,97,130,131]**. A two-group stage adjustment can move the latter REQUESTED into partial overlap with the selected output after the former REQUESTED. If so, one or more **complete four-native-word coupons** would be independently determined by intact spool words at the shifted boundaries, without any selected ACK2 copy bytes, long seed guesses or 2^32 free-word brute force.

This differs in **producer constraint** from generic aligned packet word mosaics: all 528 original words must jointly fit the entire symbolic MT state, and any complete coupon must have zero free MT bits at the exact potential selected output phase. Unlike the completed [one-unknown-word adjacent stages](h17-k04-adjacent-shift-one-word-exhaustive.md), these two-source joins can emit full coupon objects without one missing word. Some individual source packets and shifted-coupon families overlap historical tests, so **do not add these five raw candidates to a global purported disjoint search count**.

**Crucial limitation:** neither REQUESTED buffer has independent paper/media integrity, and the third is *later and unacknowledged*. Selected-to-flank native stage order is a speculative single-MT copy/emit model; it is **not** a historical authorization to use an unacknowledged request as the selected printed medium. The 18:02 original ACK2 physical coupon remains unauthenticated.

## Executed source-only selection and exact complete outputs

Freeze the all42 chronology and original source, then shift only the two named connected row-groups: delta128 in `-4..+1`, delta130 in `-5..+3`. Require monotone original packet stages and `row128 <= selected <= row130`; do not require every REQUESTED/ACK copy to advance four fresh native words, since the hypothesis specifically tests overlap/copy buffering. With original disputed row129 **omitted before its PAYLOAD is decoded**, invert tempering for the remaining 132 source packets, construct the 19,968-variable GF(2) MT recurrence, and reject any candidate stage assignment that contradicts an actual original packet bit.

- **54** source placement assignments satisfy the bounded monotone and selected-event chronology.
- **47** contradict the complete original source; **7** fit all 528 original native words, each with GF(2) rank **15,434**.
- For each of the seven, test *every* selected stage between its actual 18:01 and 18:03 packet starts: **44** conditional stages.
- Exactly **20** assignments specify all 128 selected native bits. These reduce to **five distinct complete 16-byte source coupons**.
- All five are tempered, serialized little-endian, XORed with the unchanged original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and subjected to the complete original 256-bit SHA256 commitment. **Zero authentic K04 matches**.

| Complete original-source coupon (16B hex) | K04 component after original XOR mask | Original commitment |
| --- | --- | --- |
| `CD3E4F216ADB2FB180DA2AA90B33F7A4` (REQUESTED1, existing control) | `486887EA0B9B884825C8106E5C2819B8` | NO_MATCH |
| **`6ADB2FB180DA2AA90B33F7A444D53DFC`** (two-flank join, 3+1 words) | `EF8DE77AE19A8D50AE21CD6313CED3E0` | **NO_MATCH** |
| **`80DA2AA90B33F7A444D53DFC29D7943A`** (two-flank join, 2+2 words) | `058CE2626A73505DE1C7073B7ECC7A26` | **NO_MATCH** |
| **`0B33F7A444D53DFC29D7943A95D89371`** (two-flank join, 1+3 words) | `8E653F6F25959A058CC5AEFDC2C37D6D` | **NO_MATCH** |
| `44D53DFC29D7943A95D89371DA58EC64` (REQUESTED3, existing control) | `C183F537489733C330CAA9B68D430278` | NO_MATCH |

The source tests use exact original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; the original K04 acceptance SHA256 is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

In the frozen all42 stage-952 family itself, 100 of 101 checked one-group source-compatible stage changes leave the selected first **96 bits** fixed to `6ADB2FB180DA2AA90B33F7A4`, with only a final 32-bit word unknown. That **entire 2^32 candidate superset was already exhaustively rejected** by Agent21's [four adjacent stage checks](h17-k04-adjacent-shift-one-word-exhaustive.md), independently of any seed initializer. The 101st one-group shift aliases the complete first request, also a recorded negative. We **stopped** a planned broader NumPy initialized-state sweep as logically target-redundant rather than consume compute on a previously exhausted value family. The distinct two-flank source-join pilots above are the direct resulting alternative.

## Reproduction, scope, next meaningful advance

[Read-only single-file reproducible Python test](../agents/agent31/k04_all42_twoflank_stagecopy_sft.py), standard library only (imports Agent1's original SHA-pinned all42 row parser and immutable stage constants), asserts counts, source ranks, all five output/coupon bytes, full original commitment misses and a synthetic full 16-byte positive. The local original-source run completed against the supplied original ZIP; the checked code was pushed to GitHub. No original input, route, verifier, acceptance commitment, or canonical candidate was altered.

The test **rules out these precise five complete source-produced coupons**, not every physically possible output, future MT stage, cross-source issuer or copy transformation. The more permissive 44 selected phases include candidates with **32, 64 or 96 unknown native bits**; no brute-force expansion was launched because without a new stage/producer/physical source discriminator, these return to already poorly evidenced large missing-word families. The hypothesized MT chronology and stage-copy behavior are not historically authenticated. Nothing here identifies Emily's exact K08 final caption.

A genuinely target-bearing next step still requires an independently witnessed selected attempt2 REQUESTED/print-media record, a source-authored short-entropy whole-coupon producer, or the original keeper caption inscription. The new coherent two-flank join itself yields **zero verified original K04 bits** outside its conditional model and **no seventh REC8/1 PASS**.
