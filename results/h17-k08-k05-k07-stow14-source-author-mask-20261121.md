# H-17 K08: K05–K07 sender union decodes STOW14 and returns to David's MAIL-14

**Agent 22 | 21 November 2026 | Source-local routing hypothesis; K08 still missing**

## New construction

A second readable code occurs in the 24 original crew-note author tags using exactly the prior Emily-author CREW4 encoding: four consecutive A=0 five-bit letters, read LSB-first, followed by a four-bit LSB-first numeric suffix.

The already accepted consecutive components K05, K06, K07 have directly identified original source-mail authors:

| Source component | Source email | Sender |
|---|---|---|
| K05, recorder | MAIL-10 | Simon |
| K06, RC-17 approved issue | MAIL-11 | Emily |
| K07, committed transfer | MAIL-13 | Gabriel |

In original N01..N24 order set each bit to 1 iff the note's author is Simon, Emily or Gabriel:

**010011100101110011010111**

First 20 bits as four five-bit little-endian A=0 symbols give **18,19,14,22 = STOW**; last four bits give **14**. Result: **STOW14**. There are also exactly 14 crew notes by these three selected authors.

Separately, the existing Emily-only source-author encoding gives CREW4, selecting fourth-first-appearance author **David**. STOW14 plausibly names original **MAIL-14**, whose sender is **David**. In that source David explicitly says Emily's desk notes were stored **under** the signed WN-14 watch folder, outside its controlled-copy sleeve; it also mentions the photographs and galley captions being kept separately from engineering procedures. The two decoded address/author paths converge on a real recorded paper-stowage statement.

## Exact conditional specificity

The SFT fixes the eight original Emily positions used for CREW4 and allocates the six Gabriel/Simon positions to any six of the other 16 note positions. Exactly **one of 8008** allocations decodes STOW14; exactly **three of 8008** spell STOW with any suffix. This is a finite conditional comparator for that predeclared author-position structure; it is *not* a calibrated p-value after accounting for multiple possible selectors, alphabets, textual interpretations and source joins.

The source neither explicitly defines the 3-author union as a cipher nor distinguishes MAIL-14 from N14/WN-14 as the intended destination. MAIL-14's direct statement about the loose notes is independently stronger evidence than the constructed locator. This finding does not contain Emily's final inscription, authentic K04 bytes or a K08 HMAC commitment hit. Official REC8/1 remains six PASS, K04/K08 MISSING, combined INCOMPLETE.

## Reproducer

Source-pinned Python SFT: [agents/agent22/k08_stow14_author_mask_sft.py](../agents/agent22/k08_stow14_author_mask_sft.py). It reads only the exact original crew notes and MAIL-10/11/13/14, tests the two author masks and mail joins, and exhaustively enumerates all 8008 six-position assignments. Tested successfully against the unmodified supplied ZIP source contents.

No source records, candidate, acceptance data, routing, or verifier were changed.
