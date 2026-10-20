# Agent 4 continuity: H-17 REC8/1 archive reconstruction

**Identity claim:** 2026-10-20T05:08:42Z; lease at `agents/agent4/.lease.json` (run `60b136de2bbe4dbf44f0e04c`). Normal research mode after executed uniform 1..10 draw returned 5. Never refresh the lease; after checkpoints measure actual age and release only at >=70 minutes per prompt.

## Source-derived / validated conclusions

- Read README rules. Source ZIP supplied to this ChatGPT invocation: `h17-archive-dump.zip`, 50,526 bytes, SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`.
- **New exact source attestation:** The ZIP's 42-file `evidence/` Git tree is `0196e2bc6b207b8065f50698273db9581ca3f286`, **identical** to the live `resources/evidence` tree on `FlareZ123/workplace-v2` at inspection. Remaining four originals (`START_HERE.md`, `acceptance.json`, `candidate.template.json`, `verify.py`) also have identical Git blob IDs. Thus the uploaded ZIP contains no fresh original-source bytes relative to the repo; it is a faithful copy of the 46 source files, not an independent original witness.
- Preserved write-up `results/h17-attached-zip-integrity.md`, reusable tested Python standard-library comparison tool `work/h17_source_integrity.py`, and a summary link in `results/README.md`. Local tool output on supplied ZIP: 46 unchanged, zero changed/new/missing. Tool separately reimplements Git tree hashing; computed SHA matches a temporary Git index's tree, a useful cross-check.
- Independently ran the ZIP's untouched `verify.py` with the six previously accepted values. K01 K02 K03 K05 K06 K07 PASS; K04 and K08 MISSING; combined INCOMPLETE, `accepted=false`. Verifier exit status 1 means incomplete acceptance, not a crash. Local ephemeral candidate was a test fixture and original evidence ZIP was not modified.
- Prior research in `FlareZ123/workplace-v1` contains >180 reports on byte-identical originals. A duplicate K04 arbitrary three-byte correction sweep was already completely exhausted; K08 caption guesses and PDF/site scans were extensive. See `results/h17-v1-prior-art-gate.md`, `results/h17-evidence-coverage.md`, and v1 `results/README.md`. Do not repeat without new target evidence.

## Live blockers and plausible next actions

- **K04:** Original ESC-N printer job `PS-261003-0417`, ACK attempt 2, 2026-10-03T18:02Z, recovered payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with retained mask gives component `2CFF149C50E54557228E7DE60B3EB7C9`, rejected by K04 acceptance. ACK proves dispatch, not byte integrity. No independent original coupon or 16-byte checksum in identical uploaded ZIP.
- **K08:** Original final desk-margin caption **not quoted** in supplied notes. N02/N06 are drafts; N17/N18 different envelope labels; N23 attests a final line but doesn't include words. HMAC is a candidate verifier, not a reconstruction algorithm. Current exact text remains missing.
- Most efficient new sources: authenticated historical ESC-N coupon/buffer with job+attempt record and final verbatim Emily keeper-margin text, or an authorized archived copy of the `file:///R:/Records/INDEX/IR-261003-H17.txt` original index which may point to those records. An `R:` reference is an offline mapped-drive locator, not a public URL. Do not enter the protected online portal or guess credentials.
- Continue by looking for *genuinely new target-bearing information or independently predicted intact-source mechanism*. Report null components honestly; do not change original commitments, verifier or original evidence.

## Additional cross-repo source-history audit

- Compared **all four accessible default-branch `resources/` snapshots** in predecessor `workplace-v1` (17 Oct initial `5e03668c3652`, 18 Oct cleanup `dc04788bf7dc`, 20 Oct supplement `ca43daaec3cd`, 20 Oct editorial revision `8beda6625e89`). Original 38 pre-supplement evidence files and acceptance/checker blobs were unchanged throughout. Four office supplement files were added on 20 Oct. Sole deleted resource was `AGENT_PROMPT.txt`, inspected at initial ref; it contains only prior assignment and scope, no missing coupon/caption. Historical `START_HERE` editorial changes had no recovered bytes. Details appended to `results/h17-attached-zip-integrity.md`.
- Global GitHub code-search queries for exact `CEG-ARCHIVE-RECOVERY/v1`, `IR-261003-H17`, and original desk nonce returned no matches in available search index; web exact identifier search likewise surfaced unrelated content, no authenticated original witness. Search coverage not exhaustive.
