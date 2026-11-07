# K04: exact same-job earlier LABEL1 one-native-word copy-stage slip, full negative

**Agent 4 | 7 November 2026 | [32-job original GitHub Actions SUCCESS](https://github.com/FlareZ123/workplace-v2/actions/runs/42326424020) | 8,589,934,592 original K04 full SHA256 checks | 0 matches; 32/32 planted positives.** Original K01/K02/K03/K05/K06/K07 PASS, K04/K08 missing, combined INCOMPLETE.

## Historical source and precise candidate mechanism

Original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` contains *two* same-job records with prior ACK before the selected K04 recovery event:

- **16:45 UTC LABEL ACK attempt1**, `PS-261003-0417`, source buffer `E1E60D5F6B6DD2225FA6D5A2A63AD932`.
- **18:02 UTC RECOVER ACK attempt2**, same job `PS-261003-0417`, disputed copied buffer `A9A9DC5731A5E2AE879C47215C2559D5`.

An unproven same-job cache reuse/copy-stage misalignment might have transferred **three consecutive 4byte words from the earlier acknowledged LABEL output** into the subsequent RECOVER physical coupon with a one-native-word slip. This is specifically earlier *same-job* LABEL1 input, not the 18:01 RECOVER REQUESTED1 and 18:03 REQUESTED3 buffers already tested in Agent21's [four neighboring stage-shift families](h17-k04-adjacent-shift-one-word-exhaustive.md).

Freeze two complete candidate forms, each with 12 original bytes and 4 entirely arbitrary bytes:

1. **Prepend one output word:** `unknown4 || LABEL1[0:12]`.
2. **Append one output word:** `LABEL1[4:16] || unknown4`.

For every `unknown4 in {0,1}^32`, XOR each complete 16byte candidate buffer with untouched original K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C`; compare entire full SHA256 to unchanged commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. These exact candidate byte formats derive from the prior same-job buffer, and the selected disputed 18:02 copied buffer is **never read as a generator input**. No assumption about byte contents or PRNG recurrence is required for the missing 4byte word.

## Complete execution and audit

Read-only [source-pinned C++17/OpenSSL/OpenMP SFT](../agents/agent4/k04_earlier_label_overlap_sft.cpp), [32-job manual workflow](../.github/workflows/agent4-k04-earlier-label-offset-manual.yml), original [Actions run 42326424020](https://github.com/FlareZ123/workplace-v2/actions/runs/42326424020), head `15b5d977795d166d30d9a84b6df6ad3cf6ed1bf1`. Each side has 16 disjoint shards fixing the top four bits of the unknown 32bit word; each shard scans exactly `2^28=268,435,456` complete component assignments. Per-job source pins, exact selected and earlier physical record lines, original mask/commitment and **1024 complete SHA256 differential test messages**. Each shard constructs its own full planted target with an independently chosen 32bit word and requires exactly one synthetic positive.

Original 32/32 jobs completed success. Agent4 inspected the actual **32 distinct saved job logs** in two 16-job batches, not merely their CI statuses. Every log contains `SOURCE_SHA_AND_1024_COMPLETE_MESSAGE_CONTROLS_PASS`, a `SHARD_COMPLETE` with exact side/shard and `checks=268435456 original_hits=0 planted_hits=1`. Job inventory covers **(side,shard) ∈ {0,1}×{0..15}** with no missing/duplicate cases; neither batch had a discrepancy.

| Original scan family | Complete source-derived coupon candidates | Historical K04 matches | Synthetic exact positives |
| --- | ---: | ---: | ---: |
| Prepend one unknown native 32bit word to earlier LABEL1 first twelve bytes | 4,294,967,296 | 0 | 16 |
| Append one unknown native 32bit word to earlier LABEL1 last twelve bytes | 4,294,967,296 | 0 | 16 |
| **Combined, disjoint side assignments** | **8,589,934,592** | **0** | **32** |

## Interpretation

The historical K04 coupon is **not** any complete component produced by these two exact earlier same-job LABEL1 one-word-shift models under the original route mask. This is an exhaustive full-original-target exclusion, with a genuine source-selected earlier parent and exactly 32 complete planted positives. It does not prove the two source buffers share an underlying generator, that their printer copy states were causally connected, or that the printer had a one-word shifted copy fault. Other earlier record-derived transforms, noncontiguous source words, more unknown words, and wholly different physical media remain open.

The old selected copied buffer has no independent physical authenticity, so the negative does not establish a physical K04 bit. Original six slots remain PASS, exact K08 author-final caption missing, combined REC8/1 INCOMPLETE. No original inputs, verifier or accepted candidate were changed.
