# K04 exact source-only certificates: selected RECOVER class cannot be a 32-bit affine stream

**Agent 39 | 28 November 2026.** This is a compact algebraic certificate that upgrades the [arbitrary 32-bit affine issuer screen](h17-k04-arbitrary-gf2-affine32-native-source-emitter-20261128.md) from mismatch counts to two small **explicit source-only impossibility witnesses**. It neither reads the disputed 18:02 ACK copy nor consults the K04 commitment, route mask, verifier or key bytes.

## Proof principle

Any native 32-bit GF(2)-affine state update has `y=M*x XOR c`. Augment each 32-bit input with an extra leading 1 to obtain 33-bit `z=(1||x)`. Then `y=L(z)` for some GF(2)-linear `L`. Therefore, **for every subset of transitions** S:

```text
(XOR of z[i] for i in S) = 0
    => (XOR of next_word[i] for i in S) = 0.
```

The implication holds for **all 2^1056** affine maps, no matter what the coefficients or seed are. It is a necessary condition proved by linearity, not a guessed implementation.

Use the 128 intact ordinary records of the original printer spool, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Filter the preserved source `CLASS=RECOVER` in chronological order: 35 full ordinary packets, all preceding the selected later 18:02 job. Parse each packet into its four native 32-bit big-endian words.

## Two source-native contradictions

<escape>| Certificate | Native sequence | 0-based **transition indices** making the input XOR zero | Terms | XOR of actual output words |
| --- | --- | --- | ---: | --- |
| Serial RECOVER | Concatenate four native words per packet (140 words) | 6, 7, 9, 10, 11, 14, 15, 17, 19, 20, 21, 28, 29, 31, 32, 33 | 16 | **Nonzero; 19 set bits** |
| Parallel RECOVER lane 1 | Second 32-bit word of each packet (35 words) | 3, 4, 8, 12, 15, 16, 21, 26, 27, 32 | 10 | **Nonzero; 15 set bits** |</escape>

For each listed set, the reproducer explicitly XORs the original 33-bit augmented **source inputs** and asserts the result is exactly zero, then XORs the corresponding **actual next-word outputs** and asserts it is nonzero with the stated bit count. This is sufficient to refute any uniform fixed affine transform for the source-selected RECOVER class under **both** source native-stream topologies, independently of whether a trained full map could reconstruct the missing coupon.

As an independent positive control, it creates eight random arbitrary 32x32 GF(2) coefficient matrices plus affine offsets for *each* of the two original input-dependency sets, applies the transforms to the actual original inputs and asserts output XOR zero in **16/16** cases. The implication is direct linear algebra, not an empirical pattern that requires a significance threshold.

## Scope / recovery impact

These certificates rule out **all** single fixed affine 32-bit next-word maps under the two described selected-CLASS native packet layouts; no further seed or affine-coefficient enumeration can rescue them. They do **not** address nonlinear scramblers, other source stage orderings, resets, hidden bytes, physical copying or nonaffine state updates.

No authentic selected attempt-2 coupon byte was obtained, K04 still fails its original commitment, and K08's final caption remains unquoted. Six other original components are accepted; REC8/1 remains incomplete. The practical next step requires actual selected-stage physical issuance/copy evidence, not another affine seed hypothesis.

Reproducer: [source-pinned selected-class affine proof SFT](../agents/agent39/k04_affine32_selected_class_cert_sft.py), run `python agents/agent39/k04_affine32_selected_class_cert_sft.py --root resources`. The source and commitment materials remain unchanged, and no physical/candidate bytes are published.
