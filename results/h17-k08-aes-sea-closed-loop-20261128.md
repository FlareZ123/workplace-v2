# K08: AES/SEA reversal closes the AT emitter loop through LOW and N07

**Agent 45 | 28 November 2026 | target-blind source-local operator calibration; K08 final wording remains unresolved**

## Question

The current K08 source chain emits the exact fragment whose final three words reduce under the already-established LOW BIT / LOW IF EVEN rule to the literal token `AES`. Prior work tested AES as a cryptographic instruction and found no accepted K04/K08 result. Does the same token instead participate in the already-established A1Z26 / note-count / LOW vocabulary?

## Frozen construction

This test reads only the SHA-pinned 24-note crew source. It never reads the K08 nonce, acceptance target, candidate file, printer data, or any PDF.

1. Interpret `AES` with the same A1Z26 note namespace already used by STOW and the AT/MT overlap chain: A/E/S -> N01/N05/N19.
2. Count normalized post-label words in those three notes using the existing alphanumeric tokenizer.
3. Under the existing A=0 count-to-letter convention, the counts are **11,14,22 -> LOW**.
4. Apply the already-established ASCII LOW BIT packing to `AES`: it yields **7**, selecting N07. N07's first three normalized words are a direct reversal instruction; the public report records their SHA-256 rather than reproducing the source wording.
5. Apply that reversal to `AES`, yielding `SEA`.
6. Re-run the same checks on `SEA`: A1Z26 S/E/A -> N19/N05/N01 has counts **22,14,11 -> WOL**, exactly the reversal of LOW; LOW BIT(`SEA`) is again 7.
7. Search the numbered-note corpus for the literal normalized token `sea`. It occurs in exactly **N01 and N20**. Their IDs map back to **AT**, the independent literal token already emitted by TAILBIT/LEN.

## Result

The source-local loop is therefore:

`AT -> [unique N01/N20 overlap] -> SEA <-> AES -> LOW -> N07 reversal instruction -> SEA -> N01/N20 -> AT`

The reversal is checked in two independent source representations:

- token order: `AES <-> SEA`;
- note-count letters: `LOW <-> WOL`.

Both `AES` and `SEA` have LOW BIT value 7 and therefore select the same N07 instruction.

As a finite denominator, exactly **36** ordered note triples have the count vector 11/14/22 that maps to LOW, and 36 have the reversed vector 22/14/11 that maps to WOL. The `AES` token is not selected from those 36 possibilities: it was emitted independently upstream. The corpus occurrence step is stronger: literal `sea` occurs in exactly two numbered notes, N01/N20, giving AT with no choice.

## Consequence

This supplies a closed target-blind calibration for the AT/common-span result and shows that the emitted `AES` need not imply a cipher. The source itself redirects it back into the LOW/reversal vocabulary and the first N20 motif.

It still does **not** emit Emily's complete final margin wording. The useful next K08 operation must transform the now-deterministic N20 motif payload into the missing N23 final version, rather than launch more AES modes or phrase grammars.

## Reproducer

`agents/agent45/k08_aes_sea_closed_loop_sft.py`

The reproducer pins the crew-note SHA, checks the A1Z26 addresses, count letters, LOW BIT selectors, N07 instruction fingerprint, all 24^3 count-vector controls, exact `sea` note occurrences, and the AT loop. It reads no K08 target or nonce.
