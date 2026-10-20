# Agent 27: H-17 original-source acquisition and verifier checks

Claim: 2026-10-20T06:26:08Z, run `h17-agent27-b1ae54f05745`.

## Checkpoint 2026-10-20 UTC

- Random mode selector yielded **3** (normal research). Claimed `agents/agent27/.lease.json` and confirmed exact returned lease content at commit `c5e602e674fbf82e988af4a35223926572d9d250`. Memory was initially blank; no agent27 mailbox.
- Independently unpacked user-supplied `h17-archive-dump.zip` in an ephemeral local workspace: 46 non-directory files, ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. This agrees with the newer v2 provenance reporting, not the older v1 original ZIP container SHA.
- Ran **unmodified** supplied `verify.py` + `acceptance.json` with the repository's canonical six components. Result `K01,K02,K03,K05,K06,K07=PASS`, `K04,K08=MISSING`, `passed=6`, `combined=INCOMPLETE`, `accepted=false`; verifier exit code 1 (expected for incomplete).
- Consulted live v2 `results/README.md`, detailed `h17-recovery-status.md`, prior-art gate, missing-evidence issue #1, broadcasts from Critic and agents 3/6. Issue #1 was **open with zero comments** when checked. The latest v1 synthesis confirms vast prior testing; in particular exhaustive K04 exact 3-byte replacement and extensive source-only MT models, K08 caption edit/span generation, public-site source census. Both original source/commitment trees are already audited identical by other agents. No useful duplicate rerun warranted.
- Re-examined original MAIL-16 / MAIL-20, records-custodian, spool selection, note N02/N06/N10/N13/N20/N23, supplemental office bookmark. The unresolved source provenance remains K04 selected `PS-261003-0417` RECOVER ACK attempt 2 payload vs single-transcription mask, and K08 final Emily margin wording absent from current export. Both are explicitly stated as integrity/wording uncertainties by source.
- Read-only public GitHub code search for exact `IR-261003-H17.txt`, `PS-261003-0417` and nonce returned no exact independent records. GitHub code search is not comprehensive; no negative beyond that restricted index. Public web search yielded no relevant independent evidence. Existing v1 public website / urlscan / archive checks already cover meaningful other routes.
- `private/` currently contains only `.gitkeep`; no additional source. Did not change original resources, acceptance, verifier, or partial candidate. No facility systems or account access.

## Research boundary and next priorities

Need an **independent original K04 coupon/checksum or mask** plus Emily's **literal final keeper caption**; source-index lead `file:///R:/Records/INDEX/IR-261003-H17.txt` is not locally available. Do not repeat v1 9.28557-billion three-byte sweep, speculative MT donor tests, broad K08 caption HMAC guessing, public corporate page crawl, or old PDF release.

New work should identify a genuinely independent original source or a source-supported deterministic mechanism reaching target bytes and predicting withheld intact data before acceptance. The untouched REC8/1 verifier is final computational authority. Check issue #1/recent source changes periodically; do not infer absence of a remote source from a 404 or code-search empty result.
