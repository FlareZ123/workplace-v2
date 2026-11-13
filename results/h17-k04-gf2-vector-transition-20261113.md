# K04: full 128-bit GF(2) state and affine-transition test

**Date:** 2026-11-13  
**Identity:** Agent 6, with independent affine-family review by Agent 3  
**Status:** Reproducible model exclusion; no K04 candidate

## Question

Can the chronological 16-byte printer payloads be treated as states of one fixed first-order transition over GF(2)? Test both the most general homogeneous 128×128 binary matrix and the entire affine family with an arbitrary 128-bit constant offset.

## Method

Source: `resources/evidence/print/spool-reconstruction.log`.

The log contains 133 payload-bearing rows: 128 regular rows (PS-261003-0300 through PS-261003-0427) followed by five late rows. Treat each 16-byte payload as a 128-bit state vector `x_i`, in chronological log order.

Fit the most general homogeneous map:

```
x[i+1] = A * x[i]  over GF(2)
```

using 128 transitions: the 128 regular payloads as inputs and the next 128 payloads as outputs. The last training output is the first late event, PS-0417 attempt-1 REQUESTED. The input-state matrix has rank **128**, so the homogeneous map is unique.

A deterministic planted invertible 128×128 GF(2) positive control (seed 20261113) is recovered and predicts **32/32** withheld random states. This validates the fit/prediction implementation, not the printer model.

Reproduction:

```bash
python agents/agent6/k04_gf2_vector_transition_sft.py
```

## Homogeneous-map results

| Held-out transition | Homogeneous prediction | Actual retained payload | Match |
|---|---|---|---|
| PS-0417 attempt-2 ACK | `CAEC4F38328DCA2769502D24FE9D80E7` | `A9A9DC5731A5E2AE879C47215C2559D5` | No |
| PS-0417 attempt-3 REQUESTED | `5EB2E2370735C37E4F790DD0323F98C2` | `44D53DFC29D7943A95D89371DA58EC64` | No |
| PS-0448 attempt-1 ACK | `3254231ABFD09D7F528C612532698421` | `234BE186E97EE05830909790E336109E` | No |
| PS-0420 attempt-2 ACK | `81406CF24E8FCA00B5F632464C456F0C` | `432475F72A62DB39F3D5693E2C937FA4` | No |

## Complete arbitrary-affine closure

Agent 3 independently extended the calculation from selected fixed offsets to **every possible 128-bit affine constant**.

Let (X) be the full-rank matrix of the 128 training input packets, (Y) their successors, and (A_0) the homogeneous fit. For any constant (c), the unique affine fit satisfying the same training pairs is:

```
F_c(x) = A_c*x XOR c
       = A_0*x XOR gamma(x)*c

gamma(x) = 1 XOR parity(alpha(x))
x = XOR_i(alpha_i * x_i)
```

Here `alpha(x)` is the unique coordinate vector of query state `x` in the 128 training input basis. The reproducer now computes this coordinate vector and the exact coefficient `gamma` for three late queries.

| Query transition | `gamma` (coefficient of arbitrary c) | `A0` prediction | Actual successor | Residual `A0 XOR actual` |
|---|---:|---|---|---|
| 18:01 PS-0417 REQUESTED1 → selected ACK2 | **1** | `CAEC4F38328DCA2769502D24FE9D80E7` | `A9A9DC5731A5E2AE879C47215C2559D5` (untrusted reconstruction) | `6345936F03282889EECC6A05A2B8D932` |
| 18:03 PS-0417 REQUESTED3 → PS-0448 ESC-S ACK | **0** | `3254231ABFD09D7F528C612532698421` | `234BE186E97EE05830909790E336109E` | `111FC29C56AE7D27621CF6B5D15F94BF` |
| PS-0448 ESC-S ACK → PS-0420 WATCH-SPARE ACK | **0** | `81406CF24E8FCA00B5F632464C456F0C` | `432475F72A62DB39F3D5693E2C937FA4` | `C264190564ED113946235B7860D610A8` |

Interpretation:

- For the selected ACK2 query, `gamma=1`: its affine prediction is `A0(x) XOR c`. As (c) ranges over all 128-bit values, the predicted ACK2 ranges over **all 2^128 possible values**. The training data therefore provide no selected K04 byte information under this affine family. A chosen offset can force any candidate, but is not evidence.
- For both independent late control transitions, `gamma=0`: their predictions are independent of (c), and both disagree with the retained successors. **No affine constant whatsoever can repair either control transition** under this precise chronological one-step model.
- The earlier finite checks using K04.mask, K08.desk_nonce, and accepted components K01/K02/K03/K05/K06/K07 are special cases of this now-complete affine analysis; no further offset enumeration is warranted.

## Conclusion and limits

The observed chronological retained-payload stream is not explained by a single fixed homogeneous or affine 128-bit GF(2) state transition with one update per logged row. The homogeneous fit is uniquely determined and fails four late holdouts; the complete affine family cannot repair two independent late controls. The selected ACK2 remains entirely underdetermined within that family.

This is a model-level exclusion, **not** proof about the historical printer writer or physical coupon. The late 16-byte fields are reconstructed dispatch metadata; the REQUESTED/ACK transitions and route/job boundaries are not authenticated as a single writer-state stream. Variable-consumption, metadata-conditioned, nonlinear, per-route/per-class, omitted-event, or copy-stage producers remain outside this exact model.

No K04 candidate is produced. Do not use the homogeneous prediction or an arbitrary affine offset as a recovery value. The actual K04 route still requires original native PS-0417 spool/coupon evidence and an authenticated copy-stage/selector relation.
