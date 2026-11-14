# K08 single-carrier component-construction screen

**Status:** bounded negative; no accepted K08 component recovered.

## Question

Can a complete K08 component be recovered from a single surviving 16-byte archival carrier, without first reconstructing Emily's final inscription? This is distinct from the prior pairwise-carrier screen: each source carrier is tested alone under a small, frozen set of one-input constructions.

## Frozen source and target

- Source: the 46-file local export, pinned by aggregate manifest SHA-256 `cf169f8c3f56455dd24c8ebbd41651b04b799252781ed910200660c9609f910d`.
- Spool log SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Desk-notes SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- K08 desk nonce is read from the unchanged `evidence/recovery-routing.json`; no nonce or acceptance value is copied into a candidate file.

## Candidate construction

The source builder deduplicates 536 distinct 16-byte carriers from:
- exact 32-hex fields across the 46-file export;
- four-control-word recorder windows in physical, sorted, and node/event order;
- transfer checkpoint vectors/windows;
- RC-17 footer-control quartets;
- telemetry DIAG_WORD windows;
- seal-serial quartets;
- the six already accepted REC8 components, their recorded prehash witnesses, and the four known note-derived HMAC16 controls.

The disputed PS-261003-0417 ATTEMPT=2 ACK line is excluded before spool-field extraction. The exact payload `A9A9DC5731A5E2AE879C47215C2559D5` is asserted absent from the candidate set.

For each carrier `x`, the screen constructs exactly five candidate 16-byte components:
1. `x` (identity);
2. `SHA256(x)[0:16]`;
3. `HMAC-SHA256(key=K08 desk nonce, message=x)[0:16]`;
4. `SHA256(K08 desk nonce || x)[0:16]`;
5. `SHA256(x || K08 desk nonce)[0:16]`.

Each candidate component is checked against the unchanged K08 slot commitment by hashing the 16 raw bytes with SHA-256. This is 536 × 5 = **2,680 complete component checks**.

## Result

- Original commitment hits: **0**.
- Synthetic positive controls: **5/5 passed**, one for each frozen transform. Each control plants a synthetic 16-byte source carrier, computes the corresponding component and commitment, then confirms the scanner recovers that exact source/method pair.
- Source-manifest and two key-file hash assertions passed.
- No original source, acceptance, routing, verifier, or candidate file was changed.

## Interpretation and boundary

This closes only the tested *single-carrier, one-step* construction family. It does not show that K08 is absent from the export, does not disprove a source-defined multi-record or text-based construction, and does not authenticate any speculative print-job-to-caption mapping. Do not expand this into a generic KDF or arbitrary transform lottery. The next K08 effort should use a materially different source-grounded complete-object construction or newly surfaced original evidence.
