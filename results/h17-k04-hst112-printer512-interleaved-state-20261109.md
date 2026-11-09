# K04: original HST-4/print interleaved 624-word state gives no complete coupon

**Agent 23, 9 November 2026. Tested directly against unchanged original K04 commitment. K04 remains unresolved.**

## Recovery mechanism

The original HST-4 freeze contains 112 distinct three-decimal PV readings, sequence numbers 100..211. The printer archive contains 128 ordinary first-attempt ACK 16-byte packets, PS-0300..0427. The arithmetic job index +200 maps PV seq100..211 to exactly the first 112 printer jobs. These provide **112 historian readings + 128 × four printer words = 624 word positions**, the MT19937 state length.

Agent8's [previous 112+512 test](h17-k04-112plus512-mt624-export-assembly-20261109.md) concatenated the two entire streams. The present **different source assembly** inserts one PV-derived 32-bit word at a fixed position 0,1,2,3 or4 in each of the first 112 corresponding fourword printer packet batches; the last 16 printer packets remain fourword-only. The output is exactly 624 words for every complete model. The disputed selected K04 row129 is not read as model input. HST-4 readings are explicit engineering PV values and were recorded much later than the printer jobs. This interleaving is **a speculative export-serialization hypothesis**, not an authenticated historic shared generator.

## Whole-object test

Use all three original PV orders (seq, raw file, acquisition timestamp), each of three wholeword codecs (IEEE754 float32 bit pattern, rounded PV×1000 integer, rounded PV integer), two printer byte-endian choices, two printer word orders and five within-batch PV insertion positions: **3×3×2×2×5 = 180 complete MT624 initial-state models**.

For every model, untemper 624 words, compute 1024 subsequent native MT outputs via the exact 624/397/227 recurrence and retemper. Check every complete fourword window (1021 per model), both wholeword orders and both byte orientations as a physical 16-byte coupon. XOR the original route mask and compare the **entire K04 SHA256 commitment**. Separately, check every future window in the model's original printer-byte view against each of four completely withheld late source packets: original spool rows 128,130,131,132 (both REQUESTED retries and the two late intact ACKs). The selected row129 is excluded from all 624-word states and from every source-control target.

**Original preserved-export result:**

| Test | Observed |
|---|---:|
| Distinct source assembly models | 180 |
| Complete physical-coupon commitment checks | **735,120** |
| Accepted K04 candidates | **0** |
| Complete matched withheld late original printer packets, any tested future position | **0** |
| Synthetic true-MT interleaved 624-state continuation | PASS, 20/20 full words |
| Planted independent 16-byte future coupon, same XOR/SHA256 path | PASS, unique hit |

The genuine positive is an independently seeded Python MT19937 stream split into 112 fiveword and 16 fourword source batches, with each fifth source PV slot round-tripped through IEEE754 float32. Reassembling those source blocks predicts all 20 genuinely withheld future output words. A complete synthetic coupon at offset9 is then recovered by the identical target reduction. The code's inverse-temper bug was caught by that true-producer control and corrected before the original 735,120-test run.

Original SHA256 pins: printer `7d71d8be...f3841b6083`, historian `3787dbd6...498026e057639f`, route `f8fcbca7...54a4764d8a5`, acceptance `68173924...0c137f`. The code asserts complete hashes. No historical source, route, verifier, acceptance, or canonical candidate changed.

**Reproducer:** [source-pinned single-file test](../agents/agent23/k04_hst624_interleaved_state_sft.py), standard-library Python, run from an ordinary checkout. It was executed locally on a repo-shaped extraction of the unmodified original ZIP; remote code was read back after the commit.

## Consequence

The exact 624-word count does **not** rescue the selected printed K04 coupon under this explicitly enumerated interleaved global-MT producer. In particular, no model reproduces even one later intact printer control; the original source evidence disfavors these layouts independently of the SHA256 target. This is narrower than excluding other historical export serialization, a differently encoded historian field, or the separate p951 sparse-gap generator model. No K04 bit is authenticated, K08 remains unquoted, and original REC8 still has six PASS and two MISSING, combined INCOMPLETE.

Target-directed next step must change the source–publisher relationship or locate actual independently indexed words in the already-identified two native gaps; additional arbitrary MT624 permutations are not supported by this null holdout.