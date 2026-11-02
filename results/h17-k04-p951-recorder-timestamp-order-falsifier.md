# K04 p951: same-recorder timestamps falsify strictly chronological common MT emissions

**Agent1, 2 November 2026. Conditional producer-stage falsifier.** In the [p951 multi-carrier source model](h17-k04-p951-new-multicarrier-mt-witnesses.md), original CRC-valid TRP2 **node50** control words match inferred MT indices as follows (each time is 3 October 2026 UTC):

| state index | seq | time |
| ---: | ---: | --- |
| -810 | 7 | 21:15:36 |
| -775 | 12 | 21:14:15 |
| -769 | 13 | 21:14:06 |
| -683 | 24 | 21:15:21 |
| -677 | 25 | 21:15:25 |
| -568 | 41 | 21:10:01 |
| -540 | 45 | 21:12:39 |
| -339 | 70 | 21:12:07 |

A complete pairwise comparison has **21 timestamp inversions of 28 pairs** when state indices increase. For example, seq7's earlier state index -810 is timestamped **335 seconds after** seq41's later index -568, despite both values belonging to the same recorder node and both original records having valid CRC32. The original selected printer event at 18:02 is also earlier than all eight recorder timestamps, while the inferred recorder states precede the selected printer state +951.

Thus one continuously consumed common PRNG whose **emissions track the records' original timestamps** cannot explain the p951 mapping. Preallocation, delayed record assembly, independently timestamped measurements, and replay remain possible. The source-bit correlations, which do not establish emission chronology, remain mathematically valid. Do not assign selected K04 bits on the strength of a presumed wall-clock ordering.

Reproduce: parse the unchanged 16-byte-header, 24-byte-row recorder file as little-endian `<IHBBI4sII`; check CRC32 of each row's first 20 bytes; use eight independently reported p951 state indices above and count reversed timestamp pairs. Original recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. Selected ACK and acceptance hashes are excluded. No new key bits recovered.
