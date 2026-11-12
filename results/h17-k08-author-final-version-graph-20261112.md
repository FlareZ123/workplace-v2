# K08 author-final version graph: exact carrier, excluded labels, missing ancestry edge

**Agent 4 · 12 November 2026 · source-pinned document/version analysis**

## Result

The final K08 carrier is the **recovery envelope**. MAIL-11 explicitly excludes Emily's two retained envelope labels (N17 standby and N18 commissioning). N23 refers to wording in her margin and says the envelope preserves the words she finally put on it; it does not establish whether that margin is on the envelope or on a separate desk note. No retained source node quotes the exact final-envelope wording.

This separates two questions that earlier phrase searches tended to conflate:

1. **Which document/version is final?** The personal caption on the recovery envelope, not N17 or N18. N23's margin is a reference/draft location; its physical relation to the envelope is not established.
2. **How was its text generated?** The surviving export does not identify the particular caption/draft Emily selected, the edits she made, or a complete final-envelope-caption exemplar. No source-grounded revision operator can currently be calibrated against an eligible same-operation final-envelope-caption holdout.

The source-pinned SFT is `agents/agent4/k08_version_graph_sft.py`. It builds the dated/undated node graph, pins the original source files, and asserts the explicit exclusions, custody statements, and absence of a complete final-margin text node. It does not generate phrase candidates or query the K08 commitment.

## Dated source graph

| UTC time | Source / author | What it establishes | What it does not establish |
|---|---|---|---|
| 1 Oct 2026 18:14 | MAIL-11 ¶3 / Emily | The selected envelope phrase is neither N17 nor N18; desk notes and photograph captions were wording inputs; intended scene is people making room after a long watch, water outside, night almost finished. | Exact words, a unique note/photo ID, or the date the final margin was written. |
| 2 Oct 2026 14:38 | MAIL-14 ¶3 / David | Emily's desk notes were under the WN-14 folder, outside the controlled-copy sleeve; photographs and galley captions were kept separate from the engineering procedure. | Named recipient, completed handoff time, or the envelope text. |
| 3 Oct 2026 17:31 | MAIL-17 / Emily | Emily would be in accommodation after dinner if the watch needed the previous note. | That the final envelope or her desk was in accommodation. |
| 3 Oct 2026 21:47 | MAIL-18 / David | Fire contained; incident team controlled access; no re-entry for records or personal belongings. | Where Emily's desk was, or whether it was inside the instrument store. |
| 4 Oct 2026 06:22 | MAIL-19 / Zoey | Spare radio chargers were at the accommodation desk. | That this was Emily's desk or that caption/envelope material was there. |
| 4 Oct 2026 11:06 | MAIL-20 ¶2 / Gabriel | Several captions and drafts were on Emily's desk; the exact words she chose matter. Header self-reference is `X-Records-Reference: MAIL-20`. | Exact phrase, desk location, caption IDs, or custody path after MAIL-18; no separate desk-note record. |

The galley log says chargers moved from the briefing room to the accommodation desk on 4 October. Together with MAIL-17/19 this makes accommodation a possible physical locator, but it still does not identify the desk in MAIL-20 as the accommodation desk. Do not promote that join to fact.

The note entries N01–N24 have no per-entry timestamps. Their numbering is not a source-authenticated chronology.

## Typed text nodes and eligibility

| Node | Author / role | Version status for K08 |
|---|---|---|
| N02 | Emily / first crew-board draft | Complete text, but a board draft rather than the final recovery-envelope margin. |
| N06 | Emily / second desk draft | Complete text, but still a draft; no authenticated word-for-word edit edge from N02. |
| N13 | Emily / reminiscence | Complete narrative, not a labelled final caption or envelope inscription. |
| N17 | Emily / standby-envelope label | Complete text, explicitly excluded by MAIL-11. |
| N18 | Emily / commissioning-envelope label | Complete text, explicitly excluded by MAIL-11. |
| N10 | Emily / desk-copy and photo reference | Identifies an unnumbered photograph after the last cup; does not quote the caption or identify the image. |
| N20 | Emily / authorial intent brief | Specifies sea, end of night, and voices at the table; not the final words. |
| N23 | Emily / margin reference | Says wording in her margin was not an official slogan and the envelope remembers the words she finally put on it; does not locate the margin or transcribe the inscription. |
| N01, N08, N09, N14 | Jason, Jason, Zoey, Gabriel / photo or galley captions | Potential source inputs, but not Emily-authored final text and not uniquely joined to the margin. |

**Eligible complete final-envelope-caption controls in the local export: 0.** N02/N06/N13 are complete but role-ineligible; N17/N18 are explicitly excluded; the third-party photo captions are possible antecedents only; N10/N20/N23 are context or carrier references rather than complete final wording. This is an evidence limitation, not a negative score for any text-generation model.

## The missing relation

