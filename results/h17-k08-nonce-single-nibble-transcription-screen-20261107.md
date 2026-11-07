# K08 one-nibble desk-nonce transcription screen

**Date:** 7 November 2026  
**Agent:** Agent 42  
**Status:** bounded negative; nonce remains unauthenticated

## Question

The route file is the only surviving copy of the K08 desk_nonce. Could a simple transcription error in that 32-hex-character value explain why the previously enumerated literal spans from the supplied crew notes and galley/stores log do not match the K08 commitment?

This test changes only the nonce under a narrow, explicit transcription-error model. It does not generate new phrase candidates.

## Source set and reproducibility

The candidate generator reproduces the supplied-note screen:

- 24 N01-N24 entries, including each note body and author-plus-body variant;
- full labelled bodies and text after a label where present;
- seven galley/stores log entries, including full entry and text after the date label;
- every contiguous normalized span from 1 through 64 words;
- deduplication after the route's lowercase / ASCII-alphanumeric / whitespace normalization.

The candidate set was exactly **4,871** distinct normalized spans.

Pinned source SHA-256 values:

| Source | SHA-256 |
| --- | --- |
| evidence/crew/noticeboard-and-desk-notes.txt | 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb |
| evidence/crew/galley-and-stores.log | 23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46 |
| evidence/recovery-routing.json | f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5 |
| acceptance.json | 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f |

The reproducible implementation is agents/agent42/k08_nonce_typo_sft.py. It uses only the Python standard library and asserts the source hashes and 4,871-candidate count before testing.

## Nonce variants

The recorded nonce was:

5F933DA6A1BD03C32DA5CBC25344F497

The tested key set contained:

- the recorded nonce;
- all 480 single-hex-nibble substitutions (32 positions × 15 alternative hex digits);
- all 29 distinct adjacent-nibble transpositions.

Total: **510** distinct 16-byte key candidates.

For every phrase/key pair, the script computed the first 16 bytes of HMAC-SHA256(key, normalized_phrase) and compared SHA256(component) with acceptance.json:slot_sha256.K08.

## Result

**0 exact hits**

- Phrase candidates: **4,871**
- Nonce variants: **510**
- HMAC/commitment checks: **2,484,210**
- Exact K08 commitment hits: **0**

No candidate was promoted.

## Interpretation and limits

This closes the specific hypothesis that a **single incorrect hex digit** or **one adjacent-nibble transposition** in the recorded nonce restores a literal contiguous phrase from the supplied N01-N24 / galley-stores text set.

It does **not** authenticate the nonce. It does not exclude multiple-character transcription errors, a nonce copied from the wrong commissioning record, noncontiguous or rewritten wording, or text omitted from the export. The N23 margin, original envelope, photographs/galley captions and original nonce commissioning record remain absent.

Do not expand this into an unbounded nonce-typo search. The next high-value evidence is the original commissioning record for the nonce and the author-attributed final envelope/margin text; authenticate those two sources independently, then run the unchanged acceptance check once.
