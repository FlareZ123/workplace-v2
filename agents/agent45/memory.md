# Agent 45 | H-17 REC8 recovery

## Claim and scope
- Normal research mode, RNG output **7**, claimed 2026-10-20T11:12:59.104Z, run_id `h17-recovery-agent45-20261020`.
- Review date 20 Oct 2026 UTC; this agent checked the **user-provided** `h17-archive-dump.zip`, the live v2 recovery index and selected original source files. No historical target-bearing source outside the known bundle was obtained.
- Original upload ZIP SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`; 56 ZIP entries, 46 files plus 10 directories; `ZipFile.testzip()` reports no CRC errors. Prior agents already independently documented exact 46-file uploaded ZIP versus repository source equivalence. Do not promote this replication to a new source.

## Reproduced acceptance state
- Ran the untouched uploaded `verify.py --candidate candidate.json --json` with six accepted public key slots: **K01,K02,K03,K05,K06,K07 PASS**; **K04,K08 MISSING**; `passed=6`, `combined=INCOMPLETE`, `accepted=false`.
- K04 current retained `PS-261003-0417`, ACK attempt 2 payload `A9A9DC5731A5E2AE879C47215C2559D5`, XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` yields `2CFF149C50E54557228E7DE60B3EB7C9`; SHA256 `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b` disagrees with untouched target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- K08 trial of note N13 verbatim, normalized via original route and HMAC, yields `26076C5426016BDB768A2B83E9F36857`; this trial **fails** the official K08 commitment. Already known class of failure; no final-caption quotation obtained.
- Independent visual rendering/extraction of password-8131 PDF BX25/08 confirms a **2025 property carry-forward annex**, FA-17 North printer/cassette, FA-18 network desk, historical external correspondence index, no original 2026 coupon or final caption. Prior art already described this document.
- GitHub Issue #1 open, latest comment 20 Oct 08:26 UTC supplies conditional K08 WN-14 folder/underleaf preservation lead. Live private/ directory contains only `.gitkeep`. Focused public web search for exact original index/job gave no matching results; target company URL not available in the web reader.

## Source/target-information handoff gate
- **Genuinely new original historical source: NONE.**
- **K04 actual selected coupon bits independently recovered: 0/128.**
- **K08 exact final incident-caption words independently attested: 0.**
- **Original REC8: 6 PASS, 2 MISSING, combined INCOMPLETE**.
- External `workplace-v1` has >180 relevant prior reports, including K04 exact 3-byte, all 13 contiguous 4-byte and periodic 4-byte XOR negative exhaustive sweeps plus source-conditional MT nullspace proofs. See `results/h17-v1-prior-art-gate.md` and `communications/broadcast/20261020T0800Z_Critic_target-information-stopwork.md`. Avoid redoing old sweeps, normal HMAC phrase guessing, repeated verifier runs or K04 producer models without authentic unseen-output prediction.
- Canonical external-record request is [Issue #1](https://github.com/FlareZ123/workplace-v2/issues/1) for original `PS-261003-0417` ESC-N attempt-2 RECOVER coupon/checksum and Emily's verbatim incident envelope final caption; optionally authorized period original `R:/Records/INDEX/IR-261003-H17.txt`, offline print-host historical snapshot, or retained WN-14 physical underleaves.
- The offline intake gate `work/h17_witness_intake.py` already exists. If genuinely new original evidence appears, hash and preserve bytes, transcribe separately, run unchanged per-slot/combined acceptance, and establish independent provenance. No current-system access or login bypass.

## Continuation
Observe the target-information admission gate. Only publish a new substantive headline when it actually changes missing target information or source provenance. Otherwise do not add redundant broadcasts. Keep memory concise and update only for useful progress.
