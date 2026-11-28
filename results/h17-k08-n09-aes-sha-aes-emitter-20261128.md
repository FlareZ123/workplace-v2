# K08: N09 body uniquely emits AES / SHA / AES under the frozen LOW-IF-EVEN note-head transform

**Agent 45 | 28 November 2026 | target-blind source program discovery; no new accepted component**

## Question

The source-local K08 chain independently selects N09 and emits the token `AES`. Does N09 itself contain a deterministic cryptographic/operator program under operations already established before this test?

## Frozen transform

Use the SHA-pinned 24-note source, normalized post-label body words, and only the existing operations:

1. For each three-word window, compute each word's ASCII **LOW BIT** value by packing character least-significant bits first-character-as-LSB.
2. Apply **LOW IF EVEN** to each value: an even selector moves one row lower; an odd selector stays.
3. If all three selectors are in the N01..N24 namespace, take the first normalized body character of the three selected notes.

No K08 nonce, target, candidate, printer record, or PDF is read.

## Result

In N09, the overlapping windows beginning at one-based body positions **2, 4, and 6** emit:

`AES / SHA / AES`

Those windows cover the contiguous N09 body region from word 2 through the source's first `cup` token.

The whole-corpus control is unusually restrictive:

- **125** three-word windows across N01..N24 have all three transformed selectors inside N01..N24.
- Among those 125 windows, the **only** outputs equal to either `AES` or `SHA` are exactly N09 starts 2, 4, and 6.
- Across every possible same-note stride-two triple-window sequence, **N09 start 2 is the only `AES, SHA, AES` sequence**.

This is independent of the K08 commitment and is not selected by target readability after the fact.

## Relation to the AES/SEA loop

The result composes with the separately reproduced loop in `h17-k08-aes-sea-closed-loop-20261128.md`:

- source-emitted `AES` -> A1Z26 note counts -> `LOW`;
- LOW BIT(`AES`) -> N07 reversal instruction;
- reverse `AES -> SEA`;
- literal `sea` occurs only in N01/N20 -> `AT`;
- AT is independently emitted by TAILBIT/LEN and feeds the finite N20 overlap decoder.

Thus N09 does not merely contain prose semantically related to AES: under the existing operator vocabulary it contains a unique explicit `AES/SHA/AES` program-like sequence.

## Bounded interpretation checks

Two narrow interpretations were tested outside the target-blind census and were negative:

- 48 source-holdout AES/SHA/AES variants over the intact PS-0417 REQUESTED1/REQUESTED3 flanks using the compact 16-byte source token as AES key: zero exact whole-flank predictions.
- 96 route-native K08 component constructions using only the compact 16-byte token and documented 16-byte desk nonce as AES keys/blocks, AES encrypt/decrypt, SHA-256 first/last half, and a second AES stage: zero original K08 commitment hits.

These negatives close only those direct block-pipeline readings. They do not weaken the source-only `AES/SHA/AES` emission result.

## Consequence

This is a materially narrower program cue than the earlier standalone AES interpretation. Future work should treat `AES/SHA/AES` as one exact source-derived operator sequence and demand a source-fixed operand/serialization before further cryptographic expansion. It does not yet emit Emily's final N23 wording.

## Reproducer

`agents/agent45/k08_n09_aes_sha_aes_sft.py` pins the crew source, enumerates all eligible body triplets, proves the three unique AES/SHA windows and the unique stride-two sequence, and reads no target data.
