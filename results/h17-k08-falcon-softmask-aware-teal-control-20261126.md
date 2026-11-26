# Falcon rear-map soft-mask-aware teal-bit control (2026-11-26)

## Question

The 2026-11-23 native-JPX control tested the two rear-map JPEG2000 image objects from the public 1889 edition of *The Cruise of the Falcon*. It found raw teal-mask pixels but explicitly did not feed the PDF's separate soft-mask objects to the teal-bit decoder. This test closes that narrow gap: are those apparent teal pixels part of the visible map, or only pixels outside the PDF soft masks?

## Reproduction

Script: [agents/agent2/k08_falcon_softmask_aware_teal_control.py](../agents/agent2/k08_falcon_softmask_aware_teal_control.py)

Run from the repository root:

    python agents/agent2/k08_falcon_softmask_aware_teal_control.py --pdf /path/to/falcononbalticc00knig.pdf

The script loads the unchanged K08 nonce and commitment from resources, verifies the two JPX codestream hashes and decoded soft-mask pixel hashes, and applies the same source-literal teal-bit layouts as work/h17_k08_teal_bit_image_scan.py. It intersects the HSV teal gate with the PDF soft mask. It prints no candidate phrase or recovery component.

Public PDF SHA-256 used: 0f237b073f5768b77b5badc78836a76e35fc84cd67e5c3542175831b87564d3b. The two JPX codestream hashes match the 2026-11-23 native-JPX control.

## Results

| PDF page | JPX dimensions | Raw teal pixels | Visible teal pixels after soft mask | Raw candidate windows | Visible candidate windows | HMAC matches |
|---|---:|---:|---:|---:|---:|---:|
| 343 | 3626 × 2167 | 1,065 | 0 | 3 | 0 | 0 |
| 344 | 3595 × 2119 | 24,720 | 0 | 17 | 0 | 0 |

The page-343 soft mask has 577,353 nonzero pixels; page 344 has 566,243. The mask pixel hashes are pinned in the script. Both visible-only scans produce zero teal pixels, zero candidate windows and zero K08 HMAC matches.

## Conclusion

The raw teal pixels previously counted in both JPX objects are entirely outside their PDF soft masks. They are not visible map content. Consequently, the raw-JPX teal counts cannot support this Falcon rear map as a visible teal-bit carrier. This is a new mask-aware negative, not a K08 phrase recovery.

## Limits

- This tests the same public Falcon edition/codestreams as the prior native-JPX control; it does not authenticate that edition as David's physical book.
- It tests the frozen teal-channel/bit-parity layouts after applying the PDF soft masks. It does not treat the soft mask itself as an arbitrary standalone bitstream.
- It does not rule out the book as a page/word locator, another photograph or workbook as the teal carrier, or a different source-authenticated K08 mechanism.
- No acceptance file, verifier, canonical candidate or original evidence was changed.

## Research consequence

Do not repeat raw-JPX teal scans or spend further effort treating these transparent-region pixels as visible map content. Keep the Falcon book's possible locator role separate from the failed teal-carrier hypothesis. K08 remains unresolved pending a source-authenticated final caption/envelope or another complete-output construction.
