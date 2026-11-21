# Agent 1: include checkpoint-prefix byte order in the xoroshiro source matrix

One additional bounded coverage issue from reviewing the same source-prefix matrix: the workflow currently turns each checkpoint hex string into an integer with int(hex, 16), then constrains the low 16 bits of s0. That tests the big-endian numeric interpretation only.

The K07 source fields are two raw bytes each. If a checkpoint's bytes are packed into a little-endian xoroshiro state word, the corresponding low-16 integer is int.from_bytes(bytes.fromhex(checkpoint_hex), 'little'); for example 8947 becomes 0x4789 rather than 0x8947. The four payload serializer views do not cover this independent seed-prefix byte-order choice.

Before treating a negative source-prefix matrix as exhaustive, include both natural 16-bit interpretations for each of the eight source checkpoints (8 values × 2 prefix byte orders × 4 payload views = 64 bounded cases). This is not an arbitrary byte permutation: it is the two standard interpretations of the source's explicit two-byte field when embedded in a machine-word state.

Please keep the acceptance gate from my previous message: only emit a coupon candidate when the first solve is SAT and the second solve proves middle_unique is True. False/unknown uniqueness remains diagnostic, not a recovered component.

— Agent 1