# K04: ST–PTW–PS offset ambiguity and the +304 alternative

**Status:** source-index hypothesis only. No K04 component was recovered. Do not treat either offset as authoritative.

## Question

A current crosswalk hypothesis treats a supplier ticket `ST-nnn` as corresponding to printer job / permit `PS/PTW-(nnn+300)`. That mapping would make the high-leverage p951 gaps 43 and 96 correspond to `ST-043`, `ST-044`, and `ST-096`, with the selected `PS-0417` corresponding to `ST-117`.

A different constant offset, **+304**, fits the surviving FA-17 supplier-ticket evidence at least as well, and better on the older-month holdout. It changes the candidate missing ticket IDs to `ST-039`, `ST-040`, `ST-092`, and `ST-113`.

## Source observations

Files used:

- `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv`
- `resources/evidence/maintenance/seal-receipts.jsonl`
- `resources/evidence/print/spool-reconstruction.log`
- The L-29/N binder order in the print-fleet retirement note.

The receipt export contains **27 singleton permits PTW-390 through PTW-416**. Every one has a same-suffix printer job in the spool log: **27/27**. `PTW-417` is a separate multi-bay case with 17 receipt rows and should not be counted as an ordinary singleton bay record.

The posted FA-17 ticket sets are:

- L-29/N: `ST-094, ST-081, ST-106, ST-099, ST-112` (binder tab order).
- Earlier L-28 control: `ST-098, ST-087`.

The South LV-42 and Watch ST-09 ticket groups lie outside the PTW-390..416 range under both candidate offsets, so they do not distinguish +300 from +304.

## Competing mappings

| Evidence | Offset +300 | Offset +304 |
|---|---|---|
| L-29/N PTW matches | 4/5 | 4/5 |
| L-29/N distinct singleton bays | 4/4 | 4/4 |
| L-29/N matched bays in binder order, omitting ST-081 | A, C, D, B | A, B, C, D |
| L-28 FA-17 PTW holdout | 1/2 | 2/2 |
| L-29/N PS jobs present | 5/5 | 5/5 |
| L-28 PS jobs present | 2/2 | 2/2 |

Under **+300**, the four North tickets with singleton PTW matches map as follows:

- ST-094 lid plate → PTW-394, bay A
- ST-106 separator → PTW-406, bay C
- ST-099 hinge → PTW-399, bay D
- ST-112 catch → PTW-412, bay B

Under **+304**, they map as:

- ST-094 lid plate → PTW-398, bay A
- ST-106 separator → PTW-410, bay B
- ST-099 hinge → PTW-403, bay C
- ST-112 catch → PTW-416, bay D

The L-28 holdout is the main discriminator in the current local evidence:

- +300 maps ST-098 → PTW-398 (present), ST-087 → PTW-387 (absent from the receipt export).
- +304 maps ST-098 → PTW-402 (present), ST-087 → PTW-391 (present).

A bounded scan of offsets 200..400, ranking North PTW coverage, distinct bay coverage, then L-28 PTW holdout, puts **+304 first**. +300 is the next strongest candidate. This is evidence for investigating +304; it does not prove a numbering rule. Other offsets produce partial overlaps.

## Consequence for the proposed missing-ticket list

The p951 high-leverage gaps are printer job indices 43, 44, and 96, corresponding to PS-0343, PS-0344, and PS-0396. The selected job is PS-0417.

| Target job/gap | If +300 | If +304 |
|---|---:|---:|
| PS-0343 / gap 43 | ST-043 | ST-039 |
| PS-0344 / gap 44 | ST-044 | ST-040 |
| PS-0396 / gap 96 | ST-096 | ST-092 |
| PS-0417 / selected job | ST-117 | ST-113 |

The +304 mapping has an additional useful shape: the last listed North ticket, ST-112, maps to PTW-416, immediately before the special four-bay PTW-417 record and selected PS-0417. Under +300, ST-112 maps to PTW-412, leaving PTW-413..416 between that ticket and PTW-417. This adjacency is suggestive, not proof.

### Additional tab-05 class discriminator (Agent38, 7 November)

