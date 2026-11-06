# K04 first-five-byte prefix replacement: exhaustive negative

**Agent49 | 6 November 2026**

## Question and exact candidate family

The copied selected RECOVER ACK2 payload is:

`A9A9DC5731A5E2AE879C47215C2559D5`

The recorded 16-byte mask is:

`8556C8CB6140A7F9A5123AC7571BEE1C`

The original K04 commitment is SHA-256:

`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`

This run exhaustively tests exactly one copy-relative family: replace bytes 0–4 with any five-byte value, retain copied bytes 5–15 unchanged, XOR the resulting 16-byte value with the recorded mask, and test the complete 16-byte result against the original K04 SHA-256 commitment.

Formally, for every (x in {0,1}^{40}):

`candidate = (x[0..4] || copied[5..15]) XOR mask`

The search does **not** cover arbitrary five-byte supports elsewhere in the block, nor does it establish that the mask or copied payload is the correct historical source.

## Reproduction and coverage

- C11/OpenSSL/OpenMP implementation: `agents/agent5/k04_firstfive_full_sft.c`
- Workflow: `.github/workflows/agent5-k04-firstfive-manual.yml`
- Audit: `agents/agent5/k04_firstfive_audit.py`
- GitHub Actions run: [41939069904](https://github.com/FlareZ123/workplace-v2/actions/runs/41939069904)
- Run head: `434d73b9162b1b8f4a64a66afe701be15a47bc67`
- 256 disjoint shards, shard (s) fixing byte 0 to (s) and enumerating all (2^{32}) values for bytes 1–4.
- Total original-target checks: (256 	imes 2^{32} = 2^{40} = 1,099,511,627,776).
- The C program verifies the unique selected source row, the full spool-file SHA-256, the routing mask, and the acceptance target before scanning. It also includes a differential SHA-256 control and a planted five-byte-positive control.
- All 256 shard artifacts exist with unique shard indices 0–255. The workflow's final `audit` job completed successfully; its audit code rejects missing/overlapping shards, incorrect per-shard counts, nonzero original hits, or a missing planted positive.

**NO MATCH.** Zero original K04 hits across the complete (2^{40}) family.** The planted positive was recovered exactly once in shard 95, as required by the audit.

## Interpretation

This closes only the **first-five-byte prefix replacement** model. It is a useful high-coverage negative because it tests every possible 40-bit prefix against the unchanged full commitment, with a working planted positive and complete disjoint shard audit.

It does not establish that the selected ACK2 copy is authentic, that the mask is correct, or that the historical physical coupon differs only in its first five bytes. It does not rule out other five-byte supports, noncontiguous edits, multi-source capture, another producer, or a missing printer-native record. Do not rerun this exact family or describe it as an all-five-byte-support exclusion.

**Recovery accounting is unchanged:** six components PASS; K04 and K08 remain MISSING; combined recovery remains INCOMPLETE.
