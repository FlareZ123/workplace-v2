# Agent 10 continuity | H-17 REC8/1

**Current incarnation:** run `h17-a10-3a319aa67b51fd10`, claimed 2026-10-20T07:31:16Z. Selected normal research mode by executed uniform 1..10 RNG (result 1). Lease in `agents/agent10/.lease.json` remains in force until measured 70 minutes.

## Source and verification findings

- Actual uploaded `/mnt/data/h17-archive-dump.zip` is 50,526 bytes with SHA-256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. Contents match existing prior [zip/tree report](../../results/h17-attached-zip-integrity.md), with no new target-bearing originals. Unpacked locally into `/mnt/data/h17-archive` (local working directory, not guaranteed persistent).
- Executed the ZIP's **unmodified** `verify.py` and `acceptance.json` on the six known values: K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, `combined=INCOMPLETE`, `accepted=false` (checker exit code 1 as intended). Canonical candidate [`candidate.json`](../../candidate.json) is the same partial state.
- K04 last-ACK attempt-2 source payload `A9A9DC5731A5E2AE879C47215C2559D5` XOR original commissioning mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives `2CFF149C50E54557228E7DE60B3EB7C9`, rejected by original K04 SHA256 commitment. No signed independent coupon currently supplied.
- K08 source `evidence/crew/noticeboard-and-desk-notes.txt` contains Emily's N02/N06 **drafts**, N13 reminiscence, N20 themes and N23 statement of a final margin but no literal final text. No original quotation or deterministic edit rule was found; a semantic restatement is not an HMAC preimage witness.
- Read and visually rendered the original encrypted BX25/08 PDF with published numeric release setting 8131: one 2025 office-property folio, no coupon or final caption. Public company site/supplement, ZIP wrapper audit, source history and K04/K08 method frontier extensively covered already in [v1 research](https://github.com/FlareZ123/workplace-v1/blob/main/results/README.md) and current [v2 prior-art gate](../../results/h17-v1-prior-art-gate.md). Do not rerun them without independent source.

## Concrete contribution this incarnation

Transferred a previously underreported **four-byte K04 negative search gate** from v1 to v2 [`results/h17-v1-prior-art-gate.md`](../../results/h17-v1-prior-art-gate.md), [`results/README.md`](../../results/README.md), and [broadcast](../../communications/broadcast/20261020T0743Z_agent10-four-byte-prior-art-gate.md). Independent predecessor full 2^32 checks at **all 13 contiguous four-byte offsets** total 55,834,574,848 replacement assignments, zero accepted K04. A 2^32 repeated-four-byte-XOR-wordlane full scan also returned zero. These are conditional corruption-class exclusions, not discovery of new coupon bits; v1 has positive controls, source SHA and details. Useful to avoid burning v2 CI on duplicate cases.

## Open priorities

1. Preserve source-provenance gate: request authenticated original `PS-261003-0417` ESC-N North RECOVER **attempt 2 ACK**, 2026-10-03 18:02Z, *independent uncorrupted 16-byte coupon* or independent mask/checksum. See [source intake issue #1](https://github.com/FlareZ123/workplace-v2/issues/1) and read-only [witness intake gate](../../results/h17-original-witness-intake-gate.md).
2. Request Emily's contemporaneous **exact final keeper-margin inscription**, not draft N02/N06 or standby label; original image plus source/custody metadata. The original HMAC normalization is fixed by `evidence/recovery-routing.json`.
3. A new K04 producer model is useful only if grounded in independently observed target-ancestor bytes (or makes a held-out intact-source prediction) and reduces actual selected K04 uncertainty. Consult predecessor [causal 128-bit MT nullspace](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-p955-constructive-128bit-causal-nullspace.md) before launching a source-only MT brute force.
4. Check GitHub issue #1 for any genuine custodian source release and cross-agent broadcasts before launching overlapping work. Latest issue viewed 07:33Z had one intake readiness comment, no new archive bytes. Avoid accessing protected company correspondence portal without authorized source.

**Status:** no real seventh/eighth PASS. All original official source, commitments, and checker remain unchanged.
