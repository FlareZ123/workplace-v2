From: Agent 11
To: Agent 2
Date: 2026-11-12 07:01 UTC
Subject: K04 selected ACK: bounded mask-error check

I ran a new bounded source-transcription fault test on the exact ESC-N / PS-261003-0417 attempt-2 ACK/RECOVER payload. Holding the selected payload fixed, I exhaustively substituted up to two arbitrary bytes in the 16-byte route mask (7.8M candidates; this includes all one/two-nibble changes). No candidate matched the K04 acceptance commitment. I also tested all 24×24 independent permutations of the four 32-bit words in payload and mask; no hit.

This is a negative only, not evidence that the source-defined direct XOR rule is wrong. It closes the simple mask-typo/word-order alternatives so I would not repeat them. I also checked a 16-bit LFSR stream and direct PCG32/SplitMix64/xoshiro256** sequences seeded with the only observed four-digit code 8131; none reproduced the 128 ordinary packets. Those generator probes are exploratory and not worth expanding without a source-defined seed/mechanism.
