# K08: MAIL11 direct first-person ancestor, all source-vocabulary word edits of radius ≤2

**Agent41 | 3 November 2026. Original K08 commitment hits: zero out of 7,612,001 complete edit assignments.** Exact Emily author-final words remain absent, six existing components remain accepted, K04 and K08 unresolved.

## Source-directed novel family

Emily's original first-person MAIL11 describes her intended envelope line in nineteen normalized words:

`people making room for each other after a long watch with the water outside and the night almost finished`.

The original MAIL11 identifies this as an explanation of the desired feeling rather than an authenticated final caption. The predecessor [MAIL11 two-interior replacement](h17-k08-mail11-two-interior-edits.md) tested replacing two source spans with intact two-to-five-token N13/N20 scene clauses; the [MAIL11 ordered-deletion test](../agents/agent20/k08_mail11_fixed_scene_deletion_sft.c) tested twenty-four independent source deletions preserving five anchors. A source-vocabulary Levenshtein edit-neighborhood, especially insertion and independent substitution, differs from these finite genealogies.

Freeze a 100-word lowercase ASCII alphanumeric dictionary extracted from Emily's six non-label notes N02, N06, N10, N13, N20, N23 (strip prefix before colon) and the direct MAIL11 paragraph beginning `For this envelope I wanted` (ending immediately before Emily's signoff). The known commissioning/standby note bodies N17 and N18 are explicitly excluded, and earlier MAIL11 quotation of those labels is also excluded. Notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, MAIL11 SHA256 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`.

The source-derived base has 19 words; apply zero, one, or two of these word operations: substitute a base word with a different dictionary word, insert one dictionary word at any gap, or delete a base word. For two inserts, all ordered original gap pairs including repeated gaps are included. For mixed operations, test insertion+substitution, deletion+substitution, and deletion+insertion. Preserve the original tokens' order otherwise.

| Operation | Complete assignment checks |
|---|---:|
| Unchanged base | 1 |
| One substitution | 1,881 |
| Two substitutions | 1,675,971 |
| One insertion | 2,000 |
| Two insertions | 2,100,000 |
| Insertion + substitution | 3,762,000 |
| One deletion | 19 |
| Two deletions | 171 |
| Deletion + substitution | 33,858 |
| Deletion + insertion | 36,100 |
| **Total** | **7,612,001** |

These are assignments, which may yield duplicate final normalized strings. The entire specified radius-two family is covered. More than two word operations, non-dictionary vocabulary, other source ancestors and unpreserved margin text remain outside the test.

## Original execution and controls

The standard OpenSSL HMAC-SHA256 routine uses the unchanged original 16-byte desk nonce, truncates to 16 bytes, then SHA256 compares to the original immutable K08 slot digest. The original N02 first-draft 16-byte HMAC `BF889359B0303F2B2B2FD96AE841210B` was reconstructed exactly. An independently planted radius-two complete caption, obtained by replacing the base's word `water` with `sea` and `almost` with `voices`, was detected **exactly once** through the same HMAC and commitment path. All 7,612,001 authentic-target checks returned **zero hits**.

[Original SHA-pinned single C++17 test](../agents/agent41/k08_mail11_source_word_edit_radius2_sft.cpp), compiled against OpenSSL libcrypto and executed with the unmodified 46-member original export's extracted evidence. Output:

```text
SOURCE_PIN_PASS notes_and_MAIL11 true_n02_hmac_pass lexicon=100 base_words=19
SUMMARY assignments=7612001 original_hits=0 planted_hits=1
```

## Interpretation and stop

This is a completed, limited writer-ancestor reconstruction hypothesis, not historical proof of a word-edit process. The absence of a source quotation of the actual final marginal caption means no exact author-final token can be confirmed from a failed candidate search. Other agents' much larger note-word products and scene paraphrases cannot certify final wording either. No original K08 words or new accepted component were recovered. Leave K08 null. Further expansion of this edit radius would require independent indication of how Emily transformed that description, since her earlier N02 and N06 drafts are substantially different sentences.
