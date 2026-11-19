# Conditional downstream factorial endpoint null for K08 LOW BIT (19 November 2026)

**Reproducer:** agents/agent9/k08_downstream_factorial_endpoint_null.py  
**Scope:** conditional on the already-derived CREW4/ALOWBIT front end. This is a downstream factorial sensitivity model, not a full upstream joint null or calibrated p-value.

## Enumerated space

The program verifies all six accepted component commitments, the K07 source-valid AX-7782 vector, the MAIL13 transfer receipt, and the source hashes. It then enumerates:

- 120 ordered assignments of three distinct accepted components;
- 60 bookmark mappings: 15 candidate positions × forward/reverse list direction × MAIL/NOTE namespace;
- 1,024 transfer/mask outputs: four retained transfer IDs × all 256 retry masks.

The full Cartesian space is **7,372,800 combinations**. Every component assignment, bookmark mapping, transfer/mask output, and alternate rendering is preserved in the JSON output.

## Endpoint counts

| Endpoint | Hits | Rate in 7,372,800-space |
|---|---:|---:|
| N11, using the fixed hex-ASCII LOW BIT selector | 195,840 | 17/640 |
| MAIL13, either item/direction mapping | 245,760 | 1/30 |
| Tea-room bookmark specifically mapping to MAIL13 | 122,880 | 1/60 |
| Transfer-ID selector returning bookmark 3 | 1,843,200 | 1/4 |
| **Joint N11 + tea-bookmark→MAIL13 + bookmark-3 return** | **1,536** | **1/4,800** |
| Joint event with source-valid mask 255 only | 24 | 1/307,200 |
| Joint event requiring exact 53D5 output | 192 | 1/38,400 |

The MAIL13 count is two of 60 mappings: forward position 13 maps the blank-request-form bookmark to MAIL13, while reverse position 3 maps the Tea-room stock sheets bookmark to MAIL13. Only the latter is the intended tea-bookmark loop. Correctly adjusted zero-based and one-based indexing produce the same normalized mapping; they are not independent extra trials.

## Rendering ambiguity in the 1,024 transfer/mask outputs

| Rendering / selector | Outputs reaching target |
|---|---:|
| Uppercase hex string LOW BIT → 11/N11 | 136/1,024 |
| Reversed hex string LOW BIT → 11 | 64/1,024 |
| Reversed hex string LOW BIT → 13 | 136/1,024 |
| Reversed byte-order hex LOW BIT → 11 | 32/1,024 |
| Packed raw-byte LSB selector → 3 | 320/1,024 |
| Printable-byte + decimal rendering LOW BIT → 13 | 16/1,024 |

For the source-valid AX-7782 mask 255, the packed bytes are 53D5. Under the fixed source-pipeline interpretation, uppercase hex 53D5 yields 11/N11. Other renderings of those same bytes yield reversed hex 5D35→13, reversed byte order D553→14, raw packed-byte LSB→3, and printable-byte/decimal S213→13. These are alternate interpretations of one output, not independent confirmations. The S213 path must not be promoted without its own source-authenticated rendering rule and matched controls.

## Interpretation and limits

The factorial result makes the endpoint frequencies explicit under a predeclared uniform control over component assignment, bookmark direction/namespace/position, transfer ID, and retry mask. It is conditional on the upstream author/row selection and uses the existing source-valid K07 rule as one distinguished mask. It does not incorporate the author-label permutation null or the N20 source-window null, and its independent uniform dimensions are a sensitivity model rather than a calibrated generative null. Do not multiply this result by the upstream 1/169,975,520 or 2/1,054 stage rates.

The operational K07 selector is reached by 24/120 component assignments; literal YEA is only 1/120. The selected tea bookmark maps to MAIL13 only under reverse order and MAIL namespace. The source-valid AX-7782 vector yields N11, but many counterfactual masks and alternate renderings also hit the same small selector space.

No K08 phrase is recovered. The N23 margin/envelope wording and mug-stock workbook remain absent. No protected-service access or new dispatch was used.


## 19 November erratum — NOTE namespace covers all 24 notes

The original 60-row mapping implementation applied the 15-mail formula `mapped = index` forward / `16-index` reverse to both namespaces. That incorrectly truncated the NOTE control to N01–N15 and omitted N16–N24. The reproducer has been corrected and now source-pins `crew/noticeboard-and-desk-notes.txt`, validates the complete N01–N24 stack, and uses:

- MAIL: forward position `i → MAIL-i`; reverse `i → MAIL-(16-i)`.
- NOTE: forward position `i → N-i`; reverse `i → N-(25-i)`.

Thus bookmark 3 maps to MAIL13 under reverse MAIL order (the tea-room endpoint), but to N22 under reverse NOTE order. The 60 raw control rows remain 15 positions × 2 directions × 2 namespaces. The downstream endpoint counts printed above are unchanged because its required tea-bookmark join is specifically to MAIL13; the NOTE matched-control identities and equivalence coverage are corrected. The result remains a conditional downstream factorial, not an upstream end-to-end null.

Reproducer correction: `agents/agent9/k08_downstream_factorial_endpoint_null.py` (Agent 9 commit `62336d68e4be8febc3ae8201732c2d70cf12b077`, regex correction `aece6243ee44fbc510ead8fc33b582eac5b6b43a`).
