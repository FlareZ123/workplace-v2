# Agent 8 continuity: H-17 source-evidence intake

**Normal mode:** Actual uniform random draw = 4 (20 Oct 2026). Claimed a previously unused `agents/agent8` identity at `2026-10-20T06:40:05Z`, run ID `h17-agent8-cdbcf124acb9`. Do not refresh lease. At every checkpoint compare current runtime UTC clock to original lease, release only after >=70 minutes.

## Current objective and truthful state

Recover 8 archival REC8/1 components using original source and original acceptance. Repo's six verified slots K01/K02/K03/K05/K06/K07 pass; K04 and K08 remain unknown. `resources/candidate.json` is canonical incomplete state. Other agents, notably prior `workplace-v1`, have extensive 180+ negative original-data studies; consult `results/h17-v1-prior-art-gate.md` before a new brute-force or external-access project.

## This incarnation

- Confirmed repo `README.md` forbids per-commit CI workflows, and its maintainer states solution exists.
- Inspected both new-repo result index and predecessor v1 synthesis, source routing, custodian record, primary mail and K04/K08 evidence; no new source-backed target material from local 46-file copy.
- Read Issue #1: exact original ESC-N attempt 2 coupon and Emily's final margin are already requested; no reply as inspected.
- Independently ran the untouched `verify.py` on a local six-slot fixture: six PASS, K04/K08 MISSING, accepted=false.
- Added **read-only source-intake bridge** `work/h17_witness_intake.py`: preserve original/transcription SHA256, verify K04 original selector with route+spool, derive XOR; normalize K08 and HMAC; call original `verify.evaluate`. Emit full candidate only on real eight-slot + combined PASS.
- Added `work/test_h17_witness_intake.py` SFT with six passed checks including real missing-slot negative tests, original-file hash invariance, and a clearly labelled **synthetic** eight-PASS positive control against isolated fake commitments. No authentic K04/K08 bytes recovered by it.
- Details in `results/h17-original-witness-intake-gate.md`. Originals and acceptance untouched.

## Next discriminative step

Test a *new independent original* ESC-N coupon or authentic final caption only if supplied, preserving both raw-source bytes and transcriptions, then document whether original H17 acceptance passes. Investigate genuinely new source provenance only where credible. Avoid repeating v1 three-byte exhaustive search, printer MT chronology/nullspace sweeps, generic phrase enumeration, ZIP container scans, public portal attempts or old Git history.

## 20 October follow-up checkpoint (07:05 UTC)

- All four primary artifacts were written through GitHub atomic contents commits, remote blob SHAs verified against the locally tested files; indexed the new gate in `results/README.md`, broadcasted one substantive readiness note, and added a non-duplicative technical handoff on existing custodian Issue #1.
- Hardened the new coupon transcription parser by importing the official verifier's `no_duplicates` hook. JSON duplicate payload keys are now rejected; SFT adds an explicit ambiguity-rejection control. Post-change local SFT passed all prior six test groups and new check; remote source/test blob SHA1s `d0cfbc0446e9747454d5d4d27b738ac58838412d` and `c8390446387dc3fcd3f3359ee5af18f7327efcbe` match tested local files.
- Report now explicitly distinguishes a genuine newly authenticated physical record's `NO_MATCH` from source forgery: the transcribed K04 mask and K08 nonce could theoretically be the mistaken layer; preserve the original new witness and seek the commissioning originals if a contradiction arises.
- Read new Agent11 memory; they independently confirmed no human-supplied original source or Issue #1 source reply at ~07:01Z. Targeted public identifier web search produced only unrelated hits. Old-site/source scans in v1 remain prior art, so no further generic crawling.

## 20 October 07:13 UTC: incremental witness integration

- Enhanced `work/h17_witness_intake.py` with `partial_candidate` containing **only** commitment-PASS components, so an authenticated coupon or caption can be submitted at different times. Previously missing-slot components in baseline `resources/candidate.json` are retained only if already accepted against the immutable original slot commitment. Six baseline slots are checked individually and an altered K01 etc raises an error.
- Enhanced `work/test_h17_witness_intake.py` to test synthetic staged K04-then-K08 input and tampered original six-slot baseline. Original intact spool and draft failures remain NO_MATCH and excluded from partial candidate. The complete synthetic 8/8 proof is **only** under temporary artificial commitments. All six numbered test groups, plus 3b/5b/5c controls, PASS locally.
- Exact local-vs-remote Git blob SHA verification of new scripts: `e1f8b7f61ab31244ed745d43301cc2115b5556fc` (intake) and `6bd0b4c5b2f498f1ead095fb5aa97697dbf098ff` (SFT); remote commits `6f4cb967` and `e28d0bcc`. Added staged-source explanation to `results/h17-original-witness-intake-gate.md` (`578d1677`).
- Source-original `verify.py` and route JSON reopened for robustness; hash-preimage target still unknown; no target-bearing evidence added. Continue respecting v1 target-information gate; no redundant CI.
