# K04: unknown-feedback binary erasure recovery across same-job printer attempts

**Agent 39 | 28 November 2026 | original-source complete 16-byte coupon checks; 8 finite models fail**

## Recovery-producing model

The original selected job `PS-261003-0417` has three original full 16-byte observations that do **not** depend on the disputed copied 18:02 ACK2 payload: a 16:45 `LABEL ACK`, 18:01 `RECOVER REQUESTED1` and 18:03 `RECOVER REQUESTED3`. A hypothetical per-job serial emitter could produce each observed 128-bit field as one consecutive interval of a **single binary linear-feedback shift register**, leaving exactly the middle 128 bits (18:02 ACK2's physical coupon) erased. Unlike earlier fixed-polynomial CRC/PRBS screens and the full 128-*ordinary-packet* Berlekamp–Massey test, the feedback polynomial is **completely unknown** and the stage/order is **same-job selected at source**, with the missing physical coupon occupying an exact one-packet gap.

Two frozen source-only histories specify exact, exhaustive **bounded-degree** reconstruction domains:

1. **REQUESTED1 → erased ACK2 → REQUESTED3**: the 128 known REQUESTED1 bits determine the entire feedback of any recurrence with minimal degree at most **64**; recover the next 128 bits as a complete hypothetical coupon, and the following 128 as an intact original holdout.
2. **Earlier LABEL ACK → REQUESTED1 → erased ACK2 → REQUESTED3**: the two surviving earlier 128-bit packets, treated as consecutive per-job intervals, determine the entire feedback of any recurrence with minimal degree at most **128**; recover the same full middle packet and predict the independent 18:03 third request.

Each history is evaluated under four reversible serializers: forward/reverse 16-byte ordering × within-byte most/least significant bit first. No unknown skip count, manually chosen polynomial, source-derived seed, bit repair, noncorresponding printer row or copied ACK2 byte enters inference. The uninterrupted per-job bitstream premise is **hypothetical**, especially across the 76-minute gap from LABEL to REQUESTED1 and the change in job CLASS.

## Mathematical completeness and controls

For each original first history, run **Berlekamp–Massey** on all 128 training bits; for the second, on all 256. Its shortest GF(2) feedback has observed degree 63–64 or 125–128 respectively. Independently compute the GF(2) rank of the training sequence's lagged-bit coefficient matrix: in **all eight historical views, rank equals the inferred degree**, so the feedback coefficients at that degree are unique. Any true recurrence of degree at most half the observed training length must obey that recovered feedback: there are no unexamined seeds or taps in these declared domains.

The runner generates independent **synthetic 384-bit and 512-bit per-job streams** from seeded random unknown feedback polynomials of actual degrees **31/47/63 and 65/95/127**, respectively. Under all four byte/bit orientations it uniquely recovers the full missing 128-bit coupon and reproduces the full withheld 128-bit final packet: **24/24 synthetic positives**. The synthetic target does not reuse historical candidate bytes.

## Original full-coupon outcomes

| History | Bit serializers | Inferred feedback degrees | Hamming errors against withheld REQUESTED3 (128 bits) | Full original K04 acceptance matches |
| --- | ---: | --- | --- | ---: |
| REQUESTED1 only; degree ≤64 | 4 | 64, 63, 63, 64 | 60, 67, 61, 61 | **0 / 4** |
| LABEL then REQUESTED1; degree ≤128 | 4 | 128, 128, 125, 128 | 55, 65, 65, 66 | **0 / 4** |
| **Total** | **8** | | all 8 disagree with independent holdout | **0 / 8** |

Each reconstructed **entire** 16-byte erased middle packet was XOR-reduced with the unchanged source route mask and checked against the **full original K04 SHA256 commitment before any REQUESTED3 holdout could disqualify it**. Zero accepted components; in addition, none of the candidate model streams predicts the independently retained final request. The selected copied ACK2 contents were never parsed, tested as authentic, or used to fit feedback. Source pin: printer reconstruction SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## What is and is not excluded

This closes all binary LFSR feedback polynomials and initial states up to the **source-determined degree ceilings** for these two exact, gap-free same-job histories under the four serializers. The results do not exclude recurrence degree >64/>128, a reset/class-dependent writer, a nonbinary or nonlinear producer, gaps inside/between packets, or physical coupon media different from any generator packet. Since the historical feedback model is unattested, a source-holdout failure cannot prove the physical ACK2 was incorrectly reconstructed or that no other extraction exists.

The decisive next evidence would be a **documented native attempt-2 physical coupon/copy-stage rule**, or an independent authentic source carrier that fixes a higher-order state and a producer chronology. Do not extend this completed finite test by arbitrary phase offsets or polynomial dictionaries without that link. Six previously accepted components remain unchanged. **K04 and K08 MISSING; REC8/1 INCOMPLETE.**

## Reproducer

[`agents/agent39/k04_samejob_unknown_lfsr_erasure_sft.py`](../agents/agent39/k04_samejob_unknown_lfsr_erasure_sft.py) is standard-library Python; from repo root run:

```bash
python agents/agent39/k04_samejob_unknown_lfsr_erasure_sft.py
```

Pass `--root <authorized-export-root>` to run against the supplied extracted ZIP. The runner prints only per-model degree, independent holdout Hamming count and original commitment hit flag; it does not print original source packet bytes, original key values, private candidate/feedback states or acceptance commitments. No public source-bearing CI was dispatched.