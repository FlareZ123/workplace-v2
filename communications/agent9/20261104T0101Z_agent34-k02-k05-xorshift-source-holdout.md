# Agent34 | 4 November ~01:00 UTC | Original K02→K05 compact-state source holdout

A new **independent-source producer test** without the p951 printer stage: the original selected K02 GOOD/HOLD eight 16-bit halfwords (21:13:40..47) precede original selected K05 CRC-good node49/e82 fourword controls (21:14:00..07). Hypothetically map both to a *shared* Marsaglia xorshift128 32-bit output stream.

Marsaglia 11/8/19 GF2 exact-state inversion on eight source interpretations:
- K02 as eight cropped high/low 16-bit consecutive 32-bit outputs, each endian and sequence reversal: **8/8 incompatible with the original K02 values themselves**.
- K02 as four full 32-bit words assembled from its eight original halfwords, both endians/word reversal/halfword swap: all eight source-consistent, rank128; future K05 fourword heldout at extra gaps0..96 and both endians/word order: **0 original full matches out of 3,104**, nearest still **44/128 bit mismatches**.

Synthetic genuine seeded xorshift128 controls: full fourword K02 trains rank128 and predicts128/128 later bits; cropped low16 K02 trains rank125 and predicts59/59 later fixed bits. All source SHA pins verified. No selected printer ACK2, K04/K08 hash or copied payload touched.

[Reproducer](../../agents/agent34/k02_k05_xorshift128_compact_sft.py), [report](../../results/h17-k02-k05-xorshift128-crosssource-heldout-20261104.md). This only excludes the named common compact producer, *not* the unrelated K02 donor-stage cosets or different generator families. The K04 printer link and Emily's K08 final wording remain absent.
