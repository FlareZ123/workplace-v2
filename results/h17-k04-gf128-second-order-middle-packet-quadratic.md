# K04: GF(2^128) quadratic middle-packet reconstruction from four surviving late packets

**Agent 48 | 3 November 2026 | Complete-candidate construction and source holdouts; no accepted K04.**

## A different missing-middle mechanism

The selected spool row index129, `PS-261003-0417` / RECOVER / ACK attempt2 at 18:02 UTC, has a copied 16-byte payload of unverified physical integrity. Instead of copying its suspect bytes, the test treats the four **other surviving late-Z packets** at indices128,130,131,132 as mathematical endpoints around an unknown 129 packet.

Hypothesis: successive packets are elements of `GF(2^128)` and obey a single fixed **second-order field-linear recurrence with optional additive stage offset**

```
X[n+2] = A * X[n+1] XOR B * X[n] XOR C
```

where multiplication is modulo the standard irreducible polynomial `x^128+x^7+x^2+x+1` (low reduction byte `0x87`), `A,B` are unknown 128-bit field coefficients, and `C` is frozen to either zero or the original K04 route mask. This is a different source-to-target construction from the previously tested Marsaglia xorshift128+, the general 128x128 GF(2) **one-step packet transformation**, or integer `mod 2^128` affine retry laws. It gives complete target candidates without guessing a generator seed, mutating the selected copied buffer or brute-forcing the missing 128 bits.

**Important caveat:** the original does not attest a finite-field printer recurrence, a repeated additive mask or continuity across the 18:03→18:24 gap and job/class transitions. Four endpoints are only a conditional interpolation construction.

## Exact field elimination

Let `x0,x2,x3,x4` be the four intact source packets, `x1` the missing one, and `c` a fixed offset. In characteristic two, eliminate the second coefficient:

```
b0 = (x4 XOR c) / x2
b1 = x3 / x2
B  = b0 XOR b1*A
```

Then eliminate `x1=(x2 XOR c XOR B*x0)/A`, obtaining the **single binary-field quadratic** in unknown first coefficient `A`:

```
(x2 XOR b1^2*x0) * A^2
  XOR (c*(1 XOR b1)) * A
  XOR (b0*(x2 XOR c) XOR b0^2*x0) = 0
```

The SFT solves this exactly. For its nonzero linear term, the standardized `z^2 XOR z=q` equation is solved using 128-bit GF(2) row elimination. For zero linear term, the square-root field operation gives a unique nondegenerate solution. Degenerate coefficient cases are explicitly treated. Back-substitution verifies **all three** surviving recurrence equations before emitting the complete missing `x1`. At most two finite candidates exist for each ordinary model.

Test eight explicit byte/word/bit packet views: forward/reversed four 32-bit words, forward/reversed bytes inside each word, and ordinary/reflected bits within each byte. Each transformation is inverted before applying the **unchanged** K04 XOR mask and SHA-256 commitment.

## Results against authentic original and controls

Source pin: original printer log SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected index129 copied payload is excluded from all generator input and is never decoded for the calculation. The untouched original K04 target digest is queried only on complete predicted components.

| Measurement | Result |
| --- | --- |
| Frozen serialization × offset models | **16** |
| Distinct fully predicted 16-byte K04 candidates | **16** |
| Original K04 commitment matches | **0** |
| Intact ordinary five-packet middle-withheld controls | **48** (three windows × sixteen models) |
| Finite predicted holdout solutions | **42** |
| Exact original withheld-packet predictions | **0** |
| Synthetic generated recurrence tests | **2/2 PASS**, covering zero and nonzero offsets |
| One-bit synthetic late-output tamper tests | **2/2 detected** |

The canonical no-reversal, zero-offset model gives the complete predicted packet

`5DBDCF1996AF6DA91DFBC2966388818E`

and therefore K04 `D8EB07D2F7EFCA50B8E9F85134936F92`, which fails the original commitment. The canonical additive K04-mask model supplies two other complete failed candidates, `2230D9B0BACABFF151770F668572D29E` and `85D4295599D4E18E9499E32F4043D019`.

**Model calibration matters:** In the homogeneous `C=0` class, essentially any nondegenerate four field endpoints can be interpolated into *some* unique hidden middle and coefficients. Such algebraic fitting is weak evidence for historical generation. The three fully withheld, intact ordinary windows are therefore the actual source-discrimination control. All 48 have no successful prediction under the tested model variants. This argues against treating the interpolation as an original printer law, even though a different exceptional-event producer remains logically possible.

## Reproduction and next attack

[Single-file source-pinned SFT](../agents/agent48/k04_gf128_secondorder_middle_sft.py). The genuine planted streams, original source checksum, derived field solutions, heldout source windows and original K04 commitment were executed locally with the original attached archive. The compact repository SFT preserves the same algebra and assertions; no independent remote execution is claimed.

The next useful work would involve **source-visible coefficient reuse or a same-stage complete intact five-packet group** in the exceptional RECOVER retry class. A second-order field model that only fits the one missing event has little selection power. This is a finite original-candidate no-hit and a stronger rejection of the proposed common source stage, **not** a new original physical coupon or an accepted key. K04 remains unresolved, K08 final words unquoted, six original components PASS, REC8 combined INCOMPLETE.


## Addendum, 3 November ~16:12 UTC: after-target-only GF(2^32) reverse producer

A separate, more strongly controlled producer family avoids inferring the missing packet directly from arbitrary four endpoints. It interprets the **twelve fully intact 32-bit words in packet rows130,131,132**, all later than the disputed row129, as a common GF(2^32) output stream with arbitrary four-lag field-linear feedback, optionally with an unknown fixed 32-bit bias:

```
w[t] = A0*w[t-4] XOR A1*w[t-3] XOR A2*w[t-2] XOR A3*w[t-1] XOR C
```

For each combination of two verified irreducible degree-32 polynomials (low reductions `0x8D`, `0x04C11DB7`), eight original-byte/word/reflection representations and homogeneous/affine bias, algebraically fit four or five coefficients from the first four/five post-target equations. **Hold out all remaining three/four complete original output words** of the 12-word future cohort. Where the oldest coefficient is invertible, reverse the recurrence eight steps to derive both (1) all four missing 18:02 selected packet words and (2) the four previous 18:01 packet words as a separate intact backward control.

**Original result:** all **32/32** models solve their limited training equations and reconstruct a complete candidate, but **0/32** have any correct future holdout output word, **0/32** reproduce the intact 18:01 packet when reversed, and all **32 distinct complete K04 candidates fail** the original untouched commitment. Hence this specific four-word finite-field producer class is source-inconsistent under its assumed continuity across the late printer packets, before any recovery claim. Four genuine planted field generators (both polynomials × both bias options) satisfy heldout forward equations and backward exact missing+prior-packet recovery. [Reversible after-target source SFT](../agents/agent48/k04_gf32_reverse_late_packet_sft.py).

This follows a stronger selection policy than the four-endpoint interpolation above: **learn from independent later source, reserve actual heldout later outputs, and test a separately retained earlier packet**. The original 18:03 to18:24 clock gap and differing job classes still prevent generalizing this rejection to all physical RECOVER producers or variable-step generators. It contributes no accepted slot or authenticated target bit.
