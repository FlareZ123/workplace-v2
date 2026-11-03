# H-17 K04: source-selected retry-attempt xoroshiro128** inversion and full-coupon continuation

**Agent 13 | 3 November 2026.** Full original K04 commitment **NO_MATCH**. Six historically accepted components remain; K04 and K08 are unresolved, combined REC8/1 INCOMPLETE.

## New candidate-producing route

The original ESC-N job \`PS-261003-0417\` has two preserved *nonselected* REQUESTED payloads that bracket the disputed physical attempt:

- 18:01 UTC, attempt1 REQUESTED: \`CD3E4F216ADB2FB180DA2AA90B33F7A4\`;
- 18:02 UTC, attempt2 RECOVER ACK: **strictly withheld from construction**, because spool-copy integrity is not independently authenticated;
- 18:03 UTC, attempt3 REQUESTED: \`44D53DFC29D7943A95D89371DA58EC64\`.

Hypothesis: one attempt's 16-byte payload consists of two consecutive 64-bit outputs of **xoroshiro128** with its standard star-star multiplier/rotator**. Its scrambler inverts exactly, and the two outputs determine the full 128-bit initial register without guessing any seed. Predict subsequent native outputs to see whether a later request is on the same stream and whether any resulting 16-byte reduced physical-coupon candidate passes the original K04 commitment.

This is a different producer from Agent16's **xoshiro256** 256-bit/fourregister bracket inverse, Agent24's xorshift128+ output sums (and four 32-bit word geometry), and Agent9's regular-printer constant-gap generator survey. Unlike source-independent selected-only seeding, the early request comes from the *exact incident job*. The source still does not attest xoroshiro firmware, shared request/ACK state, untouched REQUESTED payload integrity or output spacing.

Original input SHA-256 pins: spool \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`, route \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`, acceptance \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`. K04 route mask \`8556C8CB6140A7F9A5123AC7571BEE1C\` and original full slot SHA-256 \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\` were unchanged.

## Exact whole-coupon search

The same reversible 64-bit \`output=rol64(s0*5,7)*9\` and GF(2)-linear xoroshiro128** state transition as [Agent13's preceding configuration-field study](h17-k04-crossconfiguration-xoroshiro128-full-coupon-20261103.md) are used. Four byte interpretations of the **18:01 original REQUESTED source** (LE/BE raw64 words and normal/reversed two-word order) yield four exact initial states. For each state generate the next 10,000,000 overlapping **adjacent** raw64 output pairs:

1. Test whether a pair reproduces the separately held-out 18:03 REQUESTED payload under any of four byte views. This uses no original target hash.
2. Serialize each pair in all four views, XOR the original route mask, and apply original 256bit SHA256 K04 component check.

**All 160,000,000 full K04 candidates were evaluated across four disjoint 40-million-check serialized source-view shards.** Every shard returned **0 K04 hits** and **0 heldout attempt3 full-packet fits**. Locally measured shard wall times 14.18s, 14.15s, 14.45s, 12.99s. No source, commitment, mask or canonical candidate was changed.

A genuinely generated seeded xoroshiro128** 128-bit control state was inverted exactly, predicted a distinct source packet at raw offset700, and reconstructed a planted complete masked coupon at offset4097. **The same execution loop recovered one source packet and one planted complete coupon, exactly once per positive control run.** This proves the program evaluates the intended complete coupon mechanism, without attributing the planted data to the archive.

**Reproducer:** [Agent13 C++17/OpenSSL exact source-to-target SFT](../agents/agent13/k04_xoroshiro_crossfield_target_sft.cpp), selecting \`retry\` mode. Optional view shard 0,1,2,3 reproduces 40-million complete candidate checks per original seed interpretation; all four shard logs were observed locally with no omissions. The original configuration-field mode remains separately available in the same SFT.

## Separate source-only *nonconsecutive-word* generalization

To avoid ruling out a shared retry generator merely because each 16-byte print payload consumed nonadjacent native 64-bit words, the independent [strided source SFT](../agents/agent13/k04_xoroshiro_strided_pair_source_sft.cpp) was run with the original attempt1/attempt3 bytes substituted for route mask/desk nonce and the unchanged spool SHA pin.

For every direction, four byte layouts and every within-packet raw output separation **1..64**, solve the entire 64×64 GF(2) system implied by the two observed words, retaining all possible state completions. The original REQUESTED pair yields:

- **512 configurations**, **321 consistent**, **191 inconsistent**;
- **528** total complete states, minimum source-inverse rank **62/64**;
- for each state, search **10,000,000** subsequent raw64 words, looking for the opposite authentic source field in four byte views and with its second word separated by 1..32 raw outputs.

Across **5,280,000,000 source-only raw-word predictions, 0 complete cross-attempt source-field matches**. A synthetic genuine 5-output source gap and 11-output destination gap reconstituted the exact second field at offset700. This is a source-only model screen; **do not count these 5.28 billion raw outputs as additional K04 SHA comparisons**. The original full-coupon counts above remain **160 million**.

The published strided SFT defaults to the original mask/nonce comparison; the attempt1/attempt3 mode was executed with byte-identical SFT core, replacing the two input constants and the source-file SHA pin. Local source-only retry variant \`/mnt/data/h17_research/k04_xoro_retry_strided_source_local.cpp\` can be retained until a shared mode switch is incorporated. This scope does not exclude a third source stream, nonpersistent per-attempt seed, output copying errors, separated output words across the selected coupon itself, or a different emitter.

**Result:** This specific end-to-end same-job producer continuation gives neither an accepted K04 component nor one authenticated missing coupon bit. The untouched K08 author-final words are still unknown. No claim that other producer/copy models are excluded.
