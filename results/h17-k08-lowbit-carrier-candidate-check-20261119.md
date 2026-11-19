# K08 LOW BIT selected-carrier direct-adoption test — 19 November 2026

**Owner:** Agent 9  
**Hypothesis:** the LOW BIT route selects retained text carriers whose complete wording, or a complete sentence within them, was copied directly to the final envelope. The source-stage component map yields “Workshop to shelf”; the accepted-stage map yields “Workshop to desk”. The note HMAC cycle selects N12→N11→N13→N09, while K04 mask, K08 nonce and N20 route to N14, the Sunrise photograph. If the final phrase is directly adopted from one of those retained carriers, the unchanged K08 commitment must accept it.

## Frozen candidate family

Pinned inputs:

- crew notes SHA-256: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb
- recovery-routing SHA-256: f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5
- acceptance SHA-256: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f

Selected note carriers are N09 (galley-board caption), N10 (Emily's desk copy), N11 (mug-shelf card), N12 (workshop card), N13 (Emily reminiscence), N14 (sunrise photograph caption), N20 (Emily's intent brief), and N23 (Emily's margin/envelope note). The candidate set includes each full body, every complete sentence in those bodies, the source-stage and accepted-stage route strings, and the full N12→N11→N13→N09 cycle concatenation.

This is a role- and route-bounded direct-adoption test, not a phrase grammar. It does not generate paraphrases, reorder words, insert/delete words, or use any K08 acceptance-derived signal to select candidates.

## Result

**No direct adoption: 22 candidate records, 17 unique normalized strings; 0 matched K08.** The five duplicate records are the full-body/single-sentence overlap for N09, N11, N12, N13 and N14.

The complete per-candidate normalized text, HMAC16, component SHA-256, source note IDs and match flag are preserved in h17-k08-lowbit-carrier-candidate-check-20261119.json. Reproducer: agents/agent9/k08_lowbit_carrier_candidate_check.py.

The exact negative result rejects only direct adoption of a complete retained note body, a complete sentence from the selected carriers, either literal route instruction, or the concatenated four-note cycle. It does not reject an independently preserved photograph caption, a separate desk-copy file, the absent galley workbook, or an edit/copy operation not represented in the surviving text. The result is not a global probability and does not weaken the source-local locator findings.

## Consequence

The LOW BIT graph narrows the missing source object: the accepted-stage route points to Emily's desk copy (N10), while the independent photo convergence points to N14. The supplied notes do not contain the final wording verbatim. Further text construction from these same note bodies would retread the tested direct-adoption family. The next discriminating source is the original N10 desk-copy carrier, the N14 photo/caption original, or the bookmarked but absent R:/Stores/consumables/mug-stock.xls workbook. If the workbook is supplied, use work/h17_legacy_office_intake.py for read-only cell/formula/comment/defined-name and K08 HMAC scanning; it does not OCR embedded images/shapes/OLE objects.

No candidate, acceptance commitment, verifier, or original evidence was changed. K08 remains unresolved.
