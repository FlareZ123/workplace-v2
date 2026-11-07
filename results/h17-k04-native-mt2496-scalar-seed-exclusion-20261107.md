# K04: native MT19937 uint32 seed at p951 / 2496 prior outputs

**Agent 1 | 7 November 2026.** This is a source-only, conditional producer exclusion. It recovers no K04 component and authenticates no historical printer implementation.

## Question

Agent13 asked whether the native C++ std::mt19937(uint32_seed) family had been tested when the generator's first output precedes the first spool row by exactly 2,496 draws under the existing p951 printer packet schedule.

Earlier exclusions covered:
- every uint32 native seed when the first intact printer packet was output zero;
- 15 source-fixed negative output origins before the first packet;
- scalar-initialized 624-word windows that overlap the recoverable p951 state horizon.

Those tests did not cover a seed-initialized register beginning 2,496 outputs before spool row zero. The seed's 624-word initialization register lies outside the tested overlap interval. This report closes that precise gap.

## Original-source construction

Inputs are the unchanged local export:
- resources/evidence/print/spool-reconstruction.log, SHA-256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083;
- resources/evidence/archive-labels.ini, SHA-256 146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad.

The September route section maps ESC-N to PS-261003-0417. Its last ACK/RECOVER attempt is row129, attempt2. That entire row is withheld: its payload field is not extracted, decoded, or used in any equation. The test uses the other 132 intact original packets, four little-endian 32-bit words per packet.

The p951 packet-start schedule is the existing 133-row source model. Under the tested offset, original packet row r, lane j is native output word:

    624 + 2496 + STARTS[r] + j

The first 624 accounts for the standard MT19937 seeded state being twisted before its first output; the additional 2,496 is the proposed number of prior outputs. This is one fixed chronology and serialization hypothesis, not an independently authenticated printer history.

## Exact inversion

A native scalar-seeded MT19937 initializes its register by:

\[
S_0 = \text{seed}
\]

\[
S_i = 1812433253\,(S_{i-1}\oplus(S_{i-1}\gg30))+i
\pmod{2^{32}},\quad 1\le i<624.
\]

The multiplier is odd and therefore invertible modulo \(2^{32}\). Every fully known initial word S_i uniquely determines the seed:

1. \(x=(S_i-i)\,1812433253^{-1}\pmod{2^{32}}\)
2. \(S_{i-1}=x\oplus(x\gg30)\)
3. Repeat down to \(S_0\).

The original 132 intact packets were untempered and inserted into the exact linear MT19937 state recurrence. A ring-buffer implementation retained only 624 symbolic words. The resulting GF(2) source system has rank **15,365 of 19,968** initial-register bits and fixes **711 bits** across 88 initial words.

Four initial words are completely determined by the intact source:

| Initial word | Exact source-fixed value | Unique implied uint32 seed | Other fixed-bit disagreements for that seed |
|---:|---:|---:|---:|
| S[6] | E403BB7D | F848BA70 | 314 / 711 |
| S[7] | 1F7B301F | A5571EA3 | 351 / 711 |
| S[170] | 664F8F37 | E5FD2AAC | 327 / 711 |
| S[605] | 0D8EFC5D | E2E0B436 | 333 / 711 |

Each full word individually determines one and only one seed under the native scalar initializer. The four implied seeds are different. Each candidate also contradicts hundreds of the other source-fixed bits. Consequently, **no single uint32 scalar seed can produce all 132 intact packets under this p951 / 2496-output model**.

The test never reads the K04 route mask, K04 acceptance commitment, K08 nonce, canonical candidate, or verifier.

## Calibration and reproduction

The portable, read-only SFT is agents/agent1/k04_native_mt2496_seed_sft.py.

It includes:
- the original spool and route-label SHA-256 pins;
- a standard-library implementation of native MT19937 scalar initialization, twist, temper, and exact inverse seed recurrence;
- the original selected-row withholding rule;
- six genuine synthetic seeds (0, 1, 5489, 0x12345678, 0xDEADBEEF, 0xFFFFFFFF) generated at the same 2,496-output offset and packet schedule;
- recovery of the exact planted seed from all four fully fixed initial words in all six synthetic controls;
- the standard reference check std::mt19937(5489) first output 3499211612.

Executed locally against the uploaded original export: **6/6 synthetic controls passed**, original source rank and fixed-bit counts matched, and the four original-derived seeds disagreed as shown above.

Run from repository root:

    python agents/agent1/k04_native_mt2496_seed_sft.py

## Scope and consequence

This excludes exactly:
- native MT19937 using the standard single-uint32 scalar initializer;
- the existing p951 packet-start schedule and little-endian four-word serialization;
- the first spool output occurring after exactly 2,496 prior generator outputs.

It does not exclude std::seed_seq, CPython random.Random initialization, NumPy SeedSequence, a different output offset or packet serialization, reseeding, a non-MT printer, or a later physical/copy-stage alteration. The p951 chronology and 2,496-output history remain hypothetical.

**No authentic selected K04 bit was recovered. K08's final author wording remains absent.** The six existing accepted components are unchanged; K04 and K08 remain missing and combined REC8/1 remains INCOMPLETE. The result is a bounded closure of Agent13's specific open native-seed question, not a claim about the actual printer or the missing physical coupon.
