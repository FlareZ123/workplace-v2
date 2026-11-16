# H-17 K08: source-irreducible nonminimal three-strand caption assembly

**Agent 34 · 16 November 2026 · Original K08 commitment matches: 0.** This was a complete targeted search of one explicit conditional authoring rule, not recovery of Emily's final words.

## Mechanism and prior-art boundary

N20 says Emily wanted to preserve a sea / end-of-night / people-at-table scene. The prior [three-strand minimum-SCS test](h17-k08-three-strand-scs-minimal-editor-20261115.md) covered only *shortest* order-preserving common supersequences of selected note fragments. This experiment tests exactly **one or two extra words** beyond the shortest possible combination, preserving all chosen source words and each source's ordering. At each step, emit one of the three current head words and simultaneously advance every strand that has that same head word. This canonical synchronous-merge rule eliminates redundant copies of the same word across strands. It is an exploratory editorial model; no retained record says Emily used this operator.

Frozen source selection: N01 sea-containing contiguous spans of 2–6 tokens (10 spans); N13 spans of 4–8 containing the exact “end of the night” (12); N20 spans of 4–8 containing the exact “voices at the table” (15). There are **1,800** triples. Only complete normalized outputs with length at most 17 words and length equal to the triple's shortest common supersequence length plus **one** or **two** are eligible. Earlier minimum-length outputs are excluded.

## Original acceptance run

| Complete construction | Full original-target checks | K08 matches |
| --- | ---: | ---: |
| Minimum length + 1 | **369,357,248** | **0** |
| Minimum length + 2 | **167,294,491** | **0** |
| **Total** | **536,651,739** | **0** |

A C++17/OpenSSL/OpenMP source-pinned enumerator executed every full candidate against the unchanged original target using the exact published K08 reduction: SHA256 of the first 16 bytes of HMAC-SHA256(raw 16-byte desk nonce, normalized UTF-8 phrase). It asserted both exact assignment counts. Its in-family planted phrase “and at sea looks the end of the night voices at the table” was found exactly once against an independently computed synthetic commitment. The original N02 HMAC16 control matched **BF889359B0303F2B2B2FD96AE841210B**; the optimized HMAC implementation matched OpenSSL's independent HMAC for the planted phrase. Total native execution: 348.612 seconds, five OpenMP threads.

An independently written standard-library Python DP census over all 1,800 source triples reproduced *both* exact candidate counts and the source/motif checks. The [executed C++17/OpenSSL scanner](../agents/agent34/k08_nonminimal_scs_original_sft.cpp) is now preserved in the repository. The [Python reproducer](../agents/agent34/k08_nonminimal_scs_reproducer.py) defaults to this quick DP census; its optional `--scan` flag recomputes exact original HMAC commitment checks, though Python runs much more slowly than the C++ implementation. Its default census was executed locally against the original extracted ZIP and passed. The full C++ exhaustive scanner ran separately.

Source SHA256 pins:
- Original notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Original route: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Original acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`
- Actual original K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

## Result and limitation

The tested nonminimal three-note interleaving operator yields no historical K08 solution. The output does not exclude a separately authored word, an edited/omitted photograph, longer or differently ordered text, or the absent final margin. All sources, original nonce, commitments, verifier, and canonical `candidate.json` remain unchanged. K01/K02/K03/K05/K06/K07 are accepted; K04 and K08 remain missing; the combined REC8/1 key remains **INCOMPLETE**.

A future investigation should prioritize a uniquely authenticated source-to-final version edge over adding another word-overlap dimension.