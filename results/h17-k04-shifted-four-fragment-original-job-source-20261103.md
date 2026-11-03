# H-17 K04: four freely shifted fragments from all same-job printer buffers

**Agent 25, 3 November 2026.** New original-source-based complete-coupon reconstruction hypothesis, exhaustively rejected under its stated fragment geometry: **233,971,712 full K04 candidate assignments, zero original commitment matches.** Six known original slots remain accepted; K04 and K08 remain missing; combined incomplete.

## Competing physical-copy model

The only selected record is ESC-N, job PS-261003-0417, RECOVER ACK attempt2, 18:02 UTC. Its copied 16-byte payload lacks independent media integrity. The original spool retains four buffers of this *same* job: a 16:45 LABEL ACK, 18:01 RECOVER REQUESTED, 18:02 RECOVER ACK, and 18:03 RECOVER REQUESTED. This experiment supposes that a printer's four-unit spool/copy assembler selected four contiguous four-byte fragments from those surviving buffers, with independent source offset and byte direction per fragment, to form the original 16-byte coupon. The crew's description of a printer behaving like a fax motivates an offset/scan corruption trial, but **does not authenticate that this happened**.

Agent16's prior 4^16 exhaustive same-job byte mosaic allows copying each byte from one of four source buffers **only at the same byte position**; the present test additionally permits **arbitrary starting offsets 0..12** for each four-byte fragment and reversal within that fragment. Agent11's 4-word quartet mosaic instead used six accepted slots and their prehash precursors, different source blocks. General shifted four-byte source fragment assembly is thus a distinct candidate-construction hypothesis rather than a repeat of either test.

## Frozen source and test

Unmodified spool source SHA256: **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**. Four source buffers in job order:

1. 16:45 ACK LABEL: E1E60D5F6B6DD2225FA6D5A2A63AD932
2. 18:01 REQUESTED RECOVER: CD3E4F216ADB2FB180DA2AA90B33F7A4
3. 18:02 ACK RECOVER, copied and disputed: A9A9DC5731A5E2AE879C47215C2559D5
4. 18:03 REQUESTED RECOVER: 44D53DFC29D7943A95D89371DA58EC64

For each source, choose one of the 13 contiguous four-byte windows, and optionally reverse its byte order: **4×13×2=104 unique four-byte fragments**. Build each fourword full candidate by choosing four independent fragments in original output positions. This gives exactly **104^4 = 116,985,856 unique full 16-byte buffers** (uniqueness of the 104 fragment values verified). For every candidate check both original acceptance interpretations: (i) XOR the original 16-byte route mask **8556C8CB6140A7F9A5123AC7571BEE1C**, and SHA256 the reduced component; (ii) SHA256 the unreduced, direct buffer. The original unchanged K04 commitment is **930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0**. Thus exactly **233,971,712** complete stage-candidate assignments are tested; no claim of between-stage uniqueness is needed.

## Results, positive control and scope

[Original-data, single-file C++17/OpenSSL SFT](../agents/agent25/k04_shifted_four_fragment_sft.cpp) tests all 104 first-fragment choices in four nonoverlapping ranges. Each shard covers **58,492,928** full stage assignments. All four runs completed with exit status 0, zero original K04 matches, and source uniqueness assertions satisfied. Measured shard wall times were **18.239, 17.512, 17.920, and 18.052 seconds**.

A separately planted synthetic full component constructed with nonzero window shifts, distinct buffer choices and byte reversal was recovered **exactly once** by the complete masked-path enumeration, confirming the reconstruction and hashing procedure can detect a real in-family positive.

This eliminates only the stated *same-job, four contiguous 4-byte fragments with arbitrary 0..12 offsets and per-fragment orientation* hypothesis, under the two reducer readings and unchanged original mask/commitment. Arbitrary original source loss, more than four fragments, bit shifts, a missing true coupon, or other generator/transport architectures remain open. The selected ACK contents are disputed, and the experiment adds **0 authenticated original K04 bits**, **0 author-final K08 words**, and **no seventh verifier PASS**.

The practical learning is that introducing shifted four-byte source windows to the previously tested same-job byte-source model does **not** reconstruct a valid K04 candidate. Repeating this precise fragment class with a different enumerator or sharding policy is unnecessary without a new source or physical fault witness.
