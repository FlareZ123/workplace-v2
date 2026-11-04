# K04: invert full MurmurHash3_x64_128 unknown internal state from original source ACKs

**Agent 39 | 4 Nov 2026.** New **complete-selected-coupon construction** based on a reversible 128-bit metadata hash with unknown initial state. **25,344 original-source-conditioned producer assignments**, **23,924 distinct full K04 16-byte component candidates**, **zero original K04 commitment matches**. A dedicated held-out original 18:25 attempt-2 RECOVER ACK comparator also rejects every tested role-conditioned model. This is a finite tested alternative to the earlier MT19937 and keyed HMAC producer families.

## Mechanism

MurmurHash3_x64_128 is a public noncryptographic 128-bit hash with two 64-bit native state lanes. Unlike SHA256 or HMAC, every transformation in the x64_128 mixing pipeline is bijective when the message bytes are known:

- 64-bit add/subtract and XOR;
- rotate left/right;
- multiplication by odd 64-bit constants, invertible modulo 2^64;
- xorshift-right-33, inverted by one additional xorshift-right-33.

Consequently a **full retained 16-byte ACK payload plus its known metadata message** determines the two initial 64-bit hash state words exactly. With the **same state** used for other job records, the resulting model predicts complete other original packets and a complete selected 18:02 ACK2 coupon. This is a direct candidate construction without guessing any of the unknown selected bytes.

This extension deliberately allows **independent unknown 64-bit initial states**; requiring the standard MurmurHash3 32-bit scalar seed would be a smaller constrained subfamily. It therefore covers an explicit nonstandard state architecture as an aggressive test, although no archive source names MurmurHash3 as the real printer producer.

## Preselected finite source model and exact checks

Input is the original SHA256-pinned 133-row print spool, including only the **132 nonselected** original copied rows for producer inversion; the disputed 18:02 ACK/RECOVER attempt2 payload is never used for fitting. Original full route mask and immutable K04 commitment are used only to check predicted complete components.

There are 24 exact job-metadata message formats, constructed from combinations of job, suffix, UTC timestamp or minute/day, attempt, state, class, destination, JSON or semicolon named fields. Each original raw 16-byte packet is interpreted under eight whole-two-64-bit-lane byte-order/word-swap orientations. The chosen original source row is fully inverted into a hypothetical 128-bit initial-state pair. For each pair the same format predicts the selected attempt2 full 16-byte value. XOR the original route mask and compare the 16-byte component's SHA256 to the original unchanged slot target.

| Quantity | Original result |
| --- | ---: |
| Intact original calibration payloads | 132 |
| Frozen message forms | 24 |
| Reversible 128-bit byte/word orientations | 8 |
| **Complete source-derived producer assignments** | **25,344** |
| **Distinct full original K04 candidates** | **23,924** |
| **Original K04 slot matches** | **0** |
| Standard 32-bit identical-two-lane seed recovered from a retained packet | 0 |
| Adjacent intact-source packet predicted from any of first eight calibration anchors | 0 |

**Role-conditioned original holdout:** The 18:25 PS-261003-0420 packet is the sole nonselected other ATTEMPT=2 STATE=ACK CLASS=RECOVER original. For each of its 24×8 possible inverted unknown initial states, predict the **other eleven** original STATE=ACK CLASS=RECOVER DEST=bench packets by their metadata. Across 24×8×11 = **2,112 full original source replay checks**, **zero** full 16-byte matches. The selected 18:02 target record remains withheld.

## Synthetic algorithm controls

A complete independent MurmurHash3_x64_128 reversible implementation handles all 16-byte blocks, tail words, feed-forward addition and both fmix64 rounds. It reproduces the known standard seed-zero hello vector (raw little-endian bytes 029bbd41b3a7d8cb191dae486a901e5b). For seeded messages of length 0, 5, 47 and 159 bytes, 32-bit scalar seeds and random independent native 64-bit lane pairs are recovered **exactly**. A synthetic complete 133-row printer generated from the same unknown two-64-bit state with the original metadata messages independently reconstructs the true state from an intact original row, reproduces every other synthetic packet including the withheld attempt2, and passes a planted complete mask/XOR/slot-SHA256 acceptance control.

## Decision

Under this finite message/serializer family, neither a standard 32-bit Murmur3 producer nor a fixed unknown full 128-bit Murmur3 internal state explains the selected original historical source, and none of its exact complete K04 predictions passes the original slot commitment. The original role-matched 18:25 comparator offers a substantial source-stage check unlike purely speculative seed inversion.

This negative does **not** exclude a different hash variant, nonstandard different message serialization, producer reseeding per event, truncation from a larger digest, a different initial-state derivation, or an incorrect copied physical coupon. The authentic historical printer mechanism remains unidentified. This investigation confirms **zero authenticated selected K04 bits**, no verbatim K08 final words; six existing individual REC8/1 PASS slots remain unchanged and combined acceptance INCOMPLETE.

Local read-only independent SFT: /mnt/data/h17_murmur128_keyinverse_sft.py. Its code was executed against the original attached 46-member export with the stated synthetic controls; no official evidence or acceptance file changed.
