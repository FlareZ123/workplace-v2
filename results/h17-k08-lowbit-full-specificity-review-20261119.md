# K08 LOW BIT full source-preserving specificity review — 19 November 2026

**Owner:** Agent 9  
**Decision:** retain LOW BIT as a source-local locator hypothesis; do not promote it to a recovered K08 component or a complete phrase. K04 and K08 remain missing.

This review consolidates the existing upstream, component, transfer, print, bookmark, source-window, and downstream controls with two additional reproductions: a 16-way source-map operator sensitivity scan and a 200,000-trial within-author note-ID permutation null. It is a stratified specificity audit, **not a single calibrated global p-value**. The conditional controls reuse source records and selectors; their rates must not be multiplied.

## Frozen source and program set

The primary source files remain the official local export under resources/evidence/. Relevant pinned hashes include:

- crew/noticeboard-and-desk-notes.txt: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb
- recovery-routing.json: f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5
- telemetry/freeze-export.jsonl: 3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f
- transfers/transfer-audit.jsonl: 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf
- print/spool-reconstruction.log: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- acceptance.json: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f

Reusable source-pinned controls:

- agents/agent35/k08_crew4_four_variant_subset_scan.py — all four author encodings, all 8-of-24 subsets, and valid +1 edits.
- agents/agent9/k08_source_map_sensitivity.py — new source-map byte/hex/character-order alternatives.
- agents/agent9/k08_alowbit_splice_sensitivity.py — new complete 288-way contiguous 1+3+3 splice enumeration.
- agents/agent35/k08_component_half_bit_sensitivity.py — all 120 component orders under four half/byte-bit variants.
- agents/agent9/k08_lowbit_partial_controls.py — all 120 primary component orders, 1,024 transfer/mask outputs, and 133 print payloads.
- agents/agent9/k08_mail_bookmark_loop_controls.py — all 60 bookmark direction/namespace/position mappings.
- agents/agent9/k08_n20_source_triple_null.py — all 1,054 valid email/routing three-word windows.
- agents/agent9/k08_downstream_factorial_endpoint_null.py — the 7,372,800-combination conditional downstream factorial.
- agents/agent9/k08_note_order_null.py — new within-author note-ID permutation null; summary in results/h17-k08-note-order-null-20261119.json.

## 1. Author and row-selection front end

Agent35's four-variant subset scan finds two CREW4 subsets across A0_LSB, A0_MSB, A1_LSB, and A1_MSB:

- A0_LSB: the observed Emily positions N02, N06, N10, N13, N17, N18, N20, N23.
- A0_MSB: an alternate subset N04, N06, N10, N13, N16, N18, N19, N22.

Only the A0_LSB subset has a valid +1 edit that produces both ATEALBIT and the fixed-splice ALOWBIT. Across the two CREW4 subsets, this is one bridge among 2,941,884 variant/subset pairs. Agent35's specified upstream joint model gives 3 / 10,878,433,280; this is an upstream model-specific result, not a global K08 probability.

The selected Emily positions have seven valid sorted/unique +1 edits and seven valid -1 edits. N10→N11 is the unique +1 edit yielding ATEALBIT and the existing fixed splice ALOWBIT.

**New multiplicity correction:** for that selected edit, initials=ATEALBIT and count_letters=NLOWIF?V. Enumerating every contiguous 1+3+3 splice gives 288 possibilities, of which **two** yield ALOWBIT:

- initials[0] + count_letters[1:4] + initials[5:8];
- initials[3] + count_letters[1:4] + initials[5:8].

The repeated A at head positions 0 and 3 makes the splice non-unique. The row edit is unique under the tested +1 rule; the subsequent splice is not. The complete output is reproducible with agents/agent9/k08_alowbit_splice_sensitivity.py. The upstream joint null above does not correct for these 288 splice positions, -1 edits, or other untested grouping/operator conventions.

## 2. Source-map operator sensitivity

The baseline source map is reconstructed from accepted K01/K05/K06 bytes, the source-selected K02 telemetry raw block, and the source-valid AX-7782 K07 raw block:

K01→12, K02→11, K05→10, K06→10, K07→11.

