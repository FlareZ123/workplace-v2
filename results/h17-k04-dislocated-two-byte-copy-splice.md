# H-17 K04: nonadjacent two-byte printer-copy splice, exhaustive source-selected attack

**Agent 16 | 2 November 2026. Result: no original K04 commitment hit.** The original 16-byte selected ESC-N ACK/RECOVER attempt-2 spool buffer has unverified physical integrity. The line begins `A9A9`; by itself that repeated byte is a weak cue, since a duplicated first byte can also occur by chance. A two-fragment copy slip or dropout is an explicit possible corruption mode, without any historical attestation that it occurred.

## Mechanism and actual advance over predecessor

Prior v1 [two-byte internal splice](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent8/k04_two_byte_splice.c) and v2 [Agent 7's equivalent implementation](../agents/agent7/k04_two_byte_internal_splice_sft.cpp) exhaustively covered deleting **one contiguous pair** of bytes and inserting **one contiguous pair** of unknown bytes: `15 * 15 * 2^16 = 14,745,600` assignments. A separated pair can dislocate two different regions of the reconstructed print text, so contiguous-splice tests do not cover it. Agent 50's two-nibble reconstruction is a distinct much smaller mutation unit; the four-source same-position mosaic does not cover positional shifts.

This new test allows removal of **any two distinct original byte positions** `d0 < d1` from the copied buffer, preserving the order of the remaining 14 bytes, followed by insertion of **any two arbitrary byte values** at `i0 < i1` of the resulting 16-byte buffer. The inserted positions can be adjacent or nonadjacent. The resulting coupon is XORed against the **unchanged** original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; the 16-byte component is SHA-256 compared with the **unmodified** acceptance commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Each of the 120 deletion pairs and 120 insertion pairs is checked against all 65,536 ordered inserted byte values, totaling **943,718,400 assignments**. Assignments may duplicate full byte strings, but the scope of enumeration is exact.

## Evidence and executable control

- Primary original 0417 ACK/RECOVER attempt2 buffer: `A9A9DC5731A5E2AE879C47215C2559D5`.
- Printer log SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- [Read-only C++/OpenSSL single-file test](../agents/agent16/k04_two_dislocated_byte_indels_sft.cpp), OpenMP loops over deletion positions; in each inner test it directly hashes the reconstructed complete 16-byte K04 component.
- Synthetic positive control uses removed positions `0,7`, inserted positions `2,11` and deliberately inserted bytes `A3,5D`; SHA-256 recognition of its fabricated control candidate occurs **exactly once**. This confirms the independently synthesized two-dislocation branch executes and checks the correct hash.
- Local execution on 2 November: all 15 first-deletion-index completion markers produced; `tested=943718400 matches=0 synthetic_hits=1 seconds=167.112`, program exit status 0.

## Interpretation

The original commitment rejects **every** selected K04 candidate in this complete two-byte-dislocation/unknown-reinsertion family, including the already-tested contiguous-pair subset. This is a precise negative for an explicit copying model. It provides no historically verified byte of the physical selected coupon, and it does not exclude three or more unpreserved bytes, a different stage/route mask, a different producer, or a non-copy encoding error. K08 remains independently unresolved. The official six individually passing slots and combined **INCOMPLETE** result are unchanged. Avoid using this result as a reason to expand unrelated arbitrary edit radii; seek source-derived copier constraints or a qualitatively different complete-candidate generator.
