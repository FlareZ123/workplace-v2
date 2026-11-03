# K04: classic .NET Framework subtractive RNG, continuous and per-job exhaustive-seed exclusions

**Agent 19 | 3 November 2026 | Original K04 commitment untouched, no new selected-coupon bits.**

## Distinct generation-stage hypothesis

The surviving print-spool export resembles the output of an office software stack. This experiment tests the older **.NET Framework** \`System.Random\` subtractive 55-cell generator as a complete 16-byte packet producer. This is a producer-architecture hypothesis, with no source evidence that the printer uses .NET.

The implementation follows Microsoft's [original reference source](https://github.com/microsoft/referencesource/blob/main/mscorlib/system/random.cs), including the 55-cell initialization and \`NextBytes\` using \`InternalSample() % 256\`. [Modern .NET can use different Random implementations](https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-random); the result below does not cover all .NET versions.

The original read-only spool is \`resources/evidence/print/spool-reconstruction.log\`, SHA-256 \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. Its **128 intact ordinary job packets PS-261003-0300..0427**, 16 bytes each, are the only original data used. The selected disputed ESC-N recovery ACK2 is **excluded** from model fitting and checks.

## Model A: continuous generator with per-packet hidden draws

For raw sampled integers \`x_t\`, after the first 55 samples, the legacy generator satisfies

\`\`\`
x[t] = (x[t-55] - x[t-34]) modulo 2147483647
\`\`\`

Because \`2^31-1 ≡ 255 (mod 256)\`, each emitted byte \`b_t=x_t mod 256\` must obey

\`\`\`
(b[t] - b[t-55] + b[t-34]) modulo 256 ∈ {0,255}
\`\`\`

where all three bytes are observed.

We tested every combination of **eight invertible 4×4 byte packet layouts** (within-word reversal, word-order reversal, and 4×4 transpose) and **17 fixed inter-packet hidden-draw counts** (0..16). This makes **136** distinct original-source checks. The best model, original byte order with four hidden draws per packet, satisfies only **20/1376** required congruences; the next-best satisfies **23/1625**. **Zero models satisfy their source-required relations.** All eight geometries pass exact seeded synthetic 128-packet controls, including skips and inversions.

This rules out the exact continuous \`NextBytes\` families under the specified fixed gaps, mappings and ordinary-record ordering. It does not rule out variable gaps, changes in producer/copy stage, independent reseeds, or modern generators.

## Model B: an independent newly seeded generator for each packet

A second hypothesis drops all cross-packet chronology. Suppose job0300 is the **first 16 \`NextBytes\` outputs** of an independently constructed legacy \`System.Random(int)\` object. Every signed 32-bit constructor seed maps to a magnitude in 0..2^31 (with \`Int32.MinValue\` equivalent to magnitude zero for the reference constructor); therefore test every unique seeded 31-bit state.

For the first 16 draws before any possible state-array rollover, the reference-source recurrence implies the exact affine seed relationship

\`\`\`
x_i(seed) = (x_i(0) + (x_i(1)-x_i(0))*seed) mod (2^31-1)
\`\`\`

with invertible slope at output zero. Enumerate each raw first integer congruent to the observed packet's first byte modulo 256; derive its *unique* seed using the modular inverse of the first-output slope. This covers **2^31 candidate seed magnitudes per geometry** while evaluating only **2^23 first-byte-compatible seeds**, then filter on later observed bytes. With eight packings, the exact inversion covers **8 × 2^31 = 17,179,869,184 seed/geometry interpretations**, efficiently reduced to 67,108,864 first-byte-compatible values.

**Original job0300 result:** first-byte-compatible survivors = 8,388,608 in each geometry. After three bytes, 127..132 survivors per geometry remain. Some layouts have 1 or 2 four-byte survivors. After **five bytes, all eight modes have zero survivors**, so no seed reproduces the first 16-byte packet. The independent seeded packet model is therefore excluded for the first original packet under all eight geometries.

The complete seed inversion independently recovers a genuinely seeded, withheld **20261103** from a synthetic transposed/reversed packet. The exact \`Random(0).Next()\` and \`Random(42).Next()\` public reference values and seed affine equations are separately asserted.

## Reproduction and implications

Run the standalone Python 3 standard-library test [\`agents/agent19/k04_dotnet_framework_subtractive_sft.py\`](../agents/agent19/k04_dotnet_framework_subtractive_sft.py) from the repository. The script SHA-pins the official printer source, requires all 128 ordinary packets, checks the continuous and reset models, prints structured results and exits nonzero if a tested original model unexpectedly passes or a planted seeded control fails. It reads no acceptance commitment.

This advances the original-source producer question by testing an architecture independent of the conditional CPython/MT19937 shared-state investigations. It does **not** identify the actual printer generator or connect a physical selected copy to an authenticated producer value. **K04 still has 0 independently authenticated selected bits. K08 terminal wording is unquoted.** The original six individual slot passes and combined incomplete result remain unchanged.

A genuinely different follow-up would constrain a **per-record warmup or a nonlegacy high-byte \`Random.Next(256)\`** producer by an actual writer metadata rule. A broad unguided gap/seed search would add little; the packet-lag and direct seed tests have already decisively excluded the two specified models.


## Independent high-byte API extension: \`Random.Next(256)\` (same day)

A legacy .NET program could obtain each packet byte by calling \`Random.Next(256)\` rather than \`NextBytes\`. The former scales each full 31-bit raw output to the range 0..255; it is not the low-byte mapping of Model B. The seed-affine inverse above remains exact. For each observed first byte \`b\`, enumerate the raw interval

\`\`\`
ceil(b*(2^31-1)/256) <= x0 < ceil((b+1)*(2^31-1)/256)
\`\`\`

and invert \`x0\` for each of the exactly **8,388,608** possible original first outputs. Repeat for all **eight** packet geometries, checking every subsequent full-scale byte. This covers another **8 × 2^31 signed-seed-magnitude interpretations** of original job0300, with **zero complete matches**. The first original packet has 125..132 survivors after three bytes; three geometries leave one candidate after four, another leaves one, and all eight have **zero survivors by byte five**. An independently generated full \`Random(20261103)\` sixteen-call \`Next(256)\` packet is correctly inverted to its withheld seed, validating the full candidate-to-coupon path.

Portable reproducible C++17 file: [\`agents/agent19/k04_dotnet_next256_highbyte_sft.cpp\`](../agents/agent19/k04_dotnet_next256_highbyte_sft.cpp). It pins the first original packet's literal source row, runs the complete seed inverse for eight geometries and requires the planted seeded positive. The original source and target commitments remain unchanged.

This **separately excludes exact first-packet legacy \`Random.Next(256)\` generation without warmup**, even if every ordinary printer record is independently reseeded. It leaves a nonzero warmup, other output API, copier or generator entirely open. Original K04 still has no authenticated selected bits.
