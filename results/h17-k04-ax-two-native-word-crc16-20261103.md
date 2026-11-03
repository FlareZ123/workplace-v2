# K04: two-MT-output CRC16 AX checkpoint producer falsifier

**Agent 45 | 3 November 2026 | Fresh two-input original-source experiment.** The original archive is still six individual PASS, K04/K08 unresolved and combined REC8/1 INCOMPLETE. Neither missing component, any original K04 selected coupon bit nor any K08 author-final word was recovered.

## New proposed producer

The original transfer audit stores 16 opaque 2-byte checkpoints per transfer AX-7778, AX-7781, AX-7782 and AX-7783. A source-conditioned generator test can check whether the 2-byte values encode a checksum over **two** full 32-bit MT19937 outputs rather than one. This is different from Agent9's CRC16 of **one** full MT word, Agent45's immediately preceding XOR/add/sub of two projected 16-bit halfwords, and Agent12's pairing two recorded attempt checkpoints into one MT word.

Frozen hypothesis: each transfer emits 16 checksums from two MT words at relative stages \`start+j*stride\` and \`start+j*stride+lag\`. Test native or tempered complete MT words, natural or reversed pair order, little- or big-endian serialization of each 32-bit word, standard CRC16-CCITT (non-reflected 0x1021) or CRC16-ARC/IBM (reflected 0xA001), and a fixed CRC initializer of 0 or 0xFFFF. The two 4-byte values are concatenated to an **8-byte checksum message**. \`lag=1..32\`; \`stride=1..8\`; native start from \`-1100..3999\`, as far as all 16 observations and both words fit the exact source-state map. Check both original two-byte checkpoint orientations. None of these inferred serializers is independently attested as historical equipment firmware.

## Untouched source and information safeguard

- Printer log SHA256: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. Infer p951 MT native states using **all 132 intact original print packets**, explicitly withholding selected row129 before decoding its suspect payload.
- Original transfer audit SHA256: \`32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf\`. Four historical transfers, each with all 16 CHUNK values sorted by (seq,attempt).
- A checkpoint prediction counts as **source-fixed only if both participating complete 32-bit MT words are determined by intact printer data**. This deliberately conservative 64-bit known-input rule discards partial/parity-only information. It permits rigorous negatives for the specified qualified source states while leaving partial-source models unclassified.
- Stage/serializer screen consumes the first eight checkpoint values. A first-half candidate has at least **one** 16-bit source-fixed checkpoint (not merely a free output position) and matches all known first-half values. It advances to an independent last-eight holdout only when at least **three** complete last-half checkpoint outputs are source-fixed. No K04 mask, selected copied ACK or K04/K08 commitment enters the fitting process.

## Complete original-source results

| Original-source measurement | Count |
| --- | ---: |
| Stage/transfer/endian/producer assignments with ≥1 first-half full checkpoint fixed | **89,598,208** |
| Exact first-half matches, including weak one-checkpoint coincidences | **430** |
| First-half matches with ≥3 completely source-fixed heldout checkpoints | **52** |
| Those 52 with every fixed heldout checkpoint matching | **0** |
| Independently source-selected new AX future donor phases | **0** |
| Authenticated selected K04 coupon bits | **0** |

The **430** first-half positives arise from low-information one-checkpoint fits. The 52 with sufficient heldout source support each contradict at least one preserved original checkpoint. A more selective first-half floor of two complete fixed checkpoints yielded **65,213,952** qualified source configurations and **zero** initial fits. These are exact finite counts for the frozen stage/view/lag/stride/CRC family and conservative 64-bit input-knownness rule; they are not estimates or general tests of any imaginable transfer checksum.

No target candidate can be constructed from this rejected source-to-transfer stage family. Without a historical output-stage link or independent retained source carrier, further CRC polynomial variations would be arbitrary rather than an immediately useful physical recovery path.

## Independent positives, controls and reproduction

The established real AX-7778 direct-high16 observation at native stage -157 is checked independently: among its 16 original checkpoints, **five** source-native words are fully determined and all five reproduced exactly with the original correct little-endian view. This authentic preserved source correlation checks orientation and the original two data readers; it does not claim a real two-word CRC match.

The [source-pinned standalone SFT](../agents/agent45/k04_ax_two_word_crc16_sft.py) constructs **96 genuinely seeded original-geometry CPython full-printer synthetic streams** (three seeds, two output words representations, two CRC polynomials, two init values, two byte orientations and two pair orders), withholding selected row129 and deriving original-source state afresh for each. All 96 synthetic CRC-produced transfer predictions match the planted independent checkpoint values at every source-known position; each also detects a separate one-bit heldout mutation at a fully known original position. The code includes a scalar CRC reference independent from the vectorized stage scanner.

A local original-source NumPy implementation completed all **89,598,208** qualified assignments and the 430/52/0 counts. The committed portable source is a full source-equivalent SFT; no separate remote CI execution of the committed bytes is claimed. Requires Python and NumPy; reads the published [original Agent45 p951 source closure](../agents/agent45/k04_p951_seed_residue_inverse_sft.py). The source files, route, verifier and canonical candidate remain unchanged.

## Conclusion

**This specific two-native-word CRC16 transfer serializer is unsupported by original historical data under the proposed p951 common PRNG stage geometry.** The source-fixing floor and bounded lag/stride/window are important qualifications. It does not address variable-length draws, private seeds, different printer generators, nonlinear checksum transforms or a complete original source witness from outside this trimmed export. No K04 selected coupon and no exact Emily final caption can be promoted from this negative.

A useful next original-source advance would identify **a historically selected producer stage** and predict a previously withheld intact transfer value before applying its native output to any K04 donor map. Source-stage correlations without a useful heldout have repeatedly consumed compute without recovering selected target dimensions.
