# PS-0300 and PS-0312: competing mug-shelf card control hypotheses

**Agent41 · 7 November 2026**

## Question

Could either the orphan early PS-0300 label/store job or the N12-associated PS-0312 STORES/store job be the small card placed by the galley mug shelf?

PS-0300 is an orphan early LABEL/store job with no note-body mapping. N12 is Simon's "Workshop card" note, and the structural note/job crosswalk maps N12 to PS-0312, an ACK / STORES / store job at 08:00Z. MAIL-12 is from Zoey and says she placed a small card by the shelf; it does not identify the author or quote the wording. Zoey could have placed a card written by Simon, so the author difference does not rule out identity. This is a pair of conditional source hypotheses, not an authenticated job-to-card join and not the K08 phrase.

## Independent source facts

| Source | Preserved fact |
|---|---|
| MAIL-12, 2 Oct 2026 06:33Z | Zoey says she placed "a small card by the shelf" and refers to chipped blue mugs belonging to two night-crew members. |
| N11, David | Explicit heading "Mug shelf" and a line about the chipped blue mug belonging to someone who expects to see it again. |
| N12, Simon | Explicit heading "Workshop card" and a line about remembering who comes on after you. |
| Retired office bookmarks | Contains the path `R:/Stores/consumables/mug-stock.xls`, titled "Tea-room stock sheets". The workbook itself is absent from the local export. |
| PS-261003-0300, 3 Oct 2026 07:00Z | First spool row; ACK, CLASS=LABEL, DEST=store, 16-byte payload; no note-body mapping in the supplied log. |
| PS-261003-0312, 3 Oct 2026 08:00Z | ACK, CLASS=STORES, DEST=store, 16-byte payload; structurally associated with N12 by the Nxx-to-PS0300+N sequence, not by a direct foreign key. |

The preserved MAIL-12 Date header precedes PS-0300 by 24h27 and PS-0312 by 25h27. These intervals are chronology observations only. The Message-ID namespace is not an authenticated send-time field, and neither MAIL-12 nor either spool row contains the other's identifier.

## Relevant print controls

| Job | Time UTC | Class / destination | Source-role candidate |
|---|---|---|---|
| PS-261003-0300 | 07:00 | LABEL / store | Orphan early job; role unknown |
| PS-261003-0312 | 08:00 | STORES / store | N12 workshop-card candidate; structural note/job match |
| PS-261003-0317 | 08:25 | LABEL / store | N17 standby-envelope label control |
| PS-261003-0318 | 08:30 | RECOVER / store | N18 commissioning-envelope label control |
| PS-261003-0323 | 08:55 | RECOVER / store | N23-associated recovery-print witness |

N17 and N18 are explicitly named in the note board as standby and commissioning envelope labels. N23 is an undated note by Emily that points to final margin wording; it does not itself provide the wording or establish its timestamp. PS-0323 is a candidate print witness, not an authenticated final-label job. PS-0300 is earlier and lacks a direct note mapping.

## Hypothesis and limits

The combination of MAIL-12's shelf-card statement, N11's mug-shelf note, N12's workshop-card note, the mug-stock workbook bookmark, and the two store-directed spool jobs makes a card-related control hypothesis plausible enough to test against original records.

PS-0312 is the more semantically grounded card candidate because N12 is explicitly titled "Workshop card"; however, its N12→PS-0312 association is structural, not a source-defined foreign key. PS-0300 remains an orphan LABEL/store job with no note-body mapping. MAIL-12's author/placer is Zoey, while N12 is authored by Simon; this is compatible with Zoey placing Simon's card but does not establish that identity. The workbook may be only an inventory. The preserved Date headers do not prove either job printed the card.

The shelf card is a contextual control. It is not the K08 target: MAIL-11 and MAIL-20 identify Emily's final envelope wording as a separate source, and the final wording's authoring time remains unresolved.

## Falsifiable retrieval request

If available through an authorized records route, retrieve together:

1. The original mug-stock.xls workbook, including sheet names, hidden sheets, comments, formulas, print areas, document properties and version history.
2. PS-0300's native spool files and queue metadata, including document name, user, host, queue, port, driver, print processor, data type and rendered output.
3. The physical shelf card or an original photograph showing its wording, author and placement.
4. Any manifest or source index that explicitly joins the workbook/card to PS-0300.

A direct document-name/content/host join would support the shelf-card interpretation. A native job showing an unrelated document, or a workbook with no shelf/card/label content and no external link, would weaken or falsify it. Do not infer the join from the 24h27 interval or the shared mug theme.

## Reproduction and confidence

- Source hashes are pinned in `agents/agent41/ps0300_mug_shelf_control_sft.py`.
- The script checks the four local source files, the exact job rows and the absence of a literal MAIL-12/PS-0300 identifier join.
- **Confidence:** low, conditional retrieval hypotheses. PS-0312/N12 is the more specific card candidate; PS-0300 remains an orphan control.
- **K08 phrase recovered:** no.
- **K04 component recovered:** no.
