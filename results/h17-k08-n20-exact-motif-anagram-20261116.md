# K08 N20 three-motif exact-word anagram: closed 13-word constructor (16 November 2026)

**Agent 40 | 51,891,840 distinct complete normalized phrases | original K08 hits 0 | independent planted whole-caption positive 1.** Six accepted slots unchanged; K04 and K08 missing, combined REC8/1 incomplete.

## Candidate mechanism

Emily's N20 note explicitly describes the final line as holding "the sea, the end of the night and the voices at the table." A hypothetical exact-word editorial process could reorder the *13 lowercase tokens* in that phrase while retaining all of them, with no added, dropped or replaced words. This source-limited multiset is:

`the sea the end of the night and the voices at the table`

Nine distinct token identities, with five occurrences of `the`, imply exactly `13!/5! = 51,891,840` unique whole-phrase permutations. This is a fully closed editorial hypothesis, **not** an attested source instruction, proven authorship rule, or claim about the missing final envelope margin.

The source-normalized tokens have no punctuation and single spaces. Consequently every permutation is already in the exact K08 normal form. For each unique permutation the tester applies original `HMAC-SHA256(desk_nonce, normalized_utf8)[:16]`, then full SHA256 to the 16-byte component, comparing to the unchanged original K08 commitment.

## Source, calibration and result

- Original notes file SHA256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, asserted by the C++ reproducer. N20's exact source sentence is also asserted.
- Original `desk_nonce`: `5F933DA6A1BD03C32DA5CBC25344F497`.
- Unchanged original K08 SHA256: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- Historical N02 first-draft HMAC16 control: `BF889359B0303F2B2B2FD96AE841210B`, PASS.
- A separately generated planted target from the source-ordered 13-word phrase is encountered exactly once by the same full HMAC16/SHA256 reduction path.
- Original 51,891,840 complete-candidate commitment comparisons: **zero**.
- Local source-pinned C++17 / OpenSSL execution on the unmodified uploaded 46-file ZIP's notes completed in 29.849 seconds.

Reproducer: [`agents/agent40/k08_n20_exact_anagram_sft.cpp`](../agents/agent40/k08_n20_exact_anagram_sft.cpp). It expects the original repository notes file by default; it may also take one input path argument. Its exact observed terminal line was:

`N20_TRIAD_ANAGRAM checked=51891840 expected=51891840 synthetic=1 original=0 seconds=29.849`

## Decision boundary

This excludes **only** captions made of precisely the 13 N20 motif tokens with the stated multiplicities. It does not exclude synonym edits, word insertions/deletions, shorter or longer wording, complete independent wording, another source carrier, or the physical final-envelope inscription. There is no evidence Emily chose a pure anagram rule. Do not widen this model into unconstrained motif synonym permutations: its value is a complete finite test of one distinct candidate mechanism rather than a claim about authorial history.

The other original six components and all source/acceptance/verifier files remain unchanged. K04's selected physical ESC-N coupon and K08's exact final author-selected caption remain unavailable; combined REC8/1 stays INCOMPLETE.
