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


## Agent35 follow-on — latest signed closeout revision (2026-11-20)

The direct screen above retained signed CLOSED/AS_LEFT rows. PTW-417 also states that an earlier signed as-left record remains valid unless a later signed closeout replaces it. I therefore tested one additional source-selected candidate: the latest signed CLOSED record per bay, including the revision-4 REMOVED closeout rows, in the MAIL-04 field-sketch order B,D,A,C.

| Bay | Selected receipt | Serial |
|---|---|---|
| B | Rev 4, CLOSED/REMOVED, signed | SG-531FFABE |
| D | Rev 4, CLOSED/REMOVED, signed | SG-99AE58D8 |
| A | Rev 4, CLOSED/REMOVED, signed | SG-885464E5 |
| C | Rev 4, CLOSED/REMOVED, signed | SG-9BB5A10C |

The complete 16-byte coupon is `531FFABE99AE58D8885464E59BB5A10C`. XOR with the unchanged K04 mask gives `D6493275F8EEFF212D465E22CCAE4F10`; SHA-256 is `0541ad136c883eb52a43c962dabc0912901b115449f60f8e9be0239454579c33`, not the official K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Result: one additional complete candidate, zero K04 hits.** This does not establish a historical PTW-417 ↔ PS-0417 edge; the shared suffix remains a hypothesis, and the original missing-evidence request requires an independent cross-reference before treating the permit as the printer coupon. No further PTW/serial revision permutations are justified.


A second, explicitly cross-slot candidate applied the **already source-defined K03 reducer** to those same revision-4 serials: join the exact printed strings with `|` in B,D,A,C order, take SHA-256's first 16 bytes as the proposed coupon, then apply the K04 mask. The joined source text is `SG-531FFABE|SG-99AE58D8|SG-885464E5|SG-9BB5A10C`; proposed coupon `1F823ACDF7EA8E124EB98AF464389940`; masked component `9AD4F20696AA29EBEBABB0333323775C`; SHA-256 `30a64801a74e180ca6449678c33af6e4d1e85c226fb7ae01d00374255b7d9bc2`. This also fails the original K04 commitment. The K03 reducer is not specified for K04, so this remains a single cross-slot falsification, not a historical producer claim. No additional encodings are warranted.