The source gives a class-level statement—Emily worked from desk notes and photograph captions—but not the required individual edge:

`source caption/draft/margin-note ID → Emily's edit/version action → exact recovery-envelope inscription`

N10's “photograph after the last cup” does not uniquely identify N01, N08, N09, N14, or an omitted image. The separate retired-office-bookmarks file also lists R:/IT/desktop-move-2026.html (the first migration discriminator), R:/IT/desk-images/oldscan/scanrelease.txt, R:/Records/INDEX/IR-261003-H17.txt, R:/Stores/consumables/mug-stock.xls, and R:/Stores/returns/SEP26/index.htm. The mug-stock workbook and September returns index are the specific K08 profile-refresh candidates identified by the existing migration retrieval lead; these are historical retrieval pointers only, not file contents or proof that either contains the phrase. A previously circulated `desk-note-04` pointer was explicitly retracted: the original MAIL-20 header is `X-Records-Reference: MAIL-20`, and the supplied ZIP/repository contain no separate `desk-note-04` record. Do not confuse it with N04, which is David's numbered note. MAIL-14 confirms that the photo/caption archive was separate from the engineering procedure, but no surviving file supplies the caption revision history or its link to Emily's margin. MAIL-20 observes several drafts/captions on the desk without naming them. N23 identifies the final carrier but omits the words.

The K06 revision-C/D example in MAIL-11 is a useful contrast: its issue receipt explicitly distinguishes an issued revision from a later D-draft. That does not transfer a K06 procedure rule to K08; for K08 the source selects the envelope margin but supplies no equivalent complete version record.

## Recovery action

The only source-faithful route to exact K08 words is to recover one of the missing native carriers or an authenticated version copy:

1. Original recovery envelope, including both faces and the exact margin.
2. Original WN-14 folder and Emily's loose desk-note stack in original order, including reverse sides, adjacent sheets, pad leaf, insert, or backing that may preserve pressure indentations.
3. Separate pre-incident crew/noticeboard/galley photographs and caption records, with image originals, sidecars, author/editor identity, revision history, timestamps, and album/folder membership.
4. R:/IT/desktop-move-2026.html and its linked profile-refresh manifest/logs, to establish the historical R: mapping, migration method, store location, and file inclusion before selecting a cache source. Do not assume USMT or CSC; if R: was a mapped share and Offline Files was enabled, preserve the historical CSC tree before any synchronization or rebuild.
5. The K08 profile-refresh candidates R:/Stores/consumables/mug-stock.xls and R:/Stores/returns/SEP26/index.htm, plus the separate oldscan release notes and H-17 incident index, if an authorized preserved copy exists. Their bookmark entries do not establish contents or phrase linkage.
6. Incoming-watch WN-14 handoff and incident/property inventory records sufficient to link those physical items to the final envelope.

The existing [desk-caption custody bridge](h17-k08-desk-caption-postincident-custody-bridge-20261107.md), [pre-incident photo-caption acquisition rule](h17-k08-preincident-photo-caption-acquisition-20261107.md), [physical-carrier synthesis](h17-k08-physical-carrier-and-book-locator-synthesis-20261107.md), [profile-refresh migration lead](h17-profile-refresh-migration-store-retrieval-lead-20261107.md), and [R: / CSC retrieval gate](h17-r-drive-csc-offline-cache-retrieval-lead-20261107.md) provide the detailed acquisition boundaries. The custodian intake channel is closed; this result does not reopen it.

## Reproduction and status

From the repository root:

```bash
python agents/agent4/k08_version_graph_sft.py --root resources
```

The script checks source SHA-256 pins, the six mail timestamps, note roles, explicit N17/N18 exclusions, the WN-14 custody statement, the post-incident desk observation, the historical profile-refresh bookmark targets, and the absence of a complete Emily-authored final-envelope-caption node. It reports zero eligible complete final controls and does not calculate speculative HMAC candidates.

**Outcome:** final carrier and exclusions are source-supported; text-generation ancestry is not. **K08 remains MISSING; no candidate was promoted.** K01/K02/K03/K05/K06/K07 remain accepted, K04 remains independently unresolved, and combined REC8/1 remains INCOMPLETE. Original evidence, route, acceptance commitments, verifier, and canonical candidate were not modified.

### Source SHA-256 pins

- `evidence/mail/11.eml`: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`
- `evidence/mail/14.eml`: `9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5`
- `evidence/mail/17.eml`: `67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014`
- `evidence/mail/18.eml`: `7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0`
- `evidence/mail/19.eml`: `caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd`
- `evidence/mail/20.eml`: `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- `evidence/crew/noticeboard-and-desk-notes.txt`: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `evidence/crew/galley-and-stores.log`: `23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46`
- `evidence/h17-supplemental-office-files/retired-office-bookmarks.html`: `b9261ac17524e66bb5a6e3f3ce4996df65737aa34564b6d29a87ebab681a6096`
