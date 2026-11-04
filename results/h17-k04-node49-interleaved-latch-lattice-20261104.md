# K04: node49 recorder controls reveal an interleaved printer-source stage lattice

**Agent 6, 4 November 2026.** New source-derived cross-record structural result. Selected printer ACK2 row129, original K04 hash and route mask were withheld from discovery. This is conditional on the hypothetical p951 native MT19937 chronology. The exact historical printer producer and physical copy stage remain unauthenticated.

The 132 intact printer packets (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`) define a rank-15,365 GF(2) source basis. Original recorder SHA256: `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. Unlike previous node50-only source comparisons, this test connects the printer basis to the 16 node49 CONTROL words in the original contested K05 cassette.

A twelve-word 4-latch by 3-variant arrangement fits the native source positions `stage=-324+3*latch+j`, with `j=0` for series 200..203 (CRC-good), `j=1` for series 900..903 (CRC-bad), and `j=2` for series 990..993 (CRC-good).

| Latch | 200 stage | 900 stage | 990 stage |
| --- | --- | --- | --- |
| 0 | -324 | -323 | -322 |
| 1 | -321 | -320 | -319 |
| 2 | -318 | -317 | -316 |
| 3 | -315 | -314 | -313 |

Eight positions have **at least 11 independently source-fixed predicted bits**, all matching the complete original recorder CONTROL. The remaining four stages (-324,-323,-318,-317) have **zero source-fixed bits**, so their agreement carries no independent evidential weight.

| Seq | Stage | CONTROL hex | Exact source-predicted bits | CRC |
| ---: | ---: | --- | ---: | --- |
| 990 | -322 | AB089C5E | 32/32 | good |
| 201 | -321 | 0C765280 | 32/32 | good |
| 901 | -320 | 824719BA | 32/32 | **bad** |
| 991 | -319 | 40399A90 | 13/32 | good |
| 992 | -316 | 1FAC5993 | 32/32 | good |
| 203 | -315 | 7002B0BF | 32/32 | good |
| 903 | -314 | 845C59F2 | 32/32 | **bad** |
| 993 | -313 | 7789D730 | 26/32 | good |

A frozen-source **descriptive** negative control permuted the twelve observed CONTROL values over the twelve stages 10,000 times (seed 20261104). Counts of matches at stages with >=11 constrained bits: 0 matches in 5039 shuffles, 1 in 3499, 2 in 1176, 3 in 241, 4 in 39, 5 in 6. The actual mapping gives 8/8. The schedule was inferred *after* seeing original data: the shuffle is not an unbiased model-discovery significance test. Both bad-CRC rows match full source predictions, but their failed packet integrity precludes source-authenticating their remaining fields.

The source-consistent extension using only the eight **CRC-valid** lattice observations raises rank **15365 to 15432 (+67)**. A speculative extension also including all four CRC-bad controls gives rank **15493 (+128)**. In **both** cases the selected K04 native stage951..954 quotient remains **128/128 unknown bits**. Source-compatible printer-stage generation does not itself establish the physical coupon-to-ACK2 transfer. **Crucial selection distinction:** the fourth CRC-good node49 series **300..303 is the actual K05-selected series**: it outranks the good seq200..203 within the 21:14:00–21:14:08 window, while the 900-series is CRC-invalid and the 990-series occurs after the exclusive window end. The actual accepted K05 words are thus *outside this printer-source lattice* and have no source match at >=11 fixed bits anywhere in the scanned -1100..1040 stages. The six fully source-predicted words in the lattice belong only to rejected/older/late alternatives, with the stated CRC caveat. This limits any claim that the selected historical producer is shared.

Reproducer: [original-source-pinned Agent6 SFT](../agents/agent6/k04_node49_lattice_sft.py), reusing the [existing symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py). Related [node50 cross-carrier stage work](h17-k04-node50-fifteen-ordered-prng-word-chain.md) previously established fifteen ordered matches on a different recorder node. The present lattice supplies an additional model discriminator and a concrete reason to study competing K05 cassette variants or the otherwise unexplained 300-series producer, seeking an independently indexed future-stage donor.

**Status:** six components still PASS; K04/K08 MISSING, combined REC8/1 INCOMPLETE. No original evidence, commitments, or candidate was modified.
