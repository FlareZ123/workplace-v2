# K08 public Riddle-map colour-channel check — 2026-11-23

## Question

Could the publicly available map/chart plates from Erskine Childers, *The Riddle of the Sands* (1903), be the map-image carrier suggested by the K08 "A TEAL BIT" locator?

This is a bounded check of one existing literary candidate, not an assertion that David's physical book has been identified.

## Source basis

The local evidence provides two suggestive but non-identifying references:

- MAIL-06 mentions David's "Little Drab Book".
- MAIL-09 mentions a book belonging to David with a map in the back and a tea receipt used as a bookmark.

The public *Riddle of the Sands* text has a chapter titled "The Little Drab Book" and lists Map A, Chart A, Map B, Chart B, and a salvage-depot sketch. The CEDMagic page says its four printable map/chart plates are reproduced from the original prints in the book.

Sources:
- Project Gutenberg text, *The Riddle of the Sands*: https://www.gutenberg.org/ebooks/2360 (chapter XX and maps/charts list).
- CEDMagic map page: https://http.cedmagic.com/featured/riddle-sands/riddle-sands.html
- Pinned GITenberg source revision: https://github.com/GITenberg/The-Riddle-of-the-Sands_2360/tree/319919d550a9d5f959907ed8c75ca9509f3a56c1/2360-h/images

## Method

Retrieved and visually inspected the five image assets at the pinned GITenberg revision:

| Asset | Git blob SHA |
|---|---|
| `map-a.png` | `bd675c1593012e7992ee5e7bd45e90b31863e3dc` |
| `map-b.png` | `f79a652ddb86a42f17ba3fcff814eedcdd3d7f5d` |
| `chart-a.png` | `317af976071d26822139e9c4e7d123d6feb25013` |
| `chart-b.png` | `2a20cecc3a99b19855997ff0719d46ac0273a4f2` |
| `sketch.png` | `38f7b6fae0275f61d3b05b9406f67d65af751d0f` |

All five public scans render as monochrome/grayscale plates. None supplies a distinct teal colour plane. The check did not recolour, tint, or synthesize a channel.

## Result

**Negative for this specific carrier.** These public Riddle map/chart scans cannot substantiate a teal-channel LSB extraction: their visible content is grayscale, so treating one RGB channel as a special teal channel would add information that is not present in the source.

This does **not** establish that the Riddle is not David's physical book. A hand-coloured or annotated physical copy, a different edition, or a separate facility photograph could differ from the public scans. Nor does it recover or identify the K08 phrase.

## Consequence

Do not spend further effort extracting a "teal bit" from these five public scans. Keep *The Riddle of the Sands* as a literary locator only. The useful next source remains an independently identified image/card/book copy or the original photo-caption/profile archive; preserve colour and metadata rather than relying on public grayscale surrogates.

No candidate component, acceptance commitment, or verifier was changed.
