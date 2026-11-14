# K08 note-initialism phrase screen

**Status:** bounded negative; no accepted K08 phrase recovered.

## Source observation

After removing the short metadata prefixes (for example, “First draft for the crew board:” and “Mug shelf:”), the first words of notes N02, N06, N11, N13, N17, N18, N20 and N23 begin:

`A T E A L B I T`

That sequence is an anagram of **A BIT LATE**. This is an inferred clue, not a source-authenticated instruction or phrase. The selected set contains the mug-shelf note N11 as well as the desk drafts, photograph caption, envelope labels, semantic brief and final-margin note.

## Frozen test

Pinned inputs:
- `noticeboard-and-desk-notes.txt` SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `recovery-routing.json` SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json` SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`
- K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

The script uses the exact routing normalization and HMAC-SHA256 with the recorded K08 desk nonce, truncates to 16 bytes, then checks SHA-256 of those raw bytes against the unchanged commitment.

It tests:
1. Every eight-word phrase drawn from the 81 distinct tokens in the selected notes with initials `ATEALBIT`: **176,400** candidates.
2. Every eight-word phrase from the same vocabulary with initials `ABITLATE`: **176,400** candidates.
3. The specific one-word-per-note mapping in `ABITLATE` order `N02, N18, N20, N06, N17, N13, N23, N11`: **72** candidates.
4. The exact normalized phrases `a bit late` and `facts its a bit late`.

## Result

- Initialism-constrained phrase candidates: **352,800**; hits: **0**.
- Per-note one-word candidates: **72**; hits: **0**.
- Direct phrase checks: **0** hits.
- Synthetic positive controls: **2/2** initialism scanners passed.
- No source, routing, acceptance, verifier or candidate file was changed.

## Interpretation and boundary

The note initials form an interesting anagram, but the tested phrase constructions do not satisfy the K08 commitment. Do not promote “A BIT LATE” to a recovered phrase or treat it as proof of an ordering rule. This result excludes only the stated eight-word, selected-note-vocabulary constructions. It does not exclude an original caption with different wording, length, source or ordering.

Do not expand this into arbitrary note permutations or unrestricted phrase guessing. A further K08 attempt needs an independent source-defined ordering or a surviving final-caption carrier.
