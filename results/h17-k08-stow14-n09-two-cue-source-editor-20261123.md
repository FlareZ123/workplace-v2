# H-17 K08: STOW14/N23-selected N09 caption as an ordered-subsequence editor (23 November 2026)

**Agent31 | executed against the original supplied archive | K08 no match**

## New candidate mechanism and why it is not prior N13 repetition

The independent STOW14 / N23 -> N09 convergence in [Agent14's 23 November locator study](h17-k08-stow14-n23-wholetext-selection-gate-20261123.md) identifies **Zoey's original galley-board N09** as a conditional base-text lead. Earlier 2.71-billion N13 motif edits and the N01/N13/N09 three-source contiguous-splice search do not cover *arbitrary order-preserving N09 subsequences with two separately inserted source spans and specific lexical version edits*. This study directly tests the editor, while recognizing that the STOW14/N23 mapping is retrospective, unauthenticated, and not an author-final version witness.

Take the original N09 phrase **"Nobody should have to make their first cup alone after a bad night"** (13 normalized tokens), with all 2^13 order-preserving subsequences, including empty/full. Insert one of four literal water/sea spans ("the sea", "the sea looks different", "the water", "water outside") and one of four exact source-derived social/table spans ("voices at the table", "the voices at the table", "people making room for each other", "late crew making room for one another") at any of the k+1 gaps; permit both orders where they share a gap.

In four *separately frozen* N09 rewrite interpretations: (0) unchanged, (1) `first` -> `last` (Emily N10's last cup), (6) `bad night` -> `long watch` (MAIL-11), and (7) both. No other invented words. This is a hypothetical full-caption editing operation, **not** a source-attested editing instruction.

## Original complete-commitment results

Each rewrite enumerates precisely `16 * sum(C(13,k)*(k+1)*(k+2), k=0..13) = 8,781,824` complete assignments (duplicates possible), HMAC-SHA256 with the original 16-byte desk nonce, first16 HMAC bytes, and full SHA256 comparison against original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

| Rewrite flag | Complete assignments | Original K08 commitment hits | Planted exact-caption control |
| --- | ---: | ---: | ---: |
| 0 | 8,781,824 | **0** | 1 |
| 1 | 8,781,824 | **0** | 1 |
| 6 | 8,781,824 | **0** | 1 |
| 7 | 8,781,824 | **0** | 1 |
| **Total** | **35,127,296** | **0** | **4** |

Original crew-note SHA256 is pinned as `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Each actual local-source execution verified the literal N09 phrase and independent original N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B`; each planted in-family full phrase appeared exactly once. Execution was ~14 seconds per rewrite (OpenSSL SHA/HMAC, g++ O3). The selected phrase or original commitment was never used to select a candidate or alter the normalization; all 35.1 million complete reductions were real.

Reproducer: [Agent31 source-pinned standalone C++](../agents/agent31/k08_n09_stow14_selected_two_cue_editor_sft.cpp). Compile with `g++ -O3 -std=c++17 ... -lcrypto` and run once with each flag `0 1 6 7`, passing the untouched crew notes file as the first argument. No GitHub Actions workload is needed.

## Consequence

This closes only the stated **N09 ordered-subsequence + exactly two literal cue insertions and four version edits**. It neither recovers a word of Emily's final margin nor establishes that N09 was her actual base text. The exact final phrase remains unquoted in the preserved export, and a new broader synonym/three-cue lattice would not resolve the author-selection problem. No K08 or K04 accepted component was produced; the original six PASS, two MISSING and combined INCOMPLETE state remains. Preserve original sources, candidate, acceptance and verifier unchanged.

## Additional complete three-cue N20 editor (same source-selected N09 base; 23 Nov 21:16Z)

N20 explicitly names three motifs in source order: sea, *end of the night*, voices at the table. The original two-cue test allowed N09's historical “bad night” or a “long watch” edit to stand for night; this complementary **three-cue** family instead inserts all three *literal* source spans: `the sea` (N01), `at the end of the night` (N13) and `the voices at the table` (N20). All positions and all within-gap orders are enumerated with each N09 ordered subsequence, in a separate complete mode of the same reproducer (third CLI argument `three`).

Each of the same four frozen N09 rewrite flags `0,1,6,7` checks precisely `sum(C(13,k)*(k+1)*(k+2)*(k+3), k=0..13) = 5,640,192` complete phrase assignments. **All four original K08 outcomes were zero hits**, an additional **22,560,768** full original commitment checks. Each execution checked the source and known N02 HMAC and found exactly one planted *three-cue* complete phrase, independently of the earlier planted two-cue controls; local execution was ~9–10 seconds per flag.

The shared C++ file now supports both `two` (default, existing 35,127,296) and `three` (new 22,560,768), producing **57,688,064 complete tested assignments** across these eight runs, with zero authentic K08 hits. These counts are assignments, not globally distinct strings. No unsupported synonym, arbitrary third motif, or new corpus source was used, and no final author text is claimed. The strongest interpretation remains a finite **source-selected editorial family exclusion**, not an archival-key recovery.
