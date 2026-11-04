# K04 original K02/K05 bridge: a shared hidden 32-bit recorder whitening mask

**Agent 9 | 4 November 2026 UTC. Conditional source and complete original K04 test.** This explores a distinct **shared XOR whitening stage for the four CRC-valid node49 K05 recorder-latch words**. The original source-compatible cases produce **512 complete 16-byte K04 components**, with **zero original K04 SHA256 matches**. K04 remains missing, K08 exact final words missing and REC8/1 combined INCOMPLETE.

## Distinct mechanism from existing K02/K05 stage tests

Agent14's source-first [stride-227 K02/K05 latch model](h17-k04-k02-k05-stride227-four-latch-3bit-source-exclusion-20261104.md) treated each selected recorder word as a direct native or tempered observation of the hypothetical p951 printer MT19937 stream, in four byte-order formats. Those source models were screened and 228,352 complete K04 candidates rejected. **This new test inserts one shared, previously unknown 32-bit XOR word between the underlying stream and all four node49 latch controls.** This permits a genuine record-wide whitening/register-mask protocol that the direct-donor models do not permit.

Let original selected K05 opaque 32-bit source value at latch i be \`O_i\`, a hypothesized MT native value be \`W_{p_i}\`, and one unknown common four-byte mask be \`M\`. Each latch contributes an equation

\`W_{p_i} XOR M = O_i\`

for i=0,1,2,3 under one of four exact native/untempered, byte-endian interpretations. The hidden \`M\` is represented by **32 additional shared GF(2) variables**, so it must be consistent across all four observations. Independent mask variables for every latch would make the model largely vacuous; this shared-mask restriction is the tested physical-stage hypothesis. For a tempered serialization, applying \`untemper\` to all observed words is valid because MT tempering and its inverse are GF(2)-linear; a common tempered XOR becomes a common unknown native XOR.

This model is unverified: neither the original recorder format note nor the printer source attests a shared MT engine, a K05 whitening mask, the p951 chronology, the 227-index spacing or the correct target coupon stage. Source consistency is an internal discriminator inside that model.

## Frozen source and full test

Original printer spool SHA256: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. Original selected recorder \`K05=FF8B78200A56E8586DCDA00EF01E4572\` and telemetry \`K02=E1A5E474BAD7E853A2E8C71D3317D507\` are checked against their original SHA256 acceptance commitments. Selected copied printer ACK row129 is excluded from the symbolic source. No K04 target hash is used for stage or writer-format selection.

Start from original p951 intact printer rank **15,365**. For each of two previously studied K02 donor epochs (1178 and 1405), try the existing **16 K02 32-bit word presentations**. For each, test exactly the previously source-ranked five K05 start positions \`1120,1347,1516,1743,2139\`, with strict 227-word latch stride and the four historical raw/untempered endian presentations. The 640 assignments are decided by exact Gaussian elimination over the augmented state+mask space, using original observed source values only.

| Full source-plus-shared-mask assignment | Original count |
| --- | ---: |
| Defined K02 × stage × K05 presentation assignments | **640** |
| Original-source **consistent** models | **32** |
| Compatible K05 stage and view | **2139**, untempered little-endian |
| K02 presentations compatible at that stage | **All 16**, at both donor epochs |
| Conditional remaining selected K04 coupon degrees of freedom | **4 bits** each |
| Complete K04 candidates per surviving assignment | **16** |
| All complete original K04 SHA256 comparisons | **512** |
| Distinct complete K04 components | **512** |
| Authentic original K04 commitment matches | **0** |

The augmented source rank in each compatible case is **15,618**, counting the 32 added mask coordinates. The rank and quotient are source-model algebra, not evidence of historically recovered coupon bits.

## Independent controls and reproducibility

The [source-pinned standalone SFT](../agents/agent9/k04_common_mask_full_sft.py) checks original recorder/telemetry file SHA256, original K02 and K05 acceptance values, exact selected recorder latch CRCs, the known route mask, and original K04 full commitment. For each of the 32 compatible models, it constructs a particular affine source-state solution, generates the corresponding complete 16-byte coupon, and checks that the exhaustive **16-candidate** enumerator recovers the planted coupon **exactly once** (32/32 positive controls).

A second producer-positive creates an **independently seeded 19,968-bit MT state**, serializes all 132 source-safe original-position printer packets, creates synthetic K02 donor words, and creates four synthetic K05 recorder words by independently choosing a common 32-bit whitening mask and applying native MT tempering. It hides the selected 16-byte coupon, reconstructs the original-style source and masked-latch equations, and asserts that its complete 16-candidate coset contains **the exact genuinely generated missing coupon exactly once**. The true synthetic mask is never selected from the original K04 target.

Actual read-only local run: \`assignments=640\`, \`source_compatible=32\`, \`complete_checks=512\`, \`planted_controls=32\`, \`distinct_components=512\`, \`original_hits=0\`; genuine full-source synthetic positive PASS. Original source and official verifier unchanged.

## Scope and further crack

The shared-mask stage survives exact original source constraints in a sharply limited stage and serializer geometry, but its complete selected coupon candidates fail the historical commitment. This rejects **that 640-case proposed coupling** as an original K04 reconstruction. It does not exclude a different shared/sequence-varying whitening function, another selected event epoch, nonlinear recorder serialization, a different generator, or a physical coupon independent of the reconstructed spool.

Importantly, this is a direct complete-key attempt using historical **cross-stream** data rather than a new local edit to the suspicious copied ACK. It yields **zero authenticated original K04 bits**. The next promising discriminator is an independently attested recorder-to-printer writer relation, or a precisely source-selected alternative mask/capture stage that predicts intact controls before the target.
