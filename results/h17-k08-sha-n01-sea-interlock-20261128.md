# K08: the middle SHA token closes back to N01 / the AT sea motif

**Agent 14 | 28 November 2026 | target-blind source-program interlock; final author wording still unresolved**

## Question

Agent45's unique N09 stream emits `AES / SHA / AES`. The outer AES tokens already close target-blind through A1Z26 note counts, LOW BIT and N07 reversal to the literal SEA token. Does the middle SHA token participate in the same source-local vocabulary, or should it be treated as an unconstrained cryptographic instruction?

## Fixed continuation

Apply exactly the same first step as the AES/SEA count decoder:

1. A1Z26 `SHA` -> N19 / N08 / N01.
2. Their normalized post-label word counts are **22 / 13 / 11**.
3. Under the established A=0 count-to-letter convention those counts emit **WNL**.
4. Apply the already-established ASCII LOW BIT packing to `WNL`: it is **1**, selecting **N01**.
5. Literal normalized `sea` occurs in exactly **N01 and N20**.
6. N01/N20 are the established **AT** address pair; their unique maximal common span is the already pinned two-word AT motif span.

The reproducer reads only the pinned crew-note source and the prior public AT-span fingerprint. It does not read the K08 nonce, acceptance target, or any phrase candidate.

## Result

The middle token therefore has a deterministic source-local path:

`SHA -> N19/N08/N01 counts -> WNL -> LOW BIT 1 -> N01 -> N01/N20 -> AT sea motif`

This is distinct from the outer AES route:

`AES -> counts LOW -> LOW BIT 7 -> N07 reversal -> SEA -> N01/N20 -> AT`

So SHA does **not** duplicate the AES->LOW->N07 reversal operation, but it still converges on the same N01/N20 / AT motif network one step later.

Matched source facts:

- source SHA-256 pin: PASS;
- SHA-address note counts: exactly 22/13/11;
- count token: exactly WNL;
- LOW BIT(WNL): exactly 1;
- notes containing literal `sea`: exactly N01 and N20;
- N01/N20 unique maximal overlap length: exactly 2 words;
- overlap fingerprint: identical to the established AT span.

Repository search for `SHA WNL N01 LOW BIT` found no earlier result beyond Agent14's same-invocation handoff to Agent45.

## Consequence

The unique `AES/SHA/AES` N09 stream now has a stronger non-cryptographic interpretation: all three tokens feed the existing N01/N20 sea/AT source program, although by different routes. This weakens the rationale for launching more generic AES/SHA block constructions without a newly selected operand and serialization.

It still does **not** emit Emily's complete final margin wording. N01 is a photograph-caption antecedent already heavily covered by earlier phrase-splice searches, so this selector should not be used to reopen those grammars. The remaining useful question is still a source-fixed complete version operation from the selected antecedent/motif network to the final N23 wording.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing; REC8/1 remains incomplete.

## Reproducer

`agents/agent14/k08_sha_n01_sea_interlock_sft.py`

The script pins the original notes, reproduces SHA->WNL->N01, enumerates literal sea occurrences, verifies the N01/N20 maximal overlap fingerprint and confirms that no K08 target or nonce is read.
