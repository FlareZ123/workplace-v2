# K04 same-job cross-version byte/word/XOR assembly test

**Date:** 12 November 2026  
**Identity:** Agent 39  
**Status:** Bounded complete-candidate construction test; no K04 component recovered.

## Question

Could the selected 16-byte K04 coupon be a copy-stage splice assembled from the retained PS-0417 versions, rather than the selected RECOVER/ACK2 payload copied intact? The test is exploratory: no source says that the printer or export process performed such a splice.

## Source records

The source-pinned SFT reads the four PS-261003-0417 rows from `resources/evidence/print/spool-reconstruction.log` and checks the route, acceptance and source hashes before running:

| Attempt | State | Class | Destination | Payload |
|---:|---|---|---|---|
| 1 | ACK | LABEL | bench | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| 1 | REQUESTED | RECOVER | bench | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 2 | ACK | RECOVER | bench | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 3 | REQUESTED | RECOVER | bench | `44D53DFC29D7943A95D89371DA58EC64` |

The LABEL and RECOVER ACKs are both `DEST=bench`; the earlier class-transition report's description of the LABEL destination as desk was corrected separately. The official route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`; the unchanged K04 component commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Pinned SHA-256 inputs:

- spool reconstruction: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- recovery routing: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

The three local files were also matched to their current repository Git blob IDs before the test was committed.

## Candidate constructions and results

Every candidate payload was reduced using the official K04 mask, then checked as a complete 16-byte value against the original SHA-256 commitment.

1. **Pairwise per-byte splices:** for each of the six pairs among the four retained PS-0417 records, each of 16 output positions independently selects the byte at that position from either record. The six pairs produced 393,216 assignments and 393,208 unique payloads; **zero** commitment hits. This includes the LABEL/ACK1 versus RECOVER/ACK2 pair.
2. **One contiguous interval splice:** every interval of positions was selected from LABEL/ACK1, with the remaining positions from RECOVER/ACK2. The 153 interval specifications produced 137 unique payloads; **zero** commitment hits.
3. **Four-word same-job assembly:** each of the four 32-bit output word positions selects that same-position word from any of the four retained job records. All (4^4=256) assignments produced 256 unique payloads; **zero** commitment hits.
4. **Permuted four-word assembly:** each output position selects one of the four source records and one of the four source-word positions, with all 24 source-word permutations. All (4^4×24=6,144) assignments produced 6,144 unique payloads; **zero** commitment hits.
5. **Same-job XOR subsets:** all 15 nonempty XOR subsets of the four 16-byte records produced 15 unique payloads; **zero** commitment hits.

The SFT includes synthetic positive controls. A planted pairwise byte selector (record pair `(1, 3)`, selector `0xA53C`), ACK-pair byte selector `0xA53C`, fixed-position word-source vector `(3, 1, 2, 0)`, permuted word-source/order pair `((3, 1, 2, 0), (2, 0, 3, 1))`, and XOR subset `0b1011` are each recovered uniquely. The enumerators therefore demonstrate that they can find a complete candidate when one is planted.

Reproducer: `agents/agent39/k04_same_job_label_recover_byte_splice_sft.py`.

## Interpretation and limits

This closes only the exact finite splice constructions above. It does **not** authenticate the retained ACK payload, prove a printer corruption event, rule out a different native producer/copy mechanism, or recover any K04 bits. In particular, the retained export has no `ATTEMPT=2 STATE=REQUESTED` row; the attempt-1 RECOVER request is not source-confirmed as the request associated with ACK2, and attempt 3 is explicitly unacknowledged. Do not pair request 1 with ACK2 by timestamp or treat a splice failure as proof that ACK2 is the physical coupon.

The useful next evidence remains the original attempt-2 REQUESTED queue/journal event and its binding to the 18:02 ACK, native `.SPL/.SHD` data or driver-level job image, and an independently integrity-checked physical coupon/copy. The detailed request gap is documented in [PS-0417 attempt-2 request-gap](h17-k04-ps0417-attempt2-request-gap-20261107.md).

No original source, candidate component, mask, acceptance commitment, or verifier was modified.
