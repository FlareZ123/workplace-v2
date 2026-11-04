# K04: cross-domain selected-version postprocessor heldout test

**Agent 1, 4 November 2026, original-source-derived exploratory whole-block negative.** Official REC8 status remains six individual PASS and K04/K08 missing. No original evidence, candidate, commitments or verifier were changed. This investigates the [4 November Critic selection-stage proposal](../communications/broadcast/20261104T1315Z_Critic_selected-record-postprocessor-challenge.md) from a different causal direction than another printer PRNG. It does not identify the historical printer.

## Source-native before/after observations

The four 16-byte pairs below are assembled *without using K04's disputed 18:02 ACK2*. K05 parses node49/event82 24-byte records with valid CRC and indexes earlier seq200..203 versus selected seq300..303 by latch. K06 orders the withdrawn revision B and issued revision C footer strips by SERVICE_ORDER, not scanner page. K07 chooses greatest-attempt 2-byte checkpoints by seq in the two committed transfer groups. Printer pair uses two actual 0420 ACK entries, with distinct CLASS and DEST noted below.

| Source role | Earlier 16 bytes | Later selected/acknowledged 16 bytes |
| --- | --- | --- |
| K05 node49 seq200..203 vs seq300..303 | `42BFD0538052760C6FC2B743BFB00270` | `FF8B78200A56E8586DCDA00EF01E4572` |
| K06 withdrawn B vs issued C | `D82A73E9E1DB4379759E0027C130C9BB` | `5DBF40EE52FAAED9A536D3326CF0D95A` |
| K07 AX-7778 drill vs AX-7782 final | `AC5FBCDD1CB5C98CA234AE35DD42B16A` | `8947CEDCB9CC73BAB7E87BE63302C5C9` |
| Printer PS-261003-0420 ACK1 vs ACK2 | `31C9714DD36DB2677BB9006670A9DFFD` | `432475F72A62DB39F3D5693E2C937FA4` |

Original member SHA256s:
- `evidence/recorder/trip-recorder.raw`: `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`
- `evidence/procedures/RC-17-scans.txt`: `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d`
- `evidence/transfers/transfer-audit.jsonl`: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- `evidence/print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

These source roles are substantively different, with possible independent generators and change semantics. The 0420 printer pair changes STORES/desk to RECOVER/bench and is **not** a calibrated same-role physical-coupon transition. Using it as a strict control is a strong, intentionally hypothetical assumption.

## Complete-packet experiment

Freeze the first two pairs as training (K05 and K06); withhold **both** complete selected blocks K07 and printer0420 from model fitting. Because an unrestricted 128-bit pad per record can explain anything, test only global operations with a single shared parameterization.

1. **200 deterministic rotations with a single common 128-bit XOR pad**, trained on K05 only: 128 whole-block bit rotations, 32 per-32-bit-word rotations, 16 byte-left and 16 byte-right rotations, and eight per-byte bit rotations. All perfectly reproduce their K05 fitting pair; **zero** predict the complete K06, K07 or printer0420 target.
2. **128-bit binary-field affine operator** `T(x)=a*x xor b`, irreducible polynomial `x^128+x^7+x^2+x+1`. Solve *exactly* for two field coefficients from the K05 and K06 before/after pairs, independently choosing big/little endian for inputs and outputs (4 orientations). All four models fit both training pairs exactly; **none** predict K07 or printer0420. Four real seeded synthetic operator histories recover the planted `a,b` and the fully withheld third block.
3. **Integer-ring affine operator** `T(x)=a*x+b mod 2^128`. Solve the exact two-pair modular congruence under the same four input/output orientations. The real difference has 2-adic valuation zero for two orientations and one for two; enumerate every slope residue branch, giving **6** complete exact-fit models. Again **zero** full K07 or printer0420 heldout predictions. All original congruences are solvable, so these are genuine cross-domain holdout failures rather than failed fit attempts.

In the four GF128 models, the 16-byte K07 prediction matched **zero bytes** of actual selected K07, and the printer0420 prediction also matched **zero bytes**. The six ring predictions match zero K07 bytes and at most **one** printer0420 byte. These are descriptive byte coincidences, not an estimator of source authenticity.

A reproducible, standard-library [single-file test](../agents/agent1/k04_crossdomain_postselection_sft.py) contains all four source-extracted packet pairs, rotations, exact finite-field algebra, modular-congruence enumeration and synthetic positives. The original ZIP was parsed and source file hashes checked separately in the local original extraction step. The portable SFT keeps frozen source-derived values so it can run in the shared repo without archived binary extraction.

## Conclusion and limit

This is a falsification of **three specified global shared post-selection operator families**. It is not a proof that the original devices share no postprocessor: source-record formats, roles and version changes differ, and the printer control differs in CLASS/DEST. No class can be promoted to the selected PS-261003-0417 physical-coupon prediction without new evidence or an independent heldout selected-packet success. K04 authentic physical coupon bits: **0/128**; K08 exact final-caption words: **0**. Future research should pursue a *role-specific but externally learnable* selected-stage mechanism, not reuse an arbitrary per-record pad to retroactively fit the same records.
