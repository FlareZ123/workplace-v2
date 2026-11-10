# K04: every unknown 32×32 affine binary stride-four MT-register initializer fails preserved printer source

**Agent 11 | 10 November 2026 | original 132-packet source-only exclusion | zero K04 bits recovered.**

## Recoverable-value hypothesis

A printer's native 624-word MT19937 register might be produced in four interleaved 32-bit lanes, each advanced by the **same** unknown affine binary transition:

`S[i+4] = A·S[i] XOR c` over GF(2), for `i=0..619`, with **arbitrary** binary 32×32 matrix `A` and **arbitrary** 32-bit offset `c`.

This is a structurally wider producer than a named LFSR/xorshift tap set, an unknown single 32-bit modular-affine LCG, or a dictionary of known seeding libraries. If genuine, the complete transition could propagate source-known register words into otherwise unobserved state and yield the missing ESC-N 18:02 fourword coupon; the original mask and full K04 commitment would then be the independent final acceptance check.

**Historical caveat:** Neither firmware nor a four-lane binary initializer is documented, and the register origin comes from the conditional, retrospectively fitted p951 printer-stage chronology. The hypothesis has value only if whole intact source packets support it.

## Exact entire-model algebra and source isolation

Use the original unmodified `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected ESC-N `PS-261003-0417` 18:02 attempt2 ACK row129 is **excluded before decoding its copied payload**. The original Agent49 exact native MT19937 GF(2) source basis has rank **15,365** and permits determining particular bits of the 624-word register at the existing `ORIGIN=-1100`.

- **166 entire 32-bit register words** are source-fixed by intact source packets.
- Exactly **32** source-fixed, complete input/output pairs `(S[i],S[i+4])` are present. Their 32 input vectors have GF(2) rank **32**.
- These 32 pairs fix the arbitrary `A` **conditional** on the unknown constant `c`, rather than merely fitting a few named matrices. Represent each other source-known input `x` in that complete rank32 training basis. Write `A_0 x` for the unique linear map trained with `c=0`. If the parity of its basis coefficients is `p`, every possible affine model must obey:

`A x XOR c = A_0 x XOR (1 XOR p)·c`.

- This expression supports an **exact** test against partially source-known output words with no enumeration of the `2^32` possible constants and no invocation of the selected coupon's acceptance hash. For `p=1`, the constant cancels and output bits are unconditionally predicted. For `p=0`, each known output bit constrains the corresponding bit of one shared `c`.

The 32 fully observed training pairs and **52 additional source-observed partially determined output pairs** supply **84 original-source pair checks**. Those 52 additional pairs expose **353 independent per-position known source bits**; all fixed source bits arise from the original unchanged nonselected packet source.

## Actual original outcome

| Source-based model condition | Outcome |
| --- | ---: |
| Entire source-fixed register words | 166 |
| Complete training pair count/rank | 32 / 32 |
| Additional partially determined holdout pairs | 52 |
| Additional known holdout output bits | 353 |
| Holdout pairs with **unconditional** known-bit contradiction, any `c` | **21** |
| Constant `c` bit positions constrained by holdouts | 32 / 32 |
| Bit positions that would require `c` to be **both 0 and 1** | **27 / 32** |
| Original source-compatible affine transition matrices and constants | **0** |

For example, the first unconditionally contradictory source pair is at initial native-register index **101**. A single unconditional mismatch would suffice to refute the entire family; the additional 20 and the 27 contradictory shared-constant bit positions make the falsification independently overdetermined.

The result is not a 32-bit-parameter dictionary search. It eliminates **every binary 32×32 transition matrix and every 32-bit XOR offset** under this exact four-step native-register relation and the p951 initial-register location. The model is source-incompatible before requiring a guess for the copied 18:02 ACK, route mask or original SHA256 target.

## Positive controls and reproduction

[Portable single-file Python SFT](../agents/agent11/k04_unknown_linear_stride4_source_sft.py) imports the existing exact source-only printer basis, reconstructs all 624 source-bit visibility masks, performs full-rank binary input/output elimination, and asserts the numeric original contradictions. It also synthesizes two *genuine* interleaved unknown-generator register histories using a 32-bit xorshift transition with `c=0` and with `c=0xD6C6C5C0`. Both independent positive controls use the exact original-source partial-bit visibility pattern, retain all 32 full-pair training inputs and all 52 partially known holdouts, and pass without any unconditional or constant-bit contradiction.

Executed on the remote original checked-in repository in [one-shot GitHub Actions run 42849589955](https://github.com/FlareZ123/workplace-v2/actions/runs/42849589955) at 15:56 UTC on 10 November 2026: **SUCCESS**, including both generator controls and original assertions. The same job independently executed the companion [53-bit CPython joint metadata source gate](../agents/agent11/k04_randfloat_joint_metadata_sft.py): first/last/any placement maximum source-compatible ordinary gaps **91 / 100 / 113 of 127**, no complete source-compatible model.

## Consequence for the recovery target

This eliminates the specified unknown *linear* four-lane initializer rather than proving the missing physical coupon unrecoverable. Different origins, nonlinear 32-bit initializers, higher-dimensional state, independent selected-event replay and genuine media copy damage remain possible. None is established merely by the negative result.

**Authentic selected K04 coupon bits gained: 0/128. K08 final author wording obtained: 0.** Six original slots K01/K02/K03/K05/K06/K07 remain individually PASS, while K04 and K08 remain MISSING and combined REC8/1 remains **INCOMPLETE**. No original evidence, route, acceptance, official verifier or canonical candidate was modified.

Further work should seek a source-authenticated producer or a genuinely different selected-event/media relationship, rather than extending matrix stride choices without evidence.
