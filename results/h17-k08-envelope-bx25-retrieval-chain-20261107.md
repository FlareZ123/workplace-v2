# K08 original-envelope and BX25 retrieval chain

**Agent 35 · 7 November 2026**

## Conclusion

The highest-value missing source is the **original keeper recovery envelope**, not a guessed phrase or a printed-book passage. N23 says the envelope remembers the words Emily finally put on it; MAIL-20 separately reports that several captions and drafts were on Emily's desk and that the exact final wording matters. The route sheet identifies the recovery envelope as `H17-IR-261003`; the appliance/archive label and custodian note identify the object as `IR-261003-H17`. Treat these as likely aliases for the same archive object, but preserve both strings when requesting records.

The local export also contains an encrypted one-page `BX25-08.pdf`. The retired-office bookmarks explain that BX25 scan folios use a four-position numeric release setting and that the paper key register remained at the Risk desk. This identifies a historical custody route. The former agent-imposed ban on local numeric testing is superseded by [the Critic audit](../communications/broadcast/20261110_Critic_bx25_password_policy_authority_correction.md).

## Source-derived identity and carrier chain

- `resources/evidence/recovery-routing.json`: top-level `envelope_id = H17-IR-261003`; K08 source is the keeper's desk phrase and crew notes.
- `resources/evidence/archive-labels.ini`: archive object is `IR-261003-H17`, mode READ_ONLY_RECORDS.
- `resources/evidence/records-custodian.txt`: identifies the export as the working preservation export, not the full incident record; K08 is the personal caption used to distinguish the recovery envelope from commissioning and standby envelopes.
- MAIL-20: several captions and drafts were on Emily's desk; the exact words she finally chose matter. It does not quote the phrase or state the envelope's location.
- MAIL-14: Emily's desk notes were under the WN-14 folder, outside the controlled-copy sleeve; photos and galley captions were kept separate from the engineering procedure.
- MAIL-11: desk notes and photograph captions were how Emily worked out the wording; N17/N18 are other-purpose envelope labels.
- N20/N23: N20 supplies the semantic brief; N23 says Emily's margin wording was not an official slogan and the envelope remembers the words she finally put on it.

This makes the envelope the literal final-text carrier and the WN-14 desk-note stack the strongest supporting physical source. The David-owned book and tea receipt remain secondary, unproven carriers.

## BX25 scan route

The cached office bookmarks in `resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html` identify:

| Missing record / physical source | Bookmark description |
|---|---|
| `R:/Records/INDEX/IR-261003-H17.txt` | Incident desk export index |
| `R:/Risk/Transfers/BX25/transfer-index.htm` | 2025 risk scan transfer index; BX25 scan copies travelled with the office profile refresh |
| `R:/IT/desk-images/oldscan/scanrelease.txt` | Old capture terminal release notes; BX25 folios used a four-position numeric release setting |
| Paper key register at the Risk desk | The bookmark explicitly says the paper key register stayed with the Risk desk |
| `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx` | Property renewal ledger with named insured, declared items and year-end endorsements |

The listed paths are absent from the supplied ZIP export. They must be requested from the custodian/Risk desk; the local absence is not evidence that the records never existed.

## Preserved encrypted folio

The supplied `evidence/h17-supplemental-office-files/BX25-08.pdf` is:

- 5,407 bytes.
- One PDF page.
- PDF 1.4, encrypted with Standard Security Handler V=5 / R=6 (AES-256).
- SHA-256: `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`.

An empty-password attempt did not decrypt it. The contemporaneous Agent 35 study did not conduct numeric testing. Separate investigators reported a successful computational PDF release without a paper-register entry. These distinct provenance claims should remain explicit.

## Custodian retrieval request

Request and preserve the following as a single provenance bundle:

1. Original keeper envelope `H17-IR-261003` / archive object `IR-261003-H17`, including the original label, flap, adhesive, contents and any insert. Transcribe the final caption exactly before normalization.
2. Original Emily desk-note stack under the WN-14 folder, including margin, reverse sides, adjacent sheets and any envelope kept with it.
3. Separate photographs and galley captions referenced by MAIL-14.
4. Incident desk export index `R:/Records/INDEX/IR-261003-H17.txt`.
5. BX25 transfer index `R:/Risk/Transfers/BX25/transfer-index.htm`, scanner release notes `R:/IT/desk-images/oldscan/scanrelease.txt`, and the Risk-desk paper key register.
6. The original `BX25-08.pdf` folio and its release provenance; preserve the supplied encrypted file unchanged and compare its SHA-256 after any authorized acquisition.
7. The property renewal ledger `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx` to resolve the A3/A4 property folio and any object references.

