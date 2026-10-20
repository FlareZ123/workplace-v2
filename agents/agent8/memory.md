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

## 20 October ~07:23 UTC: cooperative integrity fixes and follow-up

- Agent11 independently reviewed `last_escrow_ack` and caught a **real** readiness flaw: my original regex required a valid recovered PAYLOAD/DEST before selecting ACK, conflating dispatch selector with corrupted printer bytes. Agent11 promptly fixed the shared script in `ce2be6b2`, added SFT `work/test_h17_ack_selector_integrity.py` in `ca7b8bd8` and report `results/h17-ack-selector-integrity-audit.md`. His three cases are preserved. I synchronized the fix locally and re-ran my original synthetic SFT, confirmed exact source Git blob `33be5b98385ae54bedb3674980c87faf91e96038` before later modifications. Credited Agent11 in my report `dcf9cdbe`, coordinated via `communications/agent11/20261020T0720Z_agent8-selector-fix-integrated.md`.
- Hardened staggered-source integration: if a newly supplied source's K04/K08 trial returns NO_MATCH but the input baseline already had a **previously accepted** component for that same slot, preserve the prior verifiable component, show the new witness's own NO_MATCH and set `conflicting_witnesses`. Synthetic control proves the discrepancy is not hidden; this is a provenance conflict, not evidence the new source is false. Remote source/test blob hashes after push were `53997e8d15a161b05b85caa0579c55eb89c50f9d` / `30e1e460be74552ee5bfbdf39b83e18d76ad9c94`.
- Ensured intake loads `resources/candidate.json` with original verifier's `no_duplicates` hook. Added test that rejects duplicate K01 baseline fields just as the unchanged CLI does. New source/test blob hashes `4640a42bfe1a5a720daf5a2a845494e21c94ba95` / `b5494962ab0bcbe2906ca63416cc7d034a011776`; last tests PASS; report updated `0fd67101`. Original source evidence, verifier, acceptance and six candidate inputs remain untouched.
- Search within connected GitHub installations for repo names/descriptions containing h17, energy, archive, recovery, records yielded no additional repo; source coverage still points to v1/v2 and offline original intake. No actual K04 coupon bits or final K08 words were identified.

## 20 October ~07:31 UTC: strict intake-success semantics and source inventory

- A previous verified K04/K08 component remains in `partial_candidate` when a later independent transcript gives NO_MATCH; new witness is explicitly NO_MATCH in witness-level status and named in `conflicting_witnesses`. **CLI now returns nonzero for this inconsistency even if previously cached 8/8 component hashes + combined digest still PASS.** Synthetic mocked-main control `TEST 5bc` exercises this; source/test Git blobs `06921a4e8b4dc747598f1ec58d1b06393307a0a2` and `8c337e2b0f9a410b7c57d685dafcd1ab78ada50b` were verified after commits `0ab7971` / `43a2908`; report `54ec7e3`.
- Project Files scoped search for original selected ESC-N coupon, final keeper margin, and mapped R:-drive incident index found only `prompt.md`; no separate Project material. GitHub installed-repository name search for `h17`, `energy`, `archive`, `recovery`, `records` found no other relevant repos. A web indexed-query search of unique historical H-17 strings found unrelated entities only. Evidence-gain zero. Source claims remain constrained to supplied ZIP and original v1/v2 GitHub resources.
- Current `resources/evidence` Git tree SHA `0196e2bc6b207b8065f50698273db9581ca3f286` and `resources/verify.py` blob SHA `059e075c71acb5f7d68e03a2614daa76d3c54331`, `resources/acceptance.json` blob `8e92ad69039cb4e24dcd6cc75dba49dfcc03e8cb`: no new source release as of this check. Issue #1 one comment remains Agent8-only, no original custodian reply. Agent1's independent manual-only private inventory found only `private/.gitkeep`.
- Source frontiers unchanged; refrain from more low-information PRNG seeds, unindexed carrier searches, K08 theme phrases, website crawls. Await only real newly preserved original media/caption, independently grounded producer/order rule, or external source actually carrying target bytes.

## 20 October ~07:34 UTC: final intake-readiness hardening

- Identified a reproducibility race: hashing a separately reopened coupon/caption transcript after parsing could attach a file digest to different bytes if the transcript was edited between reads. Modified both inputs to read a single raw-byte snapshot and compute SHA256 from **the exact bytes parsed**. Real source-original hashes remain separate, so original-vs-transcript custody can still be checked. Intake read-only semantics unchanged.
- SFT continues to pass all six groups and every subcontrol after the snapshot change. Exact local and remote code blob `467dc8e0ca83aedd2459211dc60a12e129c9afc3` in commit `bf495664`; report commit `bca41307` documents the distinction. Tests remain synthetic positives only.
- Checked current official Python documentation for `json.loads(object_pairs_hook=...)`, `datetime.fromisoformat`, `configparser` to ensure these APIs are supported. Original Python stdlib compatibility remains.
- Compared latest live v1/v2 commits: no human target-source release yet; as of the last check v2 resource tree/evidence tree unchanged; private only `.gitkeep`. No additional original coupon or verbatim keeper words. Continue source surveillance and cooperate with nearby Agent11/Agent1. Preserve the provenance separation.
