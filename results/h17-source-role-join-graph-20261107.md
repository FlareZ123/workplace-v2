# H-17 source-role join graph: selected objects, custody edges, and missing byte links

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Status:** Source-role selection reproduced; K04 and K08 component bytes remain unrecovered.

## New result

A role-aware join across the printer, procedure, transfer, and keeper-caption sources exposes two important distinctions:

1. **K07 cannot be selected from the transfer audit's `COMMIT` marker alone.** The audit contains two non-dry-run `COMMIT` records for `IR-261003-H17`: `AX-7778` and `AX-7782`. `MAIL-13` explicitly identifies `AX-7782` as the final custodian handoff and classifies `AX-7778` as a drill. The custodian statement is therefore a necessary selector; `COMMIT` plus `dry_run=false` is only a validity condition.
2. **`MAIL-11` is a dual-role source.** Paragraph 1 is the RC-17 revision-C issue receipt (K06); paragraph 3 contains Emily's keeper-caption intent and excludes the old standby/commissioning labels (K08). A message-level classifier based on the technical subject would lose the K08 evidence. The paragraph spans must retain separate roles.

The K04 and K08 selectors also remain independent of byte integrity and exact wording respectively. The K04 header selects the correct dispatch event even if its payload is damaged or omitted; `MAIL-16` explicitly says an ACK is not a media-integrity flag. K08's final carrier is identified as the envelope margin, while the exact words are not quoted in the identified author-final units.

## Source-to-selected-object graph

| Slot | Selected object / role | Source evidence | Result and boundary |
|---|---|---|---|
| K04 | `ESC-N` job `PS-261003-0417`, attempt 2, `RECOVER/ACK` | `archive-labels.ini`; `MAIL-16` ¶2; spool line 131 | Selects `2026-10-03T18:02:00Z`, ACK2. The `261003` date token in the archive object ID is cross-checked against the envelope ID and the K02/K05 incident-day windows (both 2026-10-03), then matched to route window `2026-09-01_to_2026-10-03`; the August route is excluded. Payload is 16 bytes in the reconstruction, but its independent media integrity is unverified. |
| K06 | RC-17 revision C | `MAIL-11` ¶1; `document-register.log` | C is issued and retained. D-draft is a later review copy without issue authority. |
| K07 | Transfer `AX-7782` | `MAIL-13` ¶2; `transfer-audit.jsonl`; `queue-note.txt` | AX-7782 is the explicit final custodian handoff. AX-7778 is a drill despite also having a non-dry-run COMMIT; AX-7781 is a dry run; AX-7783 stopped before handoff. |
| K08 | Emily's final wording on the recovery-envelope margin | `MAIL-11` ¶3; notes N10/N20/N23; `MAIL-20` ¶2 | The final carrier is located, the old N17/N18 labels are excluded, and the normalization/HMAC rule is known. The exact final wording is not quoted in these source units. |

### Exact source units retained

The script records source-file SHA-256 values and zero-based byte spans (end-exclusive) for the relevant email paragraphs and note blocks. Its K04 route selector parses the six-digit date token in archive object ID `IR-261003-H17`, cross-checks it against envelope ID `H17-IR-261003` and the K02/K05 incident-day UTC windows, and selects the unique `archive-labels.ini` route interval covering 2026-10-03. The file also contains an August route; a section-order reversal leaves the October route selected. A synthetic August object/envelope plus August K02/K05 windows selects the historical route, while mismatched IDs/windows are rejected. The date-token interpretation is an explicit selector inference, corroborated by the independent route-window and incident-window records and MAIL-16's current-route statement. The principal spans are:

- `evidence/mail/11.eml`: ¶1 bytes 496–711 (K06 issue receipt); ¶3 bytes 989–1422 (K08 author-final intent). Same file SHA-256: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`.
- `evidence/mail/13.eml`: ¶2 bytes 485–744 (AX-7782 final handoff); ¶3 bytes 746–1004 (chunk ordering); ¶4 bytes 1006–1146 (handoff print left with ordinary records folder). Same file SHA-256: `80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa`.
- `evidence/mail/14.eml`: ¶3 bytes 841–1091 (WN-14 folder and Emily's notes beneath it, outside the controlled-copy sleeve).
- `evidence/mail/16.eml`: ¶2 bytes 633–905 (ESC-N/last-ACK selector); ¶3 bytes 907–1196 (ACK is not a media-integrity flag); ¶4 bytes 1198–1345 (ESC-S is excluded as an input to the keeper phrase).
- `evidence/mail/20.eml`: ¶2 bytes 696–1183 (exact final words matter); ¶3 bytes 1185–1396 (everyday notes included with technical material).
- `evidence/crew/noticeboard-and-desk-notes.txt`: N10 bytes 1180–1329 (photograph after the last cup); N20 bytes 2319–2483 (sea/end-of-night/voices-at-table brief); N23 bytes 2690–2826 (final wording is on the envelope margin). The graph also retains N17/N18 as excluded old labels, N09 as a galley-board caption, and N01/N03/N04/N08/N14 as photograph-caption inputs.

## Candidate ticket-to-spool locator (unverified)

A newly identified two-stage candidate can connect the supplier return tickets to printer-job IDs without conflating the ticket, PTW permit and spool namespaces:

- Candidate first stage: `ST-xxx → PTW-(xxx+304)`, supported by the separate permit/bay-order pattern in the PTW receipt export.
- Candidate second stage: `PTW → PS` with `+1` for FA-17/ESC-N and `+2` for LV-42/ESC-S. The print-fleet register's tab-05 anchors yield composite offsets `ST→PS +305` (ST-112→PS-0417) and `+306` (ST-142→PS-0448).
- Independent FA-17 L-28/A2 controls ST-087→PS-0392 and ST-098→PS-0403 are both retained ACK/RECOVER rows. The South non-anchor ST-121→PS-0427 is also ACK/RECOVER/desk, matching the ST-142→PS-0448 anchor. The three other predicted South jobs PS-0436/0441/0457 are outside the retained normal spool range and need native retrieval.
- North ST-112→PS-0417 places the tab-05 catch-cleaning ticket on the selected K04 logical job, whose selected event remains attempt 2 / RECOVER / ACK. The earlier PS-0416 ACK/RECOVER/bench record remains a useful adjacent same-role blind control; under the new candidate it is not an authenticated ST-112 destination.

The supplier CSV has no explicit PTW or PS foreign-key field, and the native SEP26 return index and queue/job manifest are absent. Therefore this is a **promising locator hypothesis**, not an authenticated join, a payload producer, or evidence that a physical coupon is attached to a ticket. A bounded six-control serial-seeded CPython/HMAC/BLAKE2 screen found no simple serial-derived payload producer; that negative does not challenge the locator itself. See [the full lane-specific offset screen and SFT](h17-k04-lane-specific-ticket-to-spool-offset-screen-20261107.md).

## Cross-slot ticket / book-page / spool-job index candidate

The L-29/N suffixes `81, 94, 99, 106, 112` and L-29/S suffixes `121, 130, 135, 142, 151` are the same values used in Praeger's 1947 third-edition North/South section-page hypothesis and in the lane-specific `ST→PS +305/+306` job locator. Cowper's *Sailing Tours* is named in the Riddle's yacht-library list, but every suffix 81–151 fits within both Part I (168 pages) and Part II (365 pages), so its proposed North→Part I / South→Part II assignment is non-discriminating. Wilson's 1934 guide is the closest identified physical-profile analogue to the novel's separate Little Drab Book. The two FA-17 L-28/A2 controls ST-087/ST-098 also map to candidate North pages 87/98 and predicted PS-0392/0403, both retained ACK/RECOVER rows.

This conjunction may be a shared index spine across K04 and K08. It remains unproven: the supplier CSV does not define ticket suffixes as page numbers or provide PTW/PS foreign keys; MAIL-09 does not identify Praeger or a page; the exact physical book and receipt position are unknown; and the two tab-05 offsets are calibrated from the known PS-0417/ST-112 and PS-0448/ST-142 anchors. Preserve the original book, receipt, return index, signed binder pages and native queue objects as separate carriers until an original source joins them. No page-word extraction or K08 phrase claim follows from this pattern. See [the cross-slot synthesis](h17-crossslot-ticket-book-page-spool-index-hypothesis-20261107.md).

## Custody edges and the unresolved join

The surviving text documents these edges:

- The **AX-7782 handoff print** was left with the ordinary records folder (`MAIL-13` ¶4). The message says the print contains only the reference and receipt chain, not the whole archive.
- The **WN-14 folder** was handed to the incoming watch with Emily's desk notes beneath it, outside the controlled-copy sleeve (`MAIL-14` ¶3). The photographs and galley captions were deliberately kept separate from the engineering procedure.
- Everyday notes were included with the technical material in bundle 06 (`MAIL-20` ¶3).

These statements support a documentary custody relationship among the WN-14 material, desk notes, envelope locator, and transfer handoff paperwork. They do **not** prove that the ordinary records folder and WN-14 folder are the same physical folder, that the AX-7782 data object itself was in the folder, or that the final envelope text is present in the bundle.

There is no local source unit binding the **FA-17 / ESC-N / L-29-N / H17-POL-17/A3 physical coupon** to that folder chain. Keep the K04 coupon, K08 envelope, AX-7782 handoff print, and AX-7782 data object as distinct carriers until a native index or attachment record establishes a join. In particular, do not infer that the K04 coupon is inside the WN-14 folder or AX-7782 object merely because their records appear in the same preservation bundle.

## Reproducible mutation tests

`work/h17_source_role_join_sft.py` runs eleven targeted regression checks. All passed against the uploaded archive:

- K04 route selection follows the archive-date interval when route sections are reversed.
- A synthetic August archive/envelope ID with matching K02/K05 dates selects the historical August route window.
- Mismatched archive ID, envelope ID and incident-day windows are rejected.
- K04 selector still chooses ACK2 when its payload is replaced with damaged text.
- K04 selector still chooses ACK2 when the payload field is omitted.
- K08 paragraph 3 remains discoverable after changing the technical email subject.
- K06 revision C remains selected over D-draft.
- Moving the D-draft timestamp later does not make it authorized.
- K07 selects AX-7782 over the higher-numbered aborted AX-7783.
- Removing the explicit custodian handoff statement produces no selected transfer.
- The transfer audit's non-dry-run COMMIT marker alone is detected as ambiguous (`AX-7778` and `AX-7782`).

The source ZIP SHA-256 is `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. The script emits the complete role graph as JSON, including source-file hashes and byte spans.

## Research consequence

This audit adds no candidate key bytes. It establishes a reproducible source-role selector, makes K04 route selection independent of INI section order, and closes a specific false shortcut in K07: a non-dry-run COMMIT is not enough without the final custodian receipt. It also makes the remaining K04/K08 boundaries explicit:

- **K04:** the selected dispatch event is known; the missing item is an independently authenticated physical/media copy of the coupon or a native printer-side object that validates its 16 bytes.
- **K08:** the selected carrier is the envelope margin; the missing item is the exact final wording or an authenticated version/attachment that contains it. The semantic brief and draft inputs are not a substitute for that text.

The script uses only source-role selection and small mutation controls; it does not add another generator, phrase, or hash-candidate sweep. It also does not resolve the previously identified mail-header/event-time anomalies. Selection authority and event chronology remain separate evidence dimensions.

## Reproduction

From the repository root:

```powershell
python work/h17_source_role_join_sft.py --root resources --archive C:\path\to\h17-archive-dump.zip
```

The script prints the JSON graph. Redirect stdout to a JSON file to preserve a run; pass the original ZIP to include its SHA-256.