The new reproducer enumerates 16 combinations of byte-bit order, packed-byte order, hex-character order, and character-weight order. The baseline mapping appears in **2/16** variants, not one. One is the ordinary LSB/forward/forward/LSB path; the other reverses hex-character order and character weighting, producing the same values. These are operator-sensitivity alternatives, not equally likely trials.

| # | Byte bits | Packed bytes | Hex chars | Character weights | K01/K02/K05/K06/K07 selectors |
|---:|---|---|---|---|---|
| 1 | LSB | forward | forward | LSB | 12 / 11 / 10 / 10 / 11 |
| 2 | LSB | forward | forward | MSB | 3 / 13 / 5 / 5 / 13 |
| 3 | LSB | forward | reverse | LSB | 3 / 13 / 5 / 5 / 13 |
| 4 | LSB | forward | reverse | MSB | 12 / 11 / 10 / 10 / 11 |
| 5 | LSB | reverse | forward | LSB | 3 / 14 / 10 / 10 / 14 |
| 6 | LSB | reverse | forward | MSB | 12 / 7 / 5 / 5 / 7 |
| 7 | LSB | reverse | reverse | LSB | 12 / 7 / 5 / 5 / 7 |
| 8 | LSB | reverse | reverse | MSB | 3 / 14 / 10 / 10 / 14 |
| 9 | MSB | forward | forward | LSB | 12 / 7 / 5 / 7 / 7 |
| 10 | MSB | forward | forward | MSB | 3 / 14 / 10 / 14 / 14 |
| 11 | MSB | forward | reverse | LSB | 3 / 14 / 10 / 14 / 14 |
| 12 | MSB | forward | reverse | MSB | 12 / 7 / 5 / 7 / 7 |
| 13 | MSB | reverse | forward | LSB | 3 / 13 / 5 / 13 / 13 |
| 14 | MSB | reverse | forward | MSB | 12 / 11 / 10 / 11 / 11 |
| 15 | MSB | reverse | reverse | LSB | 12 / 11 / 10 / 11 / 11 |
| 16 | MSB | reverse | reverse | MSB | 3 / 13 / 5 / 13 / 13 |

The baseline selector map therefore depends on a particular rendering/weighting convention, although one algebraically equivalent alternative reproduces it. No probability is assigned to these conventions.

## 3. Accepted-component assignment and half/bit choices

The six accepted components remain K01/K02/K03/K05/K06/K07. Agent35 enumerated all 120 ordered triples under four obvious half/byte-bit choices:

| Component half / bit order | Selector-7 triples | Literal YEA triples |
|---|---:|---:|
| Upper / LSB | 60/120 | 0 |
| Upper / MSB | 6/120 | 0 |
| Lower / LSB | 24/120 | 1/120 |
| Lower / MSB | 0/120 | 0 |

For the selected order K01/K06/K02, outputs are:

| Half / bit order | Raw bytes | Interpretation | Selector |
|---|---|---|---:|
| Upper / LSB | 0483F9 | non-text bytes | 6 |
| Upper / MSB | 20C19F | non-text bytes | 6 |
| Lower / LSB | 794561 | yEa | 7 |
| Lower / MSB | 9EA286 | non-text bytes | 0 |

The literal yEa is selective under the lower/LSB interpretation, but the downstream mechanism uses numeric selector 7. That operational endpoint occurs in 24/120 lower/LSB assignments and 60/120 upper/LSB assignments. The source rationale for selecting the lower half must remain distinct from the rationale for taking byte low bits.

## 4. Transfer and print controls

All four retained transfer IDs and all 256 attempt-1/attempt-2 masks per transfer were enumerated. The source-required greatest-attempt vector is mask 255. Results for the fixed uppercase-hex LSB selector are:

| Transfer | Official mask selector | Masks reaching selector 11 | Exact 53D5 masks |
|---|---:|---:|---:|
| AX-7778 | 6 | 0/256 | 0/256 |
| AX-7781 | 3 | 72/256 | 0/256 |
| AX-7782 | 11 | 64/256 | 8/256 |
| AX-7783 | 5 | 0/256 | 0/256 |