The print-fleet retirement note identifies North binder tab 05 as `ST-112` / `catch, clean`. Under +304, ST-112 maps to `PTW-416` and the corresponding `PS-0416` spool row is an `ACK CLASS=RECOVER`; under +300 it maps to `PTW-412` / `PS-0412`, whose row is `ACK CLASS=LABEL`. `PS-0416` is also the immediately preceding job suffix before the selected logical job `PS-0417`. This adds a source-grounded class/adjacency discriminator in favour of +304. It is still an inference from ticket description and spool class: no original ticket explicitly names PS-0416, and the PS-0417 name is reused for LABEL and RECOVER events. Do not treat this as authentication of the offset or as evidence that PS-0416 contains K04. The PS-0416 payload XOR the published mask does not pass the unchanged K04 commitment; it is not a substitute coupon.

## Cross-domain counterevidence: Praeger page-boundary fit

Agent35's separate K08 page-crosswalk report, `results/h17-k08-praeger-page-crosswalk-20261107.md`, finds that the L-29/N ticket suffixes 81/94/99/106/112 all fall in *The Volcanic North* (1947 Praeger edition, pp.62–118), while the L-29/S suffixes 121/130/135/142/151 fall in *The Silurian Region* (p.118 onward). This is itself a derived, unverified interpretation: no source says ST suffixes are book page numbers.

If that page-number interpretation is real, +300 maps selected PS-0417 to ST/page 117, the last page of *The Volcanic North*, immediately before the p.118 section boundary. +304 maps it to ST/page 113, which remains in the North section but loses the boundary coincidence. This is **secondary counterevidence in favour of +300**, and it offsets some of +304's better L-28 holdout and cleaner bay-order fit. The page locator is lower-confidence than an original ST↔PTW/PS pair and must not be used to select a ticket list without the physical book/index.

## Second book-page counterweight: Cowper Part I/II

Agent35's newer K08 synthesis identifies Frank Cowper's five-volume `Sailing Tours` as a stronger combined Riddle/ticket-volume candidate than Praeger: all L-29/N suffixes 81/94/99/106/112 fall within Part I (168 pages), while L-29/S suffixes 121/130/135/142/151 fall within Part II (365 pages). This remains a derived page-number interpretation; no source says ticket suffixes are book pages.

If that crosswalk is real, +304 maps selected PS-0417 to ST/page 113, immediately after the last North suffix ST-112, whereas +300 maps it to page117. This is a **weak adjacency counterweight in favour of +304**, complementary to the stronger PTW holdout/bay evidence. Praeger's single-volume boundary coincidence pulls the other way (+300→p.117 immediately before p.118). The two book hypotheses therefore do not independently settle the offset; keep both page clues low-confidence until the physical title/volume and original return index are authenticated. See `results/h17-k08-cowper-sailing-tours-volume-crosswalk-20261107.md`.

## Interpretation and next evidence

The raw observations support a **three-way numeric-index hypothesis** because PTW-390..416 and PS-0390..0416 align exactly, while the FA-17 ST tickets overlap that sequence under both +300 and +304. The local export contains no source record that explicitly pairs an ST ticket with a PTW permit or PS job.

The current Critic request for ST-043/ST-044/ST-096/ST-117 therefore depends on an unverified +300 assumption. The +304 alternative has better L-28 holdout coverage and a cleaner four-bay ordering. **Do not request only one inferred set.** First obtain the authoritative `R:/Stores/returns/SEP26/index.htm` return index or an original ticket showing its linked PTW/PS identifier. If that index cannot be recovered, request both candidate ID sets, including the original front/back, attachments, underlay, and any handwritten cross-reference.

A source-defined ST↔PTW/PS pair would settle the offset and turn the p951 gap IDs into a properly indexed acquisition request. Until then, ST-039/ST-040/ST-092/ST-113 and ST-043/ST-044/ST-096/ST-117 remain competing hypotheses.

## Reproduction

Run:

```text
python agents/agent12/st_ptw_ps_offset_scan.py
```

The script reads only the three local evidence files above and prints the offset ranking and the +300/+304 mappings. It performs no writes or network access.
