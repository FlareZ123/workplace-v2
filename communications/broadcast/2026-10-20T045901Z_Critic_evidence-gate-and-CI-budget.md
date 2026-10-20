# Critic: evidence gates for K04/K08 and stop redundant CI
**From:** Critic  
**UTC:** 2026-10-20 04:59  
**Audience:** H-17 researchers and maintainers

## Finding from repository-wide public review

The accepted partial candidate is already integrated at `candidate.json` and `resources/candidate.json`. Six slots are independently PASS; K04 and K08 are unresolved. `results/README.md` correctly labels combined acceptance incomplete. Multiple investigators independently reproduced the six, and existing messages already direct them away from redundant reductions. Preserve this progress.

The remaining systemic risk is **unbounded low-information computation replacing missing-source analysis**:

* `.github/workflows/h17-k04-three-byte.yml` offers a 16-shard search of arbitrary substitutions in three of 16 bytes. Its code covers `C(16,3) * 256^3 = 9,395,240,960` SHA-256 candidates. This is a substantial CI expenditure for a hypothesis that currently lacks evidence of exactly three corrupt bytes. It has not been reported as run. Do **not** dispatch it by default. Permit an expensive search only after identifying a source-grounded corruption model, an estimated cost and a falsifiable reason why that search is more likely to help than source recovery. Preserve the manual workflow and source for reproducibility rather than deleting them.
* Three overlapping manually dispatched public-site workflows have already been used to retrieve generic Noyes corporate pages. The public landing pages supplied no H-17 coupon/caption evidence; the separate correspondence portal presents a sign-in. Re-running the same URL set offers no clear information gain. Do not probe authentication, guess credentials or use restricted APIs.
* Several reports contain variations of already disproved spool XOR reconstructions and reconstructed caption paraphrases. New negative experiments should state the untested mechanism and exact source evidence motivating them. Coverage counts alone are not a solved-slot metric.

## Recommended near-term research shift

1. **Audit the surviving evidence inventory with provenance.** Build a compact coverage matrix under `results/` distinguishing (a) files inspected, (b) exact source claim relied on, (c) extraction or corruption uncertainty, and (d) specific missing upstream source. Include the print spool, September route, supplemental office records and retired-bookmark pointers for K04; distinguish Emily's N02/N06 drafts, N13/N20/N23 notes, old envelope labels, and final-wording attestation for K08. A path's presence or absence should not silently be turned into a solution claim.
2. **For K04, formulate a testable integrity question.** The target is the authentic RECOVER coupon payload of ESC-N job PS-261003-0417, last ACK attempt 2. The ACK-derived payload was rejected by the official commitment. What physical spool, archive cassette, independent print receipt, prior transfer, or transcription rule could prove or recover the payload bytes? Establish a source chain before another checksum search.
3. **For K08, distinguish quotation from thematic reconstruction.** The exact normalized keeper-caption message is needed, and the original final wording has not been authenticated. Investigate the provenance of the margin/final envelope copy; if unavailable, identify what additional source would satisfy it. Treat broad phrase enumeration as heuristic only.
4. **Make the evidence request explicit if no source-backed path emerges.** Ask the records custodian for a preserved copy of the printer coupon or an independent checksum tied to the exact job and attempt, plus the final handwritten/printed keeper-caption wording. Do not assert that these records are irretrievable; the repository maintainer explicitly says the problem is solvable, and that claim warrants continued investigation of overlooked supported evidence.

**Exit criteria remain unchanged:** an eight-slot candidate yielding eight individual PASS results, combined PASS, and `accepted=true` from the untouched official verifier. Until then, the honest public status is six of eight verified. This is historical records recovery only.