Only AX-7782 mask 255 is the source-valid K07 vector; its raw bytes reproduce the accepted K07 commitment and lowpack to 53D5. AX-7781 is a dry-run control but still reaches selector 11 under 72/256 counterfactual masks. For AX-7782, 64/256 masks reach 11 and 8/256 yield exact 53D5; only one is source-valid.

Alternate renderings of the same official 53D5 bytes produce different endpoints:

- uppercase hex 53D5 → 11;
- reversed hex 5D35 → 13;
- reversed byte-order hex D553 → 14;
- packed-byte LSB selector → 3;
- printable-byte/decimal S213 → 13.

These are alternative interpretations of one byte pair, not independent confirmations. The full 133-row print-payload control finds 122/133 selectors in N01–N15, 13/133 in N05, four RECOVER payloads in N05, and five total payloads in N11. The selected PS-0417 RECOVER ACK is not unique under the selector.

## 5. Bookmark loop and endpoint factorial

The bookmark control enumerates 15 positions × forward/reverse direction × MAIL/NOTE namespace = 60 mappings. Two map to MAIL13:

- forward position 13: Blank request form → MAIL13;
- reverse position 3: Tea-room stock sheets → MAIL13.

Only the second is the proposed tea-bookmark loop. The reverse ordinal is inferred, and the browser bookmark and physical tea receipt are distinct source objects. The existing factorial normalizes zero-based versus one-based indexing consistently; those are not independent extra trials. Transfer-ID low-bit suffixes are AX-7778→7, AX-7781→11, AX-7782→3, AX-7783→11; only AX-7782 returns bookmark 3.

The existing downstream factorial explicitly enumerates 120 component assignments × 60 bookmark mappings × 1,024 transfer/mask outputs = **7,372,800 combinations**, conditional on the primary lower/LSB component interpretation and upstream CREW4/ALOWBIT construction:

| Endpoint | Hits | Rate in 7,372,800-space |
|---|---:|---:|
| N11 under the fixed hex-ASCII selector | 195,840 | 17/640 |
| MAIL13 mapping | 245,760 | 1/30 |
| Tea bookmark → MAIL13 | 122,880 | 1/60 |
| Transfer-ID selector returns bookmark 3 | 1,843,200 | 1/4 |
| Joint N11 + tea bookmark → MAIL13 + bookmark-3 return | 1,536 | 1/4,800 |
| Joint event with source-valid mask 255 only | 24 | 1/307,200 |
| Joint event requiring exact 53D5 | 192 | 1/38,400 |

The joint rates are conditional factorial frequencies, not global probabilities. Do not multiply them by the upstream joint null or the N20 source-window rate.

## 6. N20 source-window and N23/HMAC route

The complete source-window control covers 20 email bodies and every string value in recovery-routing.json: 961 email windows + 93 routing windows = **1,054 valid contiguous three-word windows**. Exactly two map N20 to end of the:

- MAIL11: long watch with → selectors 10/11/3;
- K08 rule: late watch rather → selectors 10/11/18.

The fixed 12/10/11 extraction yields the end of only at N20, and N20 is the only note whose own 12/10/11 positional triple self-repeats contiguously. This is a positional/self-repeat result, **not** a claim that the phrase the end of occurs nowhere else; N13 contains those words in ordinary prose.

Across all eight slot-source fields and all 26 routing strings, 15 strings are eligible for the short reduction; K08/source alone produces VLOWL → 12. The note HMAC graph has a unique fixed point at N19 with path 19→13→9→12→11 and head initials SANTE. N23's token words maps to 19; N20's token wanted also maps to 19. Those are the only LOW19 tokens in the 24 note bodies. N12's HMAC selector is 11, consistent with the LOW IF EVEN row transition.

This closes a source-local locator path to N23; it does not disclose the final words written in N23's margin/envelope. The existing pre-registered N13 complete-body candidate and the chain-generated short diagnostics (the end of, end of the, SANTE, SEAT, SEATS, IF EVEN, TEAM) all fail the unchanged K08 commitment.

## 7. Within-author note-ID permutation null

New reproducer: agents/agent9/k08_note_order_null.py. It permutes complete note bodies only among IDs with the same author. This preserves the exact author-label sequence/counts, all 24 source texts, and each body's word count, tokens, and HMAC selector, while disrupting only body-to-note-ID assignment. The full-chain predicate requires all observed author/row, N20, N23, source-reduction, and HMAC-fixed-point conditions together.

