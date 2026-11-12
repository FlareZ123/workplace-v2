# K04 same-job affine-attempt and recorder CRC fault-mask screen

**Date:** 2026-11-12  
**Identity:** Agent1  
**Status:** bounded negative; no K04 candidate recovered

## Question

Could the four PS-261003-0417 spool payloads form a simple 128-bit affine recurrence across the label print and three recovery attempts, allowing the missing/selected attempt-2 payload to be reconstructed from the other attempts? Separately, do the four CRC-invalid node49/event82 recorder controls expose a 16-byte K04 donor through their correction deltas?

This is a source-specific test of the same-job attempt sequence and the CRC-failed recorder group. It does not reopen the previously tested 624-word/global-MT, p951, generic metadata, or broad donor families.

## Same-job 128-bit affine LCG

Let the observed payloads be 128-bit integers:

- (P_0): PS-261003-0417 LABEL / ACK;
- (P_1): RECOVER / REQUESTED / attempt 1;
- (P_2): RECOVER / ACK / attempt 2 (selected spool row);
- (P_3): RECOVER / REQUESTED / attempt 3.

Test the simple recurrence

[
P_{n+1}=aP_n+c pmod{2^{128}}.
]

Eliminating (c), with (d=P_1-P_0), gives

[
d,a(a+1) equiv P_3-P_1 pmod{2^{128}}.
]

The big-endian interpretation has (v_2(d)=1). Dividing by the common factor reduces the quadratic to modulus (2^{127}), where bit-lifting yields two possible intermediate values:

- `39B4EA039FFEB30286D39C33317D6464`
- `756F727D364A4ED159AD64187FF16C72`

Neither equals the observed attempt-2 payload `A9A9DC5731A5E2AE879C47215C2559D5`; neither yields the committed K04 component after applying the route mask. The little-endian interpretation has no quadratic roots. Thus this simple same-job affine LCG is falsified.

## Bounded late-payload XOR donor test

The non-target late spool donors were the same-job LABEL ACK, RECOVER REQUESTED attempts 1 and 3, the ESC-S PS-261003-0448 ACK, and the WATCH-SPARE PS-261003-0420 ACK. All 31 non-empty bytewise-XOR subsets were checked as payload candidates, both directly and after the documented K04 mask. No candidate matched the K04 SHA-256 commitment.

## Recorder CRC correction observation

For the four CRC-invalid node49/event82 seq900–903 records, solving the stored CRC against the record bytes with only the 4-byte control field varied gives the same per-record XOR correction:

`3F9B320D`

in each latch. Consequently, the stored 16-byte control block and the CRC-corrected block differ by `3F9B320D` repeated four times. The repeated delta itself, and its route-mask XOR, do not match the K04 commitment. This is an empirical common corruption signature, **not** evidence that the delta is a K04 key or mask.

## Reproduction and limits

Inputs are the preserved `evidence/print/spool-reconstruction.log`, `evidence/recorder/trip-recorder.raw`, `evidence/recovery-routing.json`, and `acceptance.json`. The modular derivation is exact under the stated LCG model; the donor screen is exhaustive only over the five named late payloads and their 31 non-empty XOR subsets. No claim is made that all possible same-job transforms or printer-stage models have been excluded.

**Conclusion:** this avenue produces no complete K04 candidate. Preserve the common recorder correction delta as a data-integrity observation, but do not promote it into a key hypothesis without an independent source relation.
