# PTW-417 serial quartet as direct K04 coupon: bounded check

**Agent:** 9  
**Date:** 19 November 2026  
**Result:** 0 exact K04 commitment matches.

## Hypothesis

The K04 print job PS-261003-0417 and maintenance permit PTW-417 share suffix 0417. A simple cross-slot hypothesis is that the PTW-417 signed seal-serial quartet itself was the 16-byte physical coupon printed by PS-0417. The K04 route defines the component as coupon XOR the published 16-byte mask.

This check tests only that direct, source-linked construction. It does not search other encodings, transforms or producer models.

## Method

- Take the witness-walk order B,D,A,C from MAIL-04.
- Retain PTW-417 signed CLOSED AS_LEFT seal rows.
- Test the official K03 selection (highest revision at every bay).
- Also test the zero-based LOW-IF-EVEN side-channel candidates: lower revision at positions 0 and 2, higher revision at positions 1 and 3. Both A/rev1 rows are retained, producing two candidates.
- Interpret each eight-hex-digit serial suffix as four raw bytes, concatenate to a 16-byte coupon, XOR with the exact K04 route mask, and SHA-256 the result.
- Compare against the official K04 component commitment.

## Results

| Candidate | Coupon bytes | SHA-256 after mask | Match |
| --- | --- | --- | --- |
| Official highest revision | D7DAD6BC9714519B7DAD0AD4BE8E87FD | BA03876DD482CA591AFEF534A32BA7547ECCD7947FFB8B076B8FDF0C3A02327B | No |
| LOW-IF-EVEN, A/rev1 no-asset row | AD1D814B9714519B574A9232BE8E87FD | E4C4C827C8FD78AD66C9CD6B84213F8C0E67B6341374B134191826E90DFF64C2 | No |
| LOW-IF-EVEN, A/rev1 asset row | AD1D814B9714519B7E73B4CCBE8E87FD | 1B8C666CF400CBE7154E9F73A9817A5A065038436380DDD7EB8010AC5329718B | No |

**Three candidates; zero commitment matches.**

## Interpretation and limits

This rejects the direct serial-quartet-as-coupon hypothesis for the official PTW-417 quartet and both source-preserved LOW-IF-EVEN revision-1 variants. It does not reject a rendered coupon derived from other fields, a printer-specific transformation, a different physical media source, or a relation involving the spool/maintenance data beyond direct identity.

This is distinct from Agent44's direct PTW-quartet-to-PS-0417-payload screen and Agent14's p951 native-stage donor extension: those tested payload production and a hypothetical MT donor bridge, respectively. This test applies the K04 mask directly to the serial quartet and checks the official component commitment.

Reproduce with:

    python work/h17_k04_ptw417_serial_coupon_screen.py --evidence-root resources/evidence --acceptance resources/acceptance.json

No K04 value is recovered.
