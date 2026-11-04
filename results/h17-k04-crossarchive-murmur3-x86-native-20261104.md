# K04: invertible MurmurHash3 x86-128 native-state cross-archive source test

**Agent13 | 4 November 2026 | 16,016 full original K04 candidates; zero original matches**

## Independent candidate-producing architecture

Agent46 previously inverted **MurmurHash3_x64_128**, a two-lane 64-bit algorithm, against selected source objects and found no common record-identity state. The public-domain MurmurHash3 implementation has a **different x86-128 construction**, using four 32-bit native accumulators, four distinct per-lane tail mixers and a different finalization function. This experiment independently inverts the **x86-128** architecture to test whether public record identities select a reproducible shared 128-bit secret state and then generate a previously missing 16-byte printer coupon.

The original source never says MurmurHash3 was used in the H-17 devices. The public API ordinarily initializes all four x86-128 accumulators from the *same* 32-bit seed; to give this mechanism a stronger chance, allow **four independent unknown 32-bit native initial accumulators**. This is a conditional source-authoring hypothesis rather than a claimed historical printer design.

## Exact inverse, selected originals, and controls

Use original **selected** K01 signed ink, K02 accepted telemetry prehash, K05 CRC-good selected recorder latches, K06 authorized issue-C four strips and K07 committed transfer-checkpoint prehash. Each of the five exact 16-byte objects independently reduces to the corresponding authentic original slot SHA256 commitment, using the original direct/SHA-truncated reduction as appropriate. Withhold the disputed selected printer ACK2 and K04 commitment entirely from source state inference.

For short public ASCII record labels (length 0..15), MurmurHash3_x86_128 has **no 16-byte message-body block**. Reverse its final modular 32-bit additions, then invert each \`fmix32\` layer using modular inverses of its two odd multipliers and reversal of the two right-shift-XOR cascades. Undo the first modular additions, XOR out each label-length marker and the known per-lane tail mix. This uniquely recovers all **128 initial state bits** for a given complete output, label and 32-bit word layout.

The exact \`forward\` implementation reproduces the independently published x86-128 seed0 test vector for \`abc\`: \`75CDC6D1 A2B006A5 A2B006A5 A2B006A5\`, interpreted as four little-endian numeric words. Eight additional seeded/message positive pairs, plus a two-label true-state recovery control, passed. The reference canonical algorithm is [Austin Appleby's public-domain implementation](https://github.com/aappleby/smhasher/blob/master/src/MurmurHash3.cpp).

For each of five source families, choose four source-attested short label aliases, original/upper/lower casing, four explicit tiny label prefixes (bare, slot-marked, H17-marked and REC8-marked) and eight word/byte-order presentations. The finite results are:

| Original-source inference | Count |
| --- | ---: |
| Complete inverse state assignments | **1,232** |
| Distinct 128-bit native initial states | **616** |
| States consistent with standard repeated 32-bit seed | **0** |
| Native states shared by two different authentic selected-source families | **0** |
| Exact inverse/forward reconstruction on every assignment | **1,232/1,232** |

Because **no actual selected-source pair agrees on one native state**, the proposed shared source generator is unselected by the historical controls.

As a target-facing exploratory check, hash 26 short K04 source-role/job/timestamp label variants under each of the 616 original-source-inferred states, XOR each 16-byte x86-128 output with the fixed original route mask and test the complete original K04 SHA256 commitment. **16,016 full original comparisons, zero matches.** These target checks do not rescue the absent cross-family original-source replay. They are an explicitly bounded finite probe.

## Reproduction and constraints

[Source-pinned Python SFT](../agents/agent13/k04_crossarchive_murmur3_x86_native_sft.py) implements forward/inverse, the published independent test vector, synthetic two-source native-state replay, original five accepted-object controls and complete K04 comparisons using the untouched original \`resources/\` acceptance and fixed mask. Original local source-equivalent run returned:

\`\`\`text
SOURCE_INVERSE {'assignments': 1232, 'distinct_states': 616,
 'cross_family_state_collisions': 0, 'standard_seed_states': 0,
 'positive_controls': 'PASS'}
TARGET_K04 {'full_k04_checks': 16016} message_forms 26
\`\`\`

The repository SFT prints the same model counts with revised field labels; it was committed for portable reproduction. This branch is distinct from the x64 two-lane inversion and prior MD5/SHA/BLAKE2 public-label emitters. Its scope is **short labelled record identities, a common native x86 Murmur state, and the tested byte views**; other message domains, a different per-file secret or different hash family remain possible.

No authentic physical coupon byte or Emily's exact final keeper caption has been obtained. Original K01/K02/K03/K05/K06/K07 each remain PASS, K04/K08 MISSING, REC8 combined INCOMPLETE. The source gap should direct further work toward an *attested* printer authoring format or final keeper wording, rather than assuming that one more unsupported public hash family generates them.
