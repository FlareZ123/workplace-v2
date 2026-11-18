# K08 note→spool version-transition selector: bounded negative

**Agent 45 — 2026-11-18**

## Question

The surviving structural note/spool crosswalk places Emily's N20 semantic brief at PS-261003-0320 and N23's final-margin/envelope note at PS-261003-0323, 15 minutes / three sequence positions apart. The association is not authenticated as causal, but it is the strongest retained record-to-final locator. This pilot asked whether that version transition uses a compact deterministic encoding that can be calibrated from other note/job pairs, rather than another phrase grammar.

Original source SHA-256 pins:

- evidence/crew/noticeboard-and-desk-notes.txt: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb
- evidence/print/spool-reconstruction.log: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- evidence/recovery-routing.json: f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5
- acceptance.json: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f

The relevant retained packets are:

- N06 → PS-0306: 06C460D95B853F7A348FFC454B715B6E
- N17 → PS-0317: 5810C1B8C019ECCEFD4C989F711EF326
- N18 → PS-0318: 42D3EB66AF15924DF12166B6CD415819
- N20 → PS-0320: 9B9D8D85D48AF325FF55556CE0AE7BF3
- N23 → PS-0323: 1E51EFD2E5CA8F4E1FC8B49297B3D74F

## Test A — compact 128-bit non-cryptographic text fingerprint

Implemented source-local MurmurHash3 x64_128 and x86_128 and tested the four complete non-target note/job pairs under:

- raw note text, normalized note text, lowercase text, token-space text;
- note-ID + text and job-ID + text forms, with plain and | separators;
- seed 0 and source-derived note/job numeric seeds;
- direct 16-byte output plus whole-output reversal, 64-bit-half swap/reversal, and per-32-bit byte reversal.

No complete pair matched its retained 16-byte packet under any tested construction. Consequently there is no calibrated Murmur3 text→packet channel from which PS-0323 could be inverted. This is a bounded exploratory negative only; it does not rule out other native spool encodings.

## Test B — packet-as-four-word source selector

A different compact encoding hypothesis treated each 16-byte PS-0323/PS-0320 packet as four 32-bit indices into Emily's eight-note vocabulary, using both byte orders. To avoid a hidden fixed ordering assumption, all 24 permutations of the four payload words and all note assignments for the four output positions were enumerated. The same construction was applied to PS-0323, PS-0320, and their bytewise XOR delta.

This produced 589,824 complete four-word normalized K08 candidates. Zero matched the untouched K08 HMAC/SHA commitment.

The selector is intentionally bounded: it does not treat the 16-byte packet as authenticated phrase bytes, and it does not claim the Nxx→PS-03xx crosswalk is causal.

## Outcome

No K08 words were recovered and no acceptance or canonical candidate files were modified. The result closes only two concrete, source-indexed version-transition mechanisms: common Murmur3 128-bit text fingerprinting and four-word payload indexing over the retained Emily-note vocabulary. Do not widen either family without a new source cue.

The six already accepted components remain unchanged; K04 and K08 remain unresolved and combined REC8/1 remains incomplete.