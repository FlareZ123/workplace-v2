# K08 crew-author bit selector: CREW4

**Date:** 2026-11-18  
**Status:** Source-local selector hypothesis; corroborative only, not a recovered K08 phrase.

## Question

Does the ordered author metadata in the 24 crew-board/desk notes contain a compact selector that identifies the owner of the unnamed map-back book mentioned in MAIL-09?

## Reproducible construction

Source: `resources/evidence/crew/noticeboard-and-desk-notes.txt`, entries N01–N24 in file order.

1. For each note, emit bit 1 if the named author is Emily and bit 0 otherwise.
2. Split the first 20 bits into four consecutive groups of five.
3. Interpret each group LSB-first as an integer 0–31; map 0–25 to A–Z.
4. Interpret the final four bits LSB-first as an integer.

The four five-bit values are 2, 17, 4, 22, giving **C R E W**. The final four bits are `0100` in source order, LSB-first value 4. The resulting selector is **CREW4**.

The first-appearance order of the six named authors in N01–N24 is Jason, Emily, Zoey, David, Gabriel, Simon. The fourth is David.

## Specificity check

Applying the same construction to a one-hot author predicate for each of the six authors gives:

| Bit is 1 when author is… | Decoded four letters + final nibble |
| --- | --- |
| Jason | BEQA0 |
| Emily | **CREW4** |
| Zoey | EIAB1 |
| David | IABI0 |
| Gabriel | QAIA8 |
| Simon | ACCA2 |

Only the Emily predicate yields the semantically legible selector CREW4. This is a bounded comparison over the six explicit authors, not an unrestricted search over encodings.

## Cross-record implication

MAIL-09 (`resources/evidence/mail/09.eml`) explicitly says the book with a map in the back belongs to David, not the communal shelf. The CREW4 output independently points to the fourth first-appearance author, David, and is consistent with that ownership statement.

This supports **David as the owner/selector for the unnamed map-back book**. It does not identify the book's title or edition, prove that the encoding was intentionally planted, select a page or coordinate system, or supply Emily's final envelope wording. The 1889 Falcon remains a candidate supported by separate edition/source work; CREW4 does not authenticate that title. Do not use this result to widen the already-frozen Falcon scan, introduce new book searches, or generate new K08 phrase candidates.

## Limitations

- The source does not specify the Emily/non-Emily bit predicate, LSB-first bit order, five-bit alphabet, or first-appearance author order as an encoding rule.
- The result is therefore a **selector hypothesis**, not a source-implied fact. The direct MAIL-09 ownership sentence remains the stronger evidence for David.
- No K08 HMAC was attempted: CREW4 is not asserted to be the keeper phrase.

## Reproduction

A minimal decoder is:

```python
def decode(bits):
    letters = []
    for i in range(0, 20, 5):
        value = sum(bits[i + j] << j for j in range(5))
        letters.append(chr(65 + value))
    suffix = sum(bits[20 + j] << j for j in range(4))
    return "".join(letters) + str(suffix)
```

The source author sequence and six-predicate outputs above are sufficient to reproduce the result.
