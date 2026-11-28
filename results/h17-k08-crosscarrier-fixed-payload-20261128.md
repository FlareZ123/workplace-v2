# K08: transfer-emitted PT removes the last heuristic stop choice from the N20 payload reconstruction

**Agent 2 | 28 November 2026 | target-blind fixed emitter improvement; K08 final wording still missing**

## Result

The recent overlap-chain reconstruction recovered the N20 payload

**the sea / the end of the night / and the / voices at the table**

and stopped at N20's sentence-two prefix **do not**. Its terminal PT address had been selected by a deterministic but still search-shaped rule: choose the earliest downstream repeated >=2-word N20 span after ET.

The independent transfer side-channel now removes that terminal search choice entirely.

A source-program path established in this invocation gives:

**ATTEMPT TAILBIT LOW IF EVEN -> AX-7782 mixed retry bytes -> 50D4 -> even-parity ASCII PT**

The resulting **PT** is not inferred from N20. Under the fixed A1Z26 note namespace it independently addresses **N16/N20**, whose unique maximal common span is **do not**. That is exactly the N20 sentence-two prefix at zero-based word 19.

The target-blind text path is now:

1. Source-selected TAILBIT/LEN emitter gives literal **AT**.
2. AT = N01/N20; unique maximal overlap = **the sea**, at N20 words 6..7.
3. Existing ATEALBIT LOW BIT calibration gives **M**; preserve T pivot -> **MT**.
4. MT = N13/N20; unique maximal overlap = **the end of the night**, N20 words 8..12.
5. LEN(MT span)=5 -> **E**; preserve T -> **ET**.
6. ET = N05/N20; unique maximal overlap = **and the**, N20 words 13..14.
7. Independent transfer channel emits **PT**.
8. PT = N16/N20; unique maximal overlap = **do not**, N20 words 19..20.
9. The source literal **BETWEEN** operation between ET and PT yields N20 words 15..18: **voices at the table**.
10. Concatenating N20 words 6 through 18 gives exactly:
   **the sea the end of the night and the voices at the table**
11. PT lands at the source-visible sentence-two prohibition boundary, so the payload terminates before **do not use the standby label just because it is shorter**.

## What changed

This is not a new phrase candidate. It strengthens the **emitter specification**.

Previously, PT was discovered by scanning downstream repeated spans and choosing the earliest eligible one. That rule was target-blind, but it was still a search policy over N20.

Now PT arrives from a different original carrier—the AX-7782 retry/tail-bit side-channel—under a separately reconstructed instruction and a parity decode. Therefore the full N20 middle payload and its stop boundary can be reproduced without consulting downstream span ordering to choose the terminal address.

This materially improves the fixed-rule status requested by the 28 November Critic direction. It still does not supply the author-final edit/version operation from this N20 semantic payload to Emily's actual keeper-envelope wording, and it does not recover the K08 component.

## Reproducer

`agents/agent2/k08_crosscarrier_fixed_payload_sft.py`

The SFT pins the original crew-note and transfer-audit sources, reproduces AT, MT, ET, the independent parity-framed PT, all four maximal overlaps, the exact N20 positions, and the final source-visible stop. It reads no K08 nonce, target commitment or candidate wording.
