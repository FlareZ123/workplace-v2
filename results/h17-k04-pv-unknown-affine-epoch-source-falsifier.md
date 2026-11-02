# K04: unknown-affine-scale PV stream bridge fails source-only intact controls

**Agent 17 | 2 November 2026.** Original selected ESC-N/RECOVER/ACK2 spool coupon, K04 mask and slot commitments were withheld throughout this experiment. This is a source-only, hypothesis-conditional K04 producer test, **not a recovered bit**.

## New question

Agent20 [first derived](../agents/agent20/k04_p955_pv_future_source_only_sft.py) **154 complete CPython-style 53-bit future float outputs** from all 132 intact printer records under the hypothetical source-consistent p955 MT19937 chronology. Their tests of five *fixed* PV engineering ranges yielded no consecutive two-float control. The possible escape was that PV values use an **unknown affine engineering scale and intercept**, making a fixed-range test too restrictive.

We therefore fit the scale and offset **from historical PV rows themselves**, without looking at the selected coupon. Also test an alternative one-raw-32-bit-MT-output-per-PV model, which exposes **318** complete source-projected future words. This changes the proposed downstream representation and learned calibration while preserving the exact prior source-only linear model.

## Frozen mechanism

For historian PV sequence `s=100..211`, hypothesize

```
index(s) = epoch + stride * (s - 100)
PV[s] = round_3(a + b * U[index(s)])
```

where `U[i]` is a future source-predicted pseudorandom float. The unknown integer `epoch` and real-valued affine parameters `a,b` are fit without a chosen engineering range. `stride=2` means CPython-style `random.random()` using consecutive pairs of 32-bit MT outputs (first upper27 / second upper26). `stride=1` means one fully source-predicted 32-bit word divided by 2^32. Allow both positive and negative slopes. Only calendar-independent **constant-step PV consumption** is asserted; per-row arbitrary skipped draws remain outside this test.

For each integer epoch where at least five original PV rows have predicted input `U`, fit least-squares `a,b` on all those available original readings and calculate RMS error. Since original PV is recorded to three decimals, exact source fidelity requires approximately 0.0005 absolute error per row; a generous RMS threshold 0.001 is used for the stop decision.

## Observed source-only results

| Hypothesized raw format | Predicted future independent inputs | Epochs with at least 5 original calibration rows | Smallest original RMS residual | Exact 0.0005-tolerance matches at best fit |
|---|---:|---:|---:|---:|
| 53-bit two-word CPython float, step 2 | 154 | **1,223** | **2.886829310** | 0 |
| 32-bit single-word scaled float, step 1 | 318 | **1,357** | **3.965853821** | 0 |

For the best 53-bit epoch `1715`, the five fitted source PV rows have RMS 2.88683, orders of magnitude above the 0.001 stop criterion. For the best 32-bit epoch `867`, RMS 3.96585. No source epoch with five or more predicted PV values is remotely close to the required quantized affine relation. The test scans epochs including the entire possible overlap with PV seq100..211, not merely the calendar-preferred physical shift.

**Reproducibility:** [source-blind standalone test driver](../agents/agent17/k04_pv_affine_epoch_sft.py) imports Agent20's prior [read-only original GF(2) future-word projector](../agents/agent20/k04_p955_pv_future_source_only_sft.py). The producer verifies original printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, rank `15305`, zero contradictions and 154 full53-bit outputs. The driver reproduces the exact epoch counts and minima; independent synthetic quantized affine controls for each stride successfully recover planted `a=12,b=76` within rounding error. Executed locally against the original unchanged ZIP on 2 November.

## Scope, next attack, and target status

This rejects **constant-step future MT float generation with one common unknown affine PV scaling** under the particular *hypothetical p955 printer-source alignment*. It does not exclude a non-MT PV producer, nonlinear engineering scaling, irregular draw consumption, different chosen chronology, or an independently indexed downstream copy. It also does not make the physical selected 18:02 ACK payload trustworthy. An authenticated source relation with nonconstant skip/index mapping would be needed before reopening this donor route.

**Actual selected K04 original bits gained: 0/128. K08 final caption words gained: 0.** Six previously validated slots remain unchanged; combined REC8 acceptance incomplete. No selected coupon, K04 mask, target hash or original verifier was modified or consulted.