- Possible within-author permutations: **1,254,113,280**.
- Randomizations: **200,000**, four reproducible seeds (20261119–20261122).
- Full observed chain: **0/200,000**; approximate rule-of-three 95% upper bound 1.5×10⁻⁵ for this conditional shuffle model only.

Marginal stage hits (not independent and not to be multiplied):

| Predicate | Hits / 200,000 | Rate |
|---|---:|---:|
| David LOW | 33,156 | 16.578% |
| Unique Emily +1 ALOWBIT bridge | 10 | 0.005% |
| N20 positional / MAIL11+route calibration / self-repeat / motif / WANTED predicates | 25,121 each | 12.5605% each |
| N23 WORDS → 19 | 24,957 | 12.4785% |
| N23 word uniquely targets a single fixed point | 301 | 0.1505% |
| Unique N19/SANTE fixed point | 196 | 0.098% |
| SEATS→N23 and WANTED/WORDS-only LOW19 pair | 3,497 each | 1.7485% each |
| K08/source VLOWL→12 | 834 | 0.417% |
| K08 route-string unique hit | 808 | 0.404% |
| N12 HMAC→11 and even | 66,448 | 33.224% |

The observed note-ID arrangement is unusual under this conservative within-author shuffle, but the result is conditional on the observed author labels and fixed LOW BIT/operator choices. It does not account for post-hoc selection of the mechanism, splice positions, byte/hex conventions, or the separate component/transfer/bookmark choices. It is not a global p-value.

## 8. Direct adoption from LOW BIT-selected carriers

A separate source-to-final hypothesis was tested: the LOW BIT route selects a retained text carrier whose complete body or complete sentence was copied verbatim to the final envelope. The candidate family was frozen to full bodies and every complete sentence from N09/N10/N11/N12/N13/N14/N20/N23, the source-stage and accepted-stage route strings (“Workshop to shelf” and “Workshop to desk”), and the concatenated N12→N11→N13→N09 HMAC cycle. These carriers are selected by the existing workshop/shelf/desk role transition, four-note cycle and N14 Sunrise-photo convergence; no paraphrase, word edit or phrase grammar was added.

**Result: 22 candidate records representing 17 unique normalized strings; 0 K08 commitment matches.** Five records duplicate a one-sentence full body (N09/N11/N12/N13/N14). Full normalized text, HMAC16 and component SHA-256 for each candidate are in results/h17-k08-lowbit-carrier-candidate-check-20261119.json; reproducer: agents/agent9/k08_lowbit_carrier_candidate_check.py. This falsifies direct adoption from the retained note text and route strings only. It does not rule out a separate N10 desk-copy original, N14 photograph/caption original, the absent R:/Stores/consumables/mug-stock.xls workbook, or an edit/copy operation not represented in the surviving notes.

## Decision and next work

The benchmark supports a **specific source-local routing hypothesis**, not a recovered K08 phrase. The N20/N23 placement and HMAC route are more discriminating than the selector-only stages, but several upstream and operator choices remain post hoc or ambiguous: the ALOWBIT splice has two constructions; source-map conventions have 16 tested variants; selector 7 is common across component orders under some half/bit choices; transfer selector 11 is reachable under many counterfactual masks and alternate renderings; and bookmark reverse ordinal is inferred.

Do not add another locator chain, rotate to another phrase, or promote S213 as a second confirmation. Preserve the existing path at its demonstrated strength. The next productive event is an independently authorized local copy of the missing original wording carrier (N23 margin/envelope, separate photo/galley-caption carrier, or the bookmarked but absent R:/Stores/consumables/mug-stock.xls workbook) or other native source that actually contains the final text. If the workbook is supplied, use work/h17_legacy_office_intake.py for read-only cell/formula/comment/defined-name and K08 HMAC scanning; it does not OCR embedded images/shapes/OLE objects. The custodian reply channel remains closed; do not recontact it, access protected services, or operate facility equipment.

No candidate, acceptance commitment, verifier, or original source record was changed. The six accepted components remain K01/K02/K03/K05/K06/K07; K04/K08 remain missing; combined REC8/1 remains incomplete.
