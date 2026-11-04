# H-17: same-ID PTW seal receipts versus printer packet word encoders

**Agent 8 | 4 November 2026 | New genuine source-paired holdout family, no recovery.**

## Recovery hypothesis

The unchanged export preserves exactly 27 one-receipt permits `PTW-390..416`, each with a signed 4-byte seal serial, and 27 independently reconstructed full 16-byte printer ACK packets with the same numeric suffix, `PS-261003-0390..0416`. The historical selections of PTW-417 (four signed as-left B,D,A,C serials) and printer PS-261003-0417 (disputed physical 18:02 ACK2 coupon) **also share 417**. Numeric equality supplies a testable *candidate* cross-record join, without establishing common hardware or issuer.

**Target-reaching proposal:** hypothetically, one of the four 32-bit words of a complete printer packet could be encoded from the same-ID 4-byte seal serial with a fixed, bay-conditioned publisher. If genuine earlier printed packets could identify four such publishers and their original word assignments, the four PTW-417 selected serials would produce a complete 16-byte K04 coupon independently of the disputed spool copy. This is a finite alternative to source-only PRNG fitting, byte repair and user-written caption guessing.

The original evidence does **not** state that a permit receipt generates a printer word. Source-only whole-packet holdouts must support any such interpretation before a recovered value can be asserted.

## Frozen genuine-original control and model

Original read-only SHA256 pins:

- `resources/evidence/maintenance/seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `resources/evidence/print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

Group original 27 singleton serial-to-packet observations by signed receipt bay: **A=8, B=4, C=9, D=6**. For each bay, train using its *two lowest numbered authentic permits* and test the rest, **19 genuine withheld permit/packet pairs in total**. Every proposed encoder must predict its assigned full 4-byte output word **for every held-out row in its bay**.

For each bay, each of four possible 32-bit printer packet word positions, two byte-endian interpretations of the serial, two output endiannesses and input byte reversal, learn a complete function through either of two full training pairs:

1. **Four independent GF(256) byte-affine maps**, `output[j] = a[j]·serial[j] XOR b[j]`, using AES GF256 field polynomial `0x11B`, with the two authentic pairs determining each byte-affine slope/intercept.
2. **32-bit modular ring affine map**, `output = a·serial + b mod 2^32`. Exact 2-adic congruence solver enumerates all valid multipliers when the training difference has at most 12 trailing zero bits.
3. **Four-byte shared XOR pad**, recovered from the first training pair, then tested on all other originals.
4. **Rotated 32-bit serial XOR common pad**, 32 cyclic bit shifts, with pad recovered from the first training pair.

This is **4,476 training-qualified held-out model assignments**, including repeated equivalent models due to redundant endianness choices. All holdout records are authentic unmodified full 16-byte printer packets; none is the disputed selected K04 payload. A separate synthetic correctly planted three-observation producer for each of four algebraic families passes, confirming the implementation can predict a withheld whole output under its own producer law.

## Complete result

| Measurement | Original result |
| --- | ---: |
| Authentic permit/printer paired source controls | 27 |
| Train per bay | 2 earliest original IDs |
| Genuine withheld source pairs tested | 19 |
| Candidate emitter assignments subjected to their bay's heldouts | 4,476 |
| **Emitter models predicting all original heldout words for their bay** | **0** |
| Planted family implementation controls | 4/4 PASS |
| Original K04 component acceptance checks | 0, deliberately skipped after source-only veto |

**Reproducer:** [single-file source-pinned Python test](../agents/agent8/k04_ptw_printer_paired_encoder_sft.py). The same exact Git blob as locally tested was committed and read back, SHA1 `9d108a42fcb9e79d1913a3f0a3d826254db27b82`; original local output:

```
CONTROLS 27 heldout_independent_records 19
SOURCE_ENCODER_HOLDOUT_ASSIGNMENTS 4476 ENTIRE_BAY_HOLDOUT_PASSES 0
PLANTED_POSITIVES GF256_BYTE RING32 XORPAD ROTATE_XOR PASS
```

## Scope and prior-art boundary

This exact original-source join into four bay-conditioned small-domain publishers differs from Agent35's archive-wide GHASH/AES publishers, Agent41's shared cassette printer pads and the v1/v2 direct byte mosaics. It has a genuine original withheld prediction before any K04 commitment comparison. The observed same-number relationship and four plausible reversible emitter families yield **no passing original producer**, so no source-justified complete K04 coupon follows from this mechanism. A more complex unknown issuer cannot be excluded by this finite test.

Our independent p951 source scan of all 27 serials found three exact source-fixed MT-stage matches: **PTW405/-964, PTW412/-944, PTW414/-937**. Those are **not new discoveries**; Agent2 identified the same three first, and Agent46 already performed source-heldout Bay/rejection tests, including the PTW416 contradiction (see [existing PTW source report](h17-ptw-bay-coupled-serial-heldouts-and-falsifier.md)). Reclassify any future cross-archive stage claim against that prior art. Our new contribution is the different same-ID original-to-original **word-publisher holdout**, not these repeated MT anchors.

K04 selected physical coupon gains **zero** authenticated bits, K08 final caption gains zero exact author-final words, original six accepted slots remain unchanged, and combined REC8/1 is **INCOMPLETE**, `accepted=false`. No original evidence, verifier, commitments or canonical candidate were modified.