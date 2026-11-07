# K08 conditional N18→N23 same-route transport test

**Agent33 · 7 November 2026 · bounded negative; no final wording or accepted K08 component recovered.**

## Question

The new note-to-spool crosswalk associates Emily's commissioning-envelope label N18 with PS-261003-0318 and her final-margin locator N23 with PS-261003-0323. Both matched rows are `ATTEMPT=1 STATE=ACK CLASS=RECOVER DEST=store`.

Could the known N18 HMAC16 and its matched payload calibrate a route-specific transport pad, allowing the N23 payload to reveal the final K08 HMAC16? This is distinct from the earlier global N17/N18 label-pair calibration: those notes map to different `CLASS` values, while this test conditions on the common `RECOVER/store` tuple.

## Frozen source inputs

SHA256-pinned originals:

- Notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- Spool reconstruction: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- Recovery routing: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- Acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The N18 literal is “Back before the first boat.” Its route-normalized HMAC-SHA256 first 16 bytes reproduce the known control:

`A3100AE1ABB9C8D58315D9EBF326978B`

Matched spool values:

- PS-0318 / N18: `42D3EB66AF15924DF12166B6CD415819`
- PS-0323 / N23: `1E51EFD2E5CA8F4E1FC8B49297B3D74F`

The shared-tuple observation is direct in the retained rows. The Nxx→PS-(0300+N) association remains an inference: no supplied source explicitly binds the note IDs to these job IDs. The spool header also says payload integrity is unverified.

## Method

Using the known N18 HMAC16 and PS-0318 payload, derive the transform parameter and apply it to PS-0323. Test four fixed 16-byte layouts:

1. identity;
2. reverse four-byte word order;
3. reverse byte order within each four-byte word;
4. reverse all bytes.

For each layout test:

- one common 16-byte XOR pad;
- one 128-bit modular additive offset in big-endian order;
- one 128-bit modular additive offset in little-endian order;
- one independent bytewise additive offset modulo 256.

This produces 16 complete candidate HMAC16 values. Each is constructed before checking its SHA256 against the unchanged K08 commitment. The selected K04 payload is never read.

All 16 corresponding synthetic positive controls recover the planted target exactly. The N18 HMAC control and all four source-file hash pins pass.

## Result

**Zero of 16 candidates match** the original K08 commitment:

`285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

The identity-layout XOR model gives the clearest candidate:

- inferred common pad: `E1C3E18704AC5A987234BF5D3E67CF92`
- decoded N23 candidate: `FF920E55E166D5D66DFC0BCFA9D418DD`
- candidate SHA256: `20e16cd7ddae31644c3fcfff698edd871cb89996d7dadc7274ea46c91268a306`

The candidate is rejected. The additive models also produce no acceptance hit. Synthetic calibration: **16/16 PASS**.

Reproducer: [`agents/agent33/k08_note_spool_same_route_pad_sft.py`](../agents/agent33/k08_note_spool_same_route_pad_sft.py).

## Interpretation and limits

This closes the tested **shared class/destination pad or additive-offset family** for the inferred N18→0318 and N23→0323 pairing. It does not establish that the two notes were actually printed by the same physical device or queue. `DEST=store` is not a printer-host identity, and ACK establishes dispatch rather than media correctness.

The result does not exclude a per-job transform, nonlinear transport, a missing native print object, a different N23/job association, or the original physical envelope/margin. It does not recover any final K08 words. The next useful K08 evidence remains the native/rendered PS-0323 object with its queue/job manifest and independent output witness, or Emily's original envelope and WN-14 margin/version stack.

No original candidate, verifier, acceptance value, route file or evidence file was changed. Six individual slots remain PASS; K04 and K08 remain MISSING; combined acceptance remains INCOMPLETE.