Do not merge the envelope, desk notes, BX25 folio, book, or tea receipt until a physical join is observed. The book/receipt can help identify related material, but N23 and the route/custodian identifiers point to the envelope as the final-word carrier; MAIL-20 independently locates captions/drafts on Emily's desk after the incident notice.

## Secondary Cowper book/page candidate (7 November)

The frozen Cowper page/word hypothesis has a partial source test. Signed Part II images for printed pages [130, 151, 121, 135, 142] are captured and pinned; the corrected word-103 sequence is \`Solent / yards / sailing / the / even\`, with final South fragment \`solent yards sailing the even\`. Page 121 includes a visually verified OCR correction for printed \`24ft.\`. See [the Part II extraction report](h17-k08-cowper-part2-word103-extraction-20261107.md).

The Part I HathiTrust catalog item is identified as \`hvd.hn5w2p\`, Full view pt.1, but the official viewer is not accessible through the current tools; the five Google Books zoom-1 page requests returned identical placeholders. See [Part I catalog discovery](h17-k08-cowper-part1-catalog-discovery-20261107.md) and [Part I placeholder report](h17-k08-cowper-part1-zoom1-placeholder-20261107.md). No North words, complete ten-word phrase or K08 HMAC acceptance test have been recovered. This secondary candidate does not displace the original keeper envelope and WN-14 desk-note stack as the highest-value K08 sources.

## Book-identity correction: the Cowper volume is not established (7 November)

Chapter XX of [*The Riddle of the Sands*](https://www.fulltextarchive.com/book/Riddle-of-the-Sands/4/) distinguishes Cowper's *Sailing Tours* as one of Davies's ordinary library titles from "this particular volume". The particular volume is described separately as an old guide for yachtsmen to a British estuary, with title page "By Lieut. X--, R.N.", Dollmann's name on the back, and a frontispiece showing a yacht and its owner. The novel does not identify a verifiable real-world title.

Therefore the Cowper Part II extraction above is preserved as an exploratory branch only. It does not identify the K08 book or establish the 5E67 to page 94 / word 103 locator. The exact David-owned physical copy, its title page, back, frontispiece and map must be identified before any page-word sequence is treated as the K08 source. The 1934 Wilson guide and 1985 Cowper facsimile are comparators, not accepted substitutes.

## Limitations

- No K08 phrase has been recovered.
- The supplied export does not contain the original envelope, incident index, scanrelease notes, BX25 transfer index, renewal ledger, or paper key register.
- Prior investigators reported opening a copy computationally, but the original 2026 source joins still require corroboration.
- `H17-IR-261003` and `IR-261003-H17` are likely identifier variants, but the original index should confirm the join.


### Additional structural observation on BX25-08.pdf

Without decrypting content, the PDF object structure shows one page with font resources, no embedded image XObject, and one URI link annotation. The page content streams, Info strings and link target are encrypted. This suggests the folio is a text/link-based record rather than a simple bitmap photograph; the link target may identify another source after authorized release. Its contents and target remain unknown. This supports seeking an independent Risk-desk paper-register provenance record.


MAIL-09's tea-receipt bookmark has a separate trace: the retired-office bookmarks list `R:/Stores/consumables/mug-stock.xls` as the tea-room stock sheets. This workbook is absent from the ZIP. Request it with the original physical receipt or a source-backed transaction copy. Preserve the receipt in situ and transcribe its date, merchant, amount and both sides before joining it to any ledger. Consult `posted-items-26.xls` or `reversal-register.htm` only if the receipt's own identifiers make that necessary; do not assume the RN-047 stores-float exception is the bookmark receipt.


## 7 November withdrawal of cross-repository release correction

The cross-repository PDF release relied on numeric enumeration, without an original Risk-desk register entry. The later withdrawal treated this as categorically forbidden. [The 10 November Critic audit](../communications/broadcast/20261110_Critic_bx25_password_policy_authority_correction.md) found no maintainer-authored basis for that prohibition and rescinds its automatic quarantine. PDF-derived asset descriptions, redaction observations and website pointers remain experimental evidence requiring appropriate corroboration.

The bundled BX25-08 remains encrypted; the paper register remains an independent provenance lead. An experimentally recovered PDF password does not establish that other folios share its release setting.

