# N14 cross-slot caption candidate: exact K08/K04 commitment test

**Agent 1 · 21 November 2026 · bounded complete-object construction · no commitment hit**

## Assumption challenged

The K04 and K08 components may not be independent: the K04 mask and K08 desk nonce both map to selector N14 under the previously reported low-bit reducer. That selector is conditional and not a source-authenticated join, but it provides one specific candidate to test without expanding a phrase grammar.

## Deterministic construction

Retained inputs and roles:

1. N14's complete caption text from noticeboard-and-desk-notes.txt:
   “Sunrise photograph: If the horizon has disappeared, the boat has probably brought the rain with it.”
2. K08 desk nonce from recovery-routing.json.
3. K04 masked_component from recovery-routing.json.
4. Unchanged K08 and K04 SHA-256 commitments from acceptance.json.

Apply the exact K08 normalization rule: lowercase; replace characters other than ASCII a-z, digits, and whitespace with spaces; collapse whitespace and trim.

For each of two literal source variants:
- body only: “If the horizon has disappeared, the boat has probably brought the rain with it.”
- full label and body: “Sunrise photograph: If the horizon has disappeared, the boat has probably brought the rain with it.”

Compute:

- K08 candidate = HMAC-SHA256(desk_nonce, normalized phrase)[:16]
- speculative shared-carrier K04 candidate = K08 candidate XOR K04 mask

Compare SHA-256 of each 16-byte candidate with the unchanged K08 and K04 commitments. The second construction is exploratory and is not asserted by the K04 route, which describes opaque printer payload bytes.

## Results

| Variant | K08 HMAC16 candidate | SHA256(HMAC16) | K08 hit |
|---|---|---|---|
| Body only | 1ADE017164A9549BAE2CBFA02FC2A423 | db4ea05259784e82412d669586cb5d6e16d1d2d687c2708c25fa3bfa4d4a7f0f | No |
| Full label and body | 634AFFF25F026AF21AE43F6CD10DE9A7 | 1e0825a7f265005685255af6bda1e73a87e8aef90c875ad252902272fc738e65 | No |

| Variant | HMAC16 XOR K04 mask | SHA256(candidate) | K04 hit |
|---|---|---|---|
| Body only | 9F88C9BA05E9F3620B3E856778D94A3F | 61d905118f39f7637649023ea54158e2f02e9734b227f984d14c5724b234b670 | No |
| Full label and body | E61C37393E42CD0BBFF605AB861607BB | fa58e4869fb83b315517deac43fe460b7a79a0aa4ce159c7bb85bbbe52f63f6c | No |

The unchanged targets are K08 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747 and K04 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

The reproducer includes a pinned synthetic positive control for both HMAC16 and HMAC16-XOR-mask transforms. It passed before the source candidates were tested.

## Falsification and limits

The literal N14 caption, with or without its “Sunrise photograph” label, does not emit either missing component under these deterministic constructions. This rejects only those exact source strings and the specified shared-carrier transform. It does not reject an edited N14 caption, another photo, or a different authorial version operator. Do not broaden this into a phrase grid: the N14 selector is not a source-authenticated instruction to use that caption, and N14 is Gabriel's note rather than an identified final Emily caption.

**Recovery status unchanged:** K01/K02/K03/K05/K06/K07 accepted; K04 and K08 remain missing; combined REC8/1 acceptance remains incomplete.

## Reproducer

agents/agent1/k08_n14_cross_slot_caption_sft.py pins the notes, routing, and acceptance files; applies the exact K08 normalizer; checks both complete-object constructions; and validates the transformation with a fixed synthetic positive control.