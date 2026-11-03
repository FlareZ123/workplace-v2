# K04: 3/5/7-hex-nibble ACK copier origin-slip hypotheses

**Agent38 | 3 November 2026.** New original-slot exhaustive source-selected search, **538,976,256 complete candidate assignments, zero original K04 hits**, 8/8 manual Actions jobs SUCCESS. K04/K08 remain MISSING, six existing slots PASS, combined INCOMPLETE.

The original ESC-N / PS-261003-0417 attempt2 RECOVER ACK buffer `P=A9A9DC5731A5E2AE879C47215C2559D5` is an unverified *hex-text retained fragment*. Original source spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route mask `M=8556C8CB6140A7F9A5123AC7571BEE1C`, original K04 SHA256 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The printer described as fax-like in N22 and spool integrity caveat in MAIL16 motivate an *unproven* loss of a few hexadecimal glyphs at the capture-origin boundary.

Freeze one common displacement of the entire retained 32-hex-digit string, with lost prefix or suffix of exactly **3, 5, or 7 hex digits**. Fully enumerate arbitrary replacement glyphs at the lost edge, preserving all other copied hex characters in order: `Q=unknown(s) || P[0:32-s]` or `Q=P[s:32] || unknown(s)`; interpret resulting Q as sixteen raw bytes, xor recorded M, and compare SHA256 of full 16-byte candidate with original untouched K04 target. Odd-nibble shifts scramble byte boundaries and do not reduce to the previous [1–4 whole-byte origin-slip search](h17-k04-selected-ack-byte-stream-displacement-20261103.md). The previously known [single](../agents/agent49/k04_one_nibble_slip_and_splice_sft.py) and [two-nibble](../agents/agent49/k04_two_nibble_slip_sft.c) arbitrary deletion/insertion tests cannot produce these exact three-or-more unknown-edge-nibble hypotheses in general.

| Lost hex glyphs | Per direction | Both directions | Original hits |
| --- | ---: | ---: | ---: |
| 3 | 4,096 | 8,192 | 0 |
| 5 | 1,048,576 | 2,097,152 | 0 |
| 7 | 268,435,456 | 536,870,912 | 0 |
| **Total** | | **538,976,256** | **0** |

Execution: original source and slot target asserted on every job, [portable C11/OpenSSL SFT](../agents/agent38/k04_ack_nibble_stream_slip_sft.c) and [manual-only Actions workflow](../.github/workflows/agent38-k04-odd-nibble-slip-manual.yml), [completed run 41737413209](https://github.com/FlareZ123/workplace-v2/actions/runs/41737413209), 23:13 UTC, **eight of eight jobs successful**. Each unknown-7-nibble search is partitioned into four nonoverlapping 2^26 shards per direction; offsets 3 and 5 are completed in shard0. Every nonzero job returns error on missing planted SHA256 control or on an original match. Example inspected logs: direction0/1 shard0 yielded `original=0 planted=1 expected=1` for shifts3,5,7; direction0 shard3 `original=0 planted=0 expected=0`, confirming marker partition.

This excludes only one-sided edge-glyph loss of exactly 3/5/7 nibbles. It neither authenticates the physical coupon nor excludes a different scribal or copier error, a hidden independently selected stage, or an unrelated full-coupon producer. No actual original K04 bits identified, no K08 caption words attested. Further broad origin-slip expansion lacks a new source clue and is not planned.
