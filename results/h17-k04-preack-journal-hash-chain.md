# H-17 K04: pre-ACK cryptographic journal digest and rolling checkpoint candidates

**Agent 8 | 3 November 2026.** New complete-coupon construction from the **129 preserved chronological printer rows before the selected 18:02 ACK**. Original K04 commitment: **zero matches**, with an independently planted end-to-end digest-positive control and rolling-chain control.

## Causal source proposal

The source says a north escrow RECOVER coupon was printed and warns that the reconstructed 18:02 payload is not integrity-authenticated. An alternate upstream generation rule could have printed an **archive journal checkpoint** computed from earlier records, rather than an independent random 16-byte token. Previous [pre-ACK cohort aggregate](h17-k04-preack-cohort-aggregate-escrow-sieve.md) already exhaustively tested XOR/sum across source intervals and selected metadata groups. [Crossslot HMAC producer](h17-k04-crossslot-hmac-perjob-producer.md) tested keyed *per-job* metadata. **This experiment tests cryptographic digests of *multi-record original journal content*, including a rolling hash chain.** No original mail or firmware documentation independently attests either checkpoint producer.

Source spool SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected `2026-10-03T18:02:00Z PS-261003-0417 RECOVER ACK2` is withheld from candidate generation and used only to establish the event boundary. The unchanged 16byte route XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. Every candidate is the first or final 16 bytes of its source digest XORed with this mask and compared by **full original SHA-256 of the 16-byte K04 component**, digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Source-defined digest family

Retain the 129 original pre-ACK chronological rows, and 18 unchanged category projections: all, ACK-only, REQUESTED-only, the three CLASS values, three DEST values and nine CLASS × DEST pairs. For each category, choose a contiguous prefix/interval from the original 129-row chronology, preserving order and skipping rows outside the category. Reject empty projections. Three original record serializations: sixteen raw PAYLOAD bytes; 32 ASCII uppercase hex characters; entire preserved spool line plus newline. Hash each selected sequence using MD5, SHA1, SHA256 or BLAKE2s, then select first or last 16 digest bytes.

A second *rolling checkpoint model* uses the same category/serialization selections, chronological or reverse order, one of four fixed initial chain states (empty, 32 zero bytes, original route mask, literal `H17-IR-261003\n`) and two update rules: `SHA256(state||next_record)` or `SHA256(next_record||state)`. Test both digest halves at every nonempty prefix, rather than only the terminal checkpoint.

| Distinct construction assignment type | Complete original K04 comparisons | Original matches |
| --- | ---: | ---: |
| Direct digests of ordered nonempty intervals | **3,146,256** | **0** |
| Stateful chained SHA256 checkpoints | **61,920** | **0** |
| **Total** | **3,208,176** | **0** |

Locally executed original-source analysis. The direct-digest engine found **22 equivalent assignments** yielding an independently planted source-derived 16-byte component, a consequence of empty-category rows at the ends of equivalent intervals. The rolling-chain positive control independently recalculated an 11-record chain and matched the enumerated complete coupon. Source hashes, original selected event and mask are asserted. These controls check the algorithm and original reduction path; they do not authenticate the checkpoint model.

Reproducer: [Agent8 single-file source-pinned SFT](../agents/agent8/k04_preack_digest_chain_sft.py). Original source, acceptance, candidate, route and verifier were not edited. The publication version has the same frozen selectors and checks as the executed version; no independent CI run is claimed.

## Limits

The precise **pre-ACK multi-row digest or rolling SHA256 journal-checkpoint** model is a negative complete-candidate construction. It does not exclude unknown keyed digests, a different content domain, post-ACK source rows, a physical coupon outside the preserved spool, or a separate byte-production mechanism. Its 3.2 million hashes reveal **zero independently authentic original K04 bits**. Emily's K08 author-final words remain unavailable. Six K01/K02/K03/K05/K06/K07 individual commitments PASS, K04/K08 MISSING and combined REC8 INCOMPLETE.

Future work should use a source-selected coupon origin or editor-revision rule; simply expanding unrestricted hash separators and category subsets after this zero-hit result has little diagnostic value.
