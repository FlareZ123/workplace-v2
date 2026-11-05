# K08: original-crib periodic-key cancellation and complete caption recovery attempt

**Agent12 | 5 November 2026, 15:06 UTC | K08 still unresolved.** New target-reaching source transport test against exact original H17 K08 HMAC/SHA commitment. This improves on the concurrent generic binary-alphabet feasibility screen: it can recover **a shorter final text under any unknown repeating XOR or modular-add key** if the final text contains a sufficiently long exact phrase from Emily's source notes or the relevant correspondence. It does not assume the key values, a guessed full sentence, a source-to-text stylistic edit, or the target component.

## Source and key-independent mechanism

Original unmodified source: 42 files under `resources/evidence/`, 112,388 bytes. The recovered crew notes are SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. The source route's 16-byte desk nonce and original K08 full commitment are read exactly and pinned in the reproducer.

For an unknown p-byte XOR key repeated over an original byte stream `C`, the source-invariant identity is

```
C[i+p] XOR C[i] = P[i+p] XOR P[i].
```

For an additive byte pad, the analogous identity holds with unsigned differences mod 256. Both eliminate **every unknown key byte** without a brute-force key search. For every p in 1..8, construct a byte-difference stream of the original, then locate each source phrase's difference pattern with ordinary exact substring search. An exact hit fixes the p pad bytes; decode the surrounding uninterrupted ASCII sentence run (up to 160 bytes each way), generate its contiguous 2..32-word normalized spans, compute the original HMAC-SHA256 truncation and test the unchanged complete K08 slot SHA256.

**Crib choice:** 21 exact contiguous source excerpts from N01/N02/N06/N08/N09/N10/N13/N17/N18/N20 and MAIL11/20, including `at the end of the night`, `the voices at the table`, `people making room for each other`, `room for one another`, `the water outside`, `the next watch`, and both complete known earlier envelope labels. Include their source-case, lowercase, uppercase and sentence-capitalized presentations, deduplicated. Require crib length at least 2p. Ordinary zero-pad matches are omitted because exact plaintext windows were covered in earlier audits; the test asks whether a nonzero transform rescued any *additional* copy.

## Actual original result

| Source outcome | Exact assignments / checks |
|---|---:|
| Source files / total bytes | 42 / 112,388 |
| Nonzero-key crib-aligned carrier assignments | **8** |
| Full source-derived normalized candidate checks | **30** |
| Accepted original K08 complete candidate | **0** |

The eight apparent transforms are all ordinary **uppercase-vs-lowercase source phrase** differences rather than concealed terminal inscriptions: six in `crew/noticeboard-and-desk-notes.txt` (periods 5–7; examples `THE LAST CUP`, `THE WATER GIVES BACK`) and two in `mail/12.eml` (`THE LITTLE LAMP`). Their keys insert the ASCII case bit 0x20 on letter lanes and preserve the space lane. They yield no original K08 acceptance.

Two independent planted *complete* caption recoveries pass: an artificial 79-character crew-scene sentence hidden under an unknown period-4 **XOR** pad and separately under a period-4 **additive** pad. Each test derives the exact key from a source-style crib, expands the full artificial phrase, and accepts the independent artificial HMAC+SHA256 commitment (six equivalent crib/period detections each). N02's known original HMAC16 is an additional positive.

## Reproduction, caveat and consequence

[Read-only Python standard-library SFT](../agents/agent12/k08_crib_periodic_key_cancellation_sft.py) pins original crew-note SHA, nonce, target K08 commitment and exact test counts. No original source, route, acceptance, candidate or combined verifier was modified.

This is a finite, directly reconstructed **source-crib** transport exclusion. It is deliberately narrower than a general absence-of-cipher claim: a final caption with **none of those exact cribs**, a key period over eight, a varying pad, nonperiodic encoding, separated fragments, a custom text alphabet or external author-final paper inscription remains possible. It recovers no exact terminal caption word beyond original draft context. K04 remains without an authenticated selected original coupon; the canonical six other slots still PASS and combined REC8 remains INCOMPLETE.

For future research, this key-cancellation method is reusable if a genuinely new **long exact author-final excerpt** is found. Increasing an arbitrary phrase grammar or repeating these 21 known cribs without new source evidence is unlikely to help.