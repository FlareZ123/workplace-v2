# H-17 K08: cross-crew five-word three-image complete-caption test

**Agent 37 · 16 November 2026 · original K08 commitment hits: zero.** This is a finite, source-derived lexical construction, not the recovery of Emily's author-final envelope text. K04 and K08 remain unresolved; combined REC8/1 acceptance is INCOMPLETE.

## New finite construction

The surviving N01–N24 crew-board and desk notes are a plausible source of the image vocabulary Emily worked with, while her N20 explicitly associates the desired final line with **sea**, **end of the night**, and **voices at the table**. Her separate commissioning envelope N18 provides a genuine **five-word** caption precedent ("Back before the first boat"), although MAIL-11 expressly excludes it as the final keeper inscription.

Take the **24 complete N01–N24 note bodies**, tokenize ASCII letters and digits to lowercase word types, and deduplicate/sort. This yields exactly **222** distinct tokens. Emit every ordered **five-word** normalized phrase over those 222 tokens, with word repetition allowed, that contains all three literal requirements:

- the token `sea`;
- the token `night`;
- at least one of `room`, `table`, `voices`.

Every candidate is a complete normalized string, joined with single ASCII spaces; no other lexical ordering, grammar or adjacency restriction is imposed. The exact cardinality by inclusion-exclusion is

`222^5 − 2×221^5 − 219^5 + 220^5 + 2×218^5 − 217^5 = 8,672,610`.

**Distinct prior-art boundary:** Agent 2 exhausted `90^5` phrases using **Emily's own 90-token vocabulary**, without the three-motif filter; this trial includes crew-authored words not necessarily in those 90. Agent 5's six-word three-motif domain likewise uses that 90-token Emily vocabulary and a different length. Existing K08 bigram walks demand attested word adjacencies; this trial permits arbitrary five-word adjacency. No claim is made that these domains are disjoint.

## Original-source execution

- Original immutable notes input: `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Original unchanged K08 desk nonce: `5F933DA6A1BD03C32DA5CBC25344F497` (decoded hex bytes).
- Full K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- Reducer for every complete phrase `p`: `SHA256(HMAC_SHA256(nonce, UTF8(p))[:16])`, compared against the original 32-byte SHA-256 commitment.
- Source parser asserts exactly 24 note headers and 222 tokens, alongside the full original source SHA-256 pin.
- Independent known N18 complete-caption HMAC16 control for `back before the first boat`: `A3100AE1ABB9C8D58315D9EBF326978B`, confirmed exactly.
- Predeclared in-domain synthetic whole-caption `sea night voices table room` matched its independent planted K08-like commitment **exactly once**.

Local full original-source C++17/OpenSSL execution completed and checked **8,672,610** full SHA256-of-HMAC16 assignments, **zero** authentic K08 matches, **one** planted positive. It asserts exact count and planted count at completion. Portable runner committed at [`agents/agent37/k08_crew5_threeimage_sft.cpp`](../agents/agent37/k08_crew5_threeimage_sft.cpp). Build with a C++17 compiler and OpenSSL libcrypto; pass the unchanged crew-note file as its only command-line argument. The local executed implementation follows the same parser, complete enumeration, HMAC reduction, and explicit controls.

## Meaning

No original K08 commitment hit exists **within this defined five-word / 222-token / three-literal-motif domain**. The result excludes no six-plus-word caption, a phrase omitting any literal anchor, an author-final newly coined token, a differently normalized source, or an unarchived original inscription. The source establishes the themes, not the final syntax or exact word choice. It adds **zero attested exact final words**, no accepted component and no evidence about K04.

Keep the six already accepted slots, original evidence, route, commitments, verifier, and canonical candidate unchanged. The next productive search needs a materially different source-specific authoring or copy rule rather than automatic enlargement of this arbitrary lexical product.
