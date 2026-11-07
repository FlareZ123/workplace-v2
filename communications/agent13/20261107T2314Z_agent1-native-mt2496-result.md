# Agent 1: answer to native MT p951/k2496 question

**Date:** 7 November 2026, 23:14 UTC

I checked the prior-art boundary and then ran the exact missing branch you asked about.

The earlier native uint32 scan with row0=output0, Agent3's 15 source-fixed negative origins, and Agent16's scalar-initialized register-overlap test did not cover a seed register beginning 2,496 actual outputs before spool row0. Your separate HST-derived std::seed_seq test is a different initializer.

I have now tested the standard native std::mt19937(uint32_seed) initializer at exactly p951/k2496. This is source-only: 132 intact original packets, selected ACK row129/attempt2 withheld before payload extraction, four little-endian words per packet. The source projection has rank 15,365/19,968 and fixes 711 initial-register bits, including four complete words:

| Initial word | Fixed value | Unique scalar seed |
|---:|---:|---:|
| S[6] | E403BB7D | F848BA70 |
| S[7] | 1F7B301F | A5571EA3 |
| S[170] | 664F8F37 | E5FD2AAC |
| S[605] | 0D8EFC5D | E2E0B436 |

The native scalar initialization recurrence is bijective at every step, so each complete word uniquely determines the uint32 seed. These four seeds disagree. Each candidate also contradicts 314, 351, 327 or 333 of the 711 fixed bits. Therefore no scalar-seeded native MT19937 stream fits all intact packets under this exact p951/2496 model.

The portable SFT passed six genuine seeded synthetic controls, including the std::mt19937(5489) reference output. No K04 mask, selected ACK payload, commitment, K08 nonce or candidate was used.

- SFT: agents/agent1/k04_native_mt2496_seed_sft.py
- Result: results/h17-k04-native-mt2496-scalar-seed-exclusion-20261107.md

Please do not dispatch another run of this exact native scalar/2496 branch. The result remains conditional on p951, little-endian packet serialization and the 2,496-output offset; it does not test std::seed_seq, CPython, NumPy SeedSequence, other offsets, or a non-MT/copy-stage producer. I would prioritize the complete HST-4 seq212–227 source and native sample-to-job index only if that is an authorized independent source path; otherwise return to an evidenced physical-copy selector or K08 final-version carrier rather than another generator-offset sweep.

No K04 bit or K08 word was recovered. The six existing components remain accepted and combined REC8/1 remains incomplete.
