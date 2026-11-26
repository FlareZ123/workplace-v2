# K08 N11 first-token convergence: ATEALBIT (2026-11-26)

## Finding

A second, independent reading of the already selected note sequence reproduces the existing `ATEALBIT` selector from note-body text, rather than from the author-position bit encoding used in the earlier CREW4 scan.

Take the first prose token from each note, stripping a short leading label before a colon where the note uses one (for example, `First draft for the crew board:` or `Mug shelf:`). In the base sequence

`N02, N06, N10, N13, N17, N18, N20, N23`

the first-token initials are:

`A T T A L B I T` → `ATTALBIT`.

Replace only `N10` with its adjacent note `N11`, yielding

`N02, N06, N11, N13, N17, N18, N20, N23`

and the first-token initials become:

`A T E A L B I T` → `ATEALBIT` (“A TEAL BIT”).

A bounded control over adjacent ±1 substitutions at each of the eight selected positions found this N10→N11 substitution to be the only one that produced the clear `ATEALBIT` reading; the other substitutions did not produce a comparably legible instruction. This is an independent convergence with the earlier author-position/low-bit `ATEALBIT` result, not a re-run of the note-body LSB serialization that Agent14 already tested.

## Source interpretation

The selected N11 note is headed “Mug shelf” and its prose concerns the chipped blue mug. N10 explicitly refers to the photograph after the last cup; N13 places mugs beside the window at the end of the night. Together, these make an N11/mug-shelf-associated image a plausible carrier for the “TEAL BIT” instruction. A low-bit extraction from a blue/teal image channel is therefore a source-grounded hypothesis worth retaining.

This does **not** prove that N11 is a photograph, that the image is the one Emily used, or that the phrase is encoded in its pixels. The local export contains no original photo, photo sidecar, or `mug-stock.xls` workbook. The K08 phrase has not been recovered and no HMAC/acceptance match was produced.

## Consequence for intake

The current `work/h17_k08_teal_bit_image_scan.py` has a source manifest gate pinned to N14. Do not weaken that gate or scan unrelated images. If an independently authorized original image or workbook object is supplied, first establish its exact source link to N11 and Emily’s final-caption workflow; then run only the already frozen teal-channel layouts against that hash-identified object. The M10 workbook locator remains conditional and should not be treated as evidence that the workbook contains the image.

This result should be considered alongside, not as a replacement for, the existing N14 photo hypothesis. It changes the priority of the next source request: obtain the N11/mug-shelf photo or a source-authenticated copy/sidecar from the relevant photo/profile archive, rather than broadening the public-map corpus.

## Reproducibility

The extraction is a deterministic read-only pass over `resources/evidence/crew/noticeboard-and-desk-notes.txt`, reproduced by [`work/h17_k08_first_token_acrostic.py`](../work/h17_k08_first_token_acrostic.py). It uses note IDs and first prose tokens only; no candidate phrase, K08 nonce, component bytes, acceptance digest, or secret-bearing diagnostic is written here. The result is a locator hypothesis, not a recovered component.
