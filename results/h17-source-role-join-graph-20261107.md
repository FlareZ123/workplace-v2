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
| K04 | `ESC-N` job `PS-261003-0417`, attempt 2, `RECOVER/ACK` | `archive-labels.ini`; `MAIL-16` ¶2; spool line 131 | Selects `2026-10-03T18:02:00Z`, ACK2. The archive ID date token `261003` is interpreted as 2026-10-03 and matched to route window `2026-09-01_to_2026-10-03`; the August route is excluded. Payload is 16 bytes in the reconstruction, but its independent media integrity is unverified. |
| K06 | RC-17 revision C | `MAIL-11` ¶1; `document-register.log` | C is issued and retained. D-draft is a later review copy without issue authority. |
| K07 | Transfer `AX-7782` | `MAIL-13` ¶2; `transfer-audit.jsonl`; `queue-note.txt` | AX-7782 is the explicit final custodian handoff. AX-7778 is a drill despite also having a non-dry-run COMMIT; AX-7781 is a dry run; AX-7783 stopped before handoff. |
| K08 | Emily's final wording on the recovery-envelope margin | `MAIL-11` ¶3; notes N10/N20/N23; `MAIL-20` ¶2 | The final carrier is located, the old N17/N18 labels are excluded, and the normalization/HMAC rule is known. The exact final wording is not quoted in these source units. |

### Exact source units retained

The script records source-file SHA-256 values and zero-based byte spans (end-exclusive) for the relevant email paragraphs and note blocks. Its K04 route selector parses the six-digit date token in archive object ID `IR-261003-H17` as 2026-10-03 and selects the unique `archive-labels.ini` route interval covering that date. The file also contains an August route; a section-order reversal leaves the October route selected. This date-token interpretation is an explicit selector inference, corroborated by MAIL-16's current-route statement. The principal spans are:

- `evidence/mail/11.eml`: ¶1 bytes 496–711 (K06 issue receipt); ¶3 bytes 989–1422 (K08 author-final intent). Same file SHA-256: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`.
- `evidence/mail/13.eml`: ¶2 bytes 485–744 (AX-7782 final handoff); ¶3 bytes 746–1004 (chunk ordering); ¶4 bytes 1006–1146 (handoff print left with ordinary records folder). Same file SHA-256: `80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa`.
- `evidence/mail/14.eml`: ¶3 bytes 841–1091 (WN-14 folder and Emily's notes beneath it, outside the controlled-copy sleeve).
- `evidence/mail/16.eml`: ¶2 bytes 633–905 (ESC-N/last-ACK selector); ¶3 bytes 907–1196 (ACK is not a media-integrity flag); ¶4 bytes 1198–1345 (ESC-S is excluded as an input to the keeper phrase).
- `evidence/mail/20.eml`: ¶2 bytes 696–1183 (exact final words matter); ¶3 bytes 1185–1396 (everyday notes included with technical material).
- `evidence/crew/noticeboard-and-desk-notes.txt`: N10 bytes 1180–1329 (photograph after the last cup); N20 bytes 2319–2483 (sea/end-of-night/voices-at-table brief); N23 bytes 2690–2826 (final wording is on the envelope margin). The graph also retains N17/N18 as excluded old labels, N09 as a galley-board caption, and N01/N03/N04/N08/N14 as photograph-caption inputs.

## Custody edges and the unresolved join

The surviving text documents these edges:

- The **AX-7782 handoff print** was left with the ordinary records folder (`MAIL-13` ¶4). The message says the print contains only the reference and receipt chain, not the whole archive.
- The **WN-14 folder** was handed to the incoming watch with Emily's desk notes beneath it, outside the controlled-copy sleeve (`MAIL-14` ¶3). The photographs and galley captions were deliberately kept separate from the engineering procedure.
- Everyday notes were included with the technical material in bundle 06 (`MAIL-20` ¶3).

These statements support a documentary custody relationship among the WN-14 material, desk notes, envelope locator, and transfer handoff paperwork. They do **not** prove that the ordinary records folder and WN-14 folder are the same physical folder, that the AX-7782 data object itself was in the folder, or that the final envelope text is present in the bundle.

There is no local source unit binding the **FA-17 / ESC-N / L-29-N / H17-POL-17/A3 physical coupon** to that folder chain. Keep the K04 coupon, K08 envelope, AX-7782 handoff print, and AX-7782 data object as distinct carriers until a native index or attachment record establishes a join. In particular, do not infer that the K04 coupon is inside the WN-14 folder or AX-7782 object merely because their records appear in the same preservation bundle.

## Reproducible mutation tests

`work/h17_source_role_join_sft.py` runs ten targeted regression checks. All passed against the uploaded archive:

- K04 route selection follows the archive-date interval when route sections are reversed.
- A synthetic August archive ID selects the historical August route window.
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