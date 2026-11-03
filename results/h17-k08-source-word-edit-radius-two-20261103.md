# K08: source-word Levenshtein-radius-two caption reconstruction

**Agent 24, 3 November 2026.** New target-facing word-level edit mechanism for the historical keeper caption. The original K08 HMAC and SHA256 commitment returned **zero matches among 207,068,260 complete candidate assignments**. This is a bounded negative, with a successful independent two-substitution planted control, and does not recover any original K08 word.

## Distinction from previous work

Agent5's N13 and MAIL11 two-interior-edit tests replaced each of two source intervals with an intact 2–5-word phrase. Agent3's ordered-subsequence and cross-crew two-interior tests use source-preserved spans and deletions. The present experiment instead enumerates **individual word substitutions, insertions and deletions**, including source-vocabulary single-word replacements that are excluded by the prior multiword-fragment-only mechanisms.

Possible ancestry candidates are Emily's full N02 first draft, N06 second draft, and N13 end-of-night prose; all are author-preserved historical text, though none is authenticated as the final K08 caption. The experiment deliberately uses no text of a missing original or semantic target wordlist. It tests a different, finite correction model motivated by the observed sequence of Emily's rewrites.

## Frozen input and construction

- Official crew notes: `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Source lexicon: exactly **355 distinct lowercase ASCII alphanumeric tokens of length >1** from the original non-N-header lines of the crew-notes file plus the post-header bodies of original MAIL11 and MAIL20. This intentionally excludes one-character inserted/replacement words such as `a` and `i`; unchanged original one-character words remain.
- Full original source sentence for N02, N06 or N13, normalized with ASCII-alphanumeric/whitespace tokenization.
- Allowed complete-candidate operations: one or two word substitutions at distinct original positions; two independently placed insertions (including the same original gap); one insertion and a substitution at any original position; one deletion and one insertion; one deletion and one substitution; two deletions. Changed/inserted words come from that fixed 355-token source vocabulary. There is no unknown-character guessing.
- Every generated phrase is fed to the **unchanged** K08 calculation: lowercase punctuation-to-space normalization, HMAC-SHA256 using the original decoded 16-byte desk nonce, first 16 bytes, and then SHA256 of those 16 bytes compared against the full original `K08` slot commitment. Same-string duplicates across assignments may occur, so these are **assignment counts** rather than certified unique normalized phrases.

## Completed exact-family results

| Source draft | One/two substitutions | Two insertions | Insert plus substitution | Deletion-involving edits | Total assignments | Original K08 hits |
|---|---:|---:|---:|---:|---:|---:|
| N02 (13 words) | 9,783,499 | 13,232,625 | 22,876,910 | 115,309 | 46,008,343 | 0 |
| N06 (11 words) | 6,896,274 | 9,829,950 | 16,588,440 | 81,950 | 33,396,614 | 0 |
| N13 (22 words) | 28,955,784 | 34,782,900 | 63,589,020 | 335,599 | 127,663,303 | 0 |
| **Total** | **45,635,557** | **57,845,475** | **103,054,370** | **532,858** | **207,068,260** | **0** |

The first source-substitution stage and the N02/N06 insertion/deletion stages completed in single local runs. The N13 two-insertion case completed as 34,782,900 checks; its insertion-plus-substitution search was split at original insertion gaps 0..10 and 11..22, producing 30,412,140 and 33,176,880 checks. All stages reported zero original acceptance matches. Counts for deletion-involving cases were corrected after noticing that comparing a mutable candidate against itself allowed redundant no-op substitutions; the final deletion counts above are from a corrected rerun and also agree with independent combinatorial counting.

**Controls:** The exact N02 first-draft HMAC first 16 bytes reproduced `BF889359B0303F2B2B2FD96AE841210B` using both OpenSSL HMAC and an independent precomputed-pad SHA256 implementation. A synthetically planted N13 phrase created by two changed words (first token `sea`, last token `table`) was recovered exactly once in the substitution family; a baseline source SHA256 check passed. The OpenSSL implementation computes the complete K08 slot SHA256 for every tested candidate.

Local SFT filename: `k08_two_word_substitutions_sft.cpp`, SHA256 `f6c390443967f61390c40c034b8a1c828d911aaa71e4e950fb6056799bc5a817`. It is a C++17 / OpenSSL libcrypto single-file program with `sub`, `2insert`, `ins-sub`, and `deletes` sharding controls. The tested local SFT was retained for transfer into shared work; use the frozen operation description and exact arithmetic above if reproducing separately.

## Interpretation and next crack

The three original Emily drafts are **not within two permitted source-vocabulary word edits of the historical normalized keeper caption**, conditional on the source choices and full acceptance commitment. This adds a specific editing-model exclusion to the older multiword-fragment and source-splicing experiments. The tested source vocabulary omits one-letter additions/replacements, and the construction does not cover three or more edits, other source antecedents, synonymous words absent from the selected corpus, or independent final composition. It supplies no authenticated final word and no K04 information.

Further blind widening of this same local edit radius is unlikely to be well-ranked given the substantial differences between N02 and N06. A more useful next experiment would identify a source-attested full-caption transformation or obtain a genuinely independent keeper-margin witness, then construct the complete candidate with an unseen holdout. Original six PASS, K04/K08 MISSING, combined INCOMPLETE.
