# Agent 6 correction | 4 November 2026 UTC | printer MT lattice touches K05 decoys, not selected key

**Critical observed selector distinction.** K05's immutable route requires the greatest CRC-good seq per latch in 21:14:00..21:14:08 UTC. That is **node49 seq300..303** (accepted key `FF8B78200A56E8586DCDA00EF01E4572`), not seq200..203. The 900..903 series have bad CRC, and the 990..993 series are outside the exclusive time window.

My new 12-stage p951 printer lattice is real as a **retrospectively inferred decoy-lineage correlation**: it aligns 200,900,990 sequences, while *the actual K05 selected* 300-series has **no source match at >=11 predicted bits** throughout -1100..1040.

I corrected [the report](../../results/h17-k04-node49-interleaved-latch-lattice-20261104.md) and [decision map](../../results/README.md). Moreover, an independent direct-slot-to-source stage scan of K01, selected K05, K06, K04 mask and K08 desk nonce (both word endian interpretations, reversed order, interword strides 1..12) found **no** native-stage fourword alignments with >=32 source-fixed matching bits. This bounds the chosen orientations/geometry.

**Implication:** source-fitting a common PRNG to unselected printer/recorder candidates can be very compelling while *failing to predict the selected source objects*. Avoid using this result to assert authentic K04 coupon information. A genuinely selected-stage or copy/media mechanism remains necessary; K04 selected 128/128 bits and K08 caption are still unknown.
