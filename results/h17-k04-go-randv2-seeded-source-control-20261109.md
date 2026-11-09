# Go 1.23 math/rand/v2 source-derived complete-print-packet control

**Agent 21 | 9 November 2026 | K04 unresolved; original commitment deliberately not queried**

## Distinct source-to-producer hypothesis

The preserved 16-byte archive components and route fields might seed a deterministic print issuer. As a producer class distinct from previously tested MT19937, legacy Go math/rand, Java 48-bit, NumPy and xoshiro models, test the documented Go 1.23 `math/rand/v2` `NewChaCha8` and `NewPCG` output architectures. **No record says the historic printer used Go, either generator or these seed constructions.** This is an exploratory source-first exclusion, not a historical claim.

Use **13 original 16-byte values**: the six already accepted components K01/K02/K03/K05/K06/K07, K04 route mask, K08 desk nonce, K02/K03/K07 original raw pre-reducer blocks and two metadata IDs from the still-encrypted BX25-08 PDF. These are publicly visible file identity bytes only, and no encrypted page content or withdrawn password is used.

- ChaCha8 key: ordered concatenation of two *distinct* 16-byte values. 13×12 = **156** streams.
- ChaCha8 key: uppercase/lowercase ASCII 32-hex spelling of one 16-byte value. 13×2 = **26** streams.
- PCG: one value split into two 64-bit seeds, little/big endian and both half orders. 13×4 = **52** streams.

For each stream enumerate the first **20,000 consecutive 16-byte windows**, without reseeding, and compare against all **132 intact retained printer packets excluding the selected PS-261003-0417 ACK attempt-2 source**. Compare eight reversible packet views (identity, complete reversal, reversible 4-/8-byte lane changes, and 4×4 transpositions). Source SHA-256 is pinned to the official reconstructed spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

The 132 packets are *historical reconstructed copies*, not independent physically certified printer originals. This experiment tests only the stated generator/seed/output-view family and does not use K04 or K08 commitments for fitting.

## Executed source-only outcome

```text
source-only: seeds=13 streams=234 windows=20000 controls=132 matches=0 planted_chacha=PASS planted_pcg=PASS
```

This is **4,680,000 complete 16-byte candidate output windows**, with **zero matches** to the original complete-packet controls. Independent planted ChaCha8 and PCG streams recover the exact withheld complete 16-byte test packet at offset 17. The source file count, supplied accepted slots and input packet hash are checked. The test ran with Go 1.23.2 against the unchanged attached 46-file original local export.

**Consequence:** none of these 234 complete seeded Go v2 output streams exhibits even one retained real whole-packet match. There is therefore no supported basis to promote one stream to the disputed selected coupon. This has **zero target-bit information** beyond the stated bounded stream exclusion. No selected K04 physical byte or K08 final word is newly recovered; no official evidence, candidate, route, commitment or verifier is modified. Combined REC8/1 remains INCOMPLETE.

Source-pinned portable reproducer: [Agent 21 Go SFT](../agents/agent21/k04_go_v2_sft.go). To run in the repository, Go 1.23+ is required. No external dependency.


## Distinct per-print-job source-seeded issuer model (same date, supplementary test)

A shared seeded stream might fail while the issuer resets a deterministic generator for every print job. The same SFT therefore derives a **separate seed for each of the 132 real unselected printed packets** from the SHA256 digest of one of 14 direct source-metadata text forms (job, original/normalized UTC timestamp, attempt, class, destination, and standard concatenations), prefixed by one of five exact archive/job context strings. For each source-derived 32-byte seed, emit 12 consecutive blocks from Go ChaCha8; separately treat the seed's first 16 bytes as Go PCG's two seeds in little or big endian. Compare each full block in eight reversible wire views to **that exact job's** original copied 16-byte packet, not merely to a random other printer row. Crucially, no selected ACK2 copied value, K04 mask or target commitment is used for selection or screening.

Executed against the unchanged uploaded ZIP with the source-pinned Go 1.23 SFT:

```text
source-only-per-job: controls=132 forms=14 prefixes=5 generator_types=3 windows=12 wireviews=8 candidate_blocks=332640 whole_matches=0
```

Thus **332,640 predicted complete historical packet candidates** and 2,661,120 full-packet original comparisons yielded **zero exact same-job matches**. This directly tests a different issuance pattern from the earlier 234 long shared streams. A model satisfying even two independent complete heldout printer jobs would have selected the same source-derived constructor for the specified ACK2 incident job, then permitted a full K04 hash check. No constructor qualified. The test supplies no historical attribution of either Go generator, and it does not establish the presence of a deterministic per-job issuer. The selected physical K04 value and exact K08 final caption remain unknown.
