# K04: mixed-endian native MT recurrence templates do not complete the selected coupon

**Agent 1 | 23 November 2026 | Controlled original-source test; K04 remains missing.**

## New model and decision

The existing lane-mosaic experiment examined 24 four-word permutations with a **uniform** little- or big-endian order for all four native 32-bit payload words. The incident printer route does not attest an output serializer. This experiment allows **each native output lane to have its own big/little-endian presentation**, crossed with all 24 packet-word permutations. There are 384 fixed views, including 336 previously untested mixed-endian views and the 48 pre-existing uniform views.

For every view, untemper each authentic intact original 32-bit packet word, find the exact three-row native MT recurrence `native[l][q] = native[k][i] XOR twist(native[r][p-1],native[r][p])` with `r<k<l`, and preserve each target-independent historical row-offset/lane signature. Translate signatures to selected row129 using two intact earlier packet donors. Only views that supply all four complete predicted target 32-bit words emit a physical 16-byte coupon. Serialize according to the tested view, XOR the untouched K04 route mask, and check the full original K04 SHA256 commitment.

The source is SHA256-pinned `resources/evidence/print/spool-reconstruction.log` (`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). The PS-261003-0417 attempt-2 ACK row is identified by date/job/attempt/class/state metadata and its disputed original PAYLOAD is **omitted before hex decoding**. No selected bytes or target digest are used to learn recurrence witnesses or lane options.

## Measured results

| Domain | Views | Maximum native recurrence witnesses | Complete K04 coupon assignments | Original SHA256 hits |
| --- | ---: | ---: | ---: | ---: |
| **Mixed per-lane endianness** | **336** | **14** | **0** | **0** |
| Existing uniform-endian control | 48 | 31 | 16,189 | 0 |
| Total | 384 | 31 | 16,189 | 0 |

The original little-endian, forward-order witness count reproduces **25** exact source recurrences. The 16,189 uniform-view assignments are enumeration events across permutations and may contain duplicates; they are not claimed as new candidate coverage beyond prior fixed-view work.

Three genuine `random.Random` MT-stream synthetic controls cover two mixed-endian permutations/flags and one uniform view. Each yields **43** exact recurrence witnesses and recovers the true 32-bit target word at lane3 under the frozen seven-output spacing; serialization/de-serialization round-trips all four native words. The other three target lanes are intentionally absent from the donor signature set under that planted stage geometry. These controls validate source parsing, native recurrence and partial-lane reconstruction. They do **not** assert a synthetic full-target recovery under a geometry where the required donors are absent.

## Inference and future use

Under this particular *fixed per-lane word-endian + permutation + observed-row signature transfer* mechanism, none of the 336 mixed views can construct even one complete selected coupon, so this variant cannot give a K04 commitment PASS. It does **not** exclude independently corroborated mixed-endian printer output, other donor relations, stage evolution, copy-state transformations or unknown original physical print media. Full-source global stage models and their missing residual bits are separate hypotheses.

Reproducer: [Agent 1 standalone SFT](../agents/agent1/k04_mixedendian_source_sft.py). Locally executed against the unchanged user-supplied original source and original commitments; genuine planted controls and exact result assertions passed. The shared original `candidate.json`, verifier, acceptance commitments, spool and source files were unmodified. No K04 key was recovered.

**Next decision:** a proposed serializer should be supported by original native job/host metadata or a new high-quality intact-packet holdout. Additional mixed/endian spelling variants of the same observed-row recurrence templates have no demonstrated target-reaching payoff.