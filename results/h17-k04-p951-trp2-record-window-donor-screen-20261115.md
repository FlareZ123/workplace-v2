# K04: p951 TRP2 record-aligned 16-byte donor-window screen

**Agent 6 · 15 November 2026 · bounded source-record donor test; no K04 component recovered.**

## Question

The conditional p951 MT19937 model leaves two four-word state blocks unobserved before the selected K04 output:

- A: native stages 328–331
- B: native stages 724–727
- target: native stages 951–954

The p951 model is not source-attested and has known source-model caveats. This test asks one narrow question: do the original CRC-valid TRP2 recorder records contain either missing four-word block as a complete 16-byte record-aligned window, when the same field offset is used for both donor blocks?

This extends the existing field-specific recorder donor inventory. It does not assert that printer and recorder historically shared an MT state.

## Frozen sources and construction

The test uses the original 46-file export and the existing exact p951 symbolic basis:

- spool reconstruction SHA-256: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`
- TRP2 recorder SHA-256: \`5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba\`
- recovery-routing SHA-256: \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`
- acceptance SHA-256: \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`

The p951 basis is built from the 132 intact original printer packets; selected row 129 is excluded. The original printer-only source rank is 15,365. The exact selected route, mask, and full K04 SHA-256 commitment remain unchanged.

The TRP2 file contains 88 records of 24 bytes. The test retains 84 CRC-valid records whose node is 49 or 50. For each retained record, it extracts the 16-byte windows beginning at offsets 0, 4, and 8. These are the three four-byte-aligned windows wholly inside the 24-byte record. No arbitrary byte offsets or cross-record windows are introduced.

For each window, the four 32-bit words are interpreted in:
1. little-endian order, raw native-state words;
2. little-endian order, inverse-tempered output words;
3. big-endian order, raw native-state words;
4. big-endian order, inverse-tempered output words.

Exact duplicate values already present in Agent50's 40-block p951 cross-stream inventory or among the 132 intact printer payloads are excluded before constructing donor variants. There were no such overlaps.

For each fixed record offset, all ordered donor pairs are tested with A at stages 328–331 and B at stages 724–727. Each pair must be consistent with every original printer source equation and determine all 128 target bits. The resulting complete 16-byte output is tempered, serialized, XORed with the official K04 mask, and checked against the unchanged full SHA-256 commitment.

## Results

| Record-window offset | Unique windows | Variants | Ordered A/B pairs | Complete pairs | K04 hits |
|---:|---:|---:|---:|---:|---:|
| 0 | 84 | 336 | 112,896 | 112,896 | **0** |
| 4 | 84 | 336 | 112,896 | 112,896 | **0** |
| 8 | 84 | 336 | 112,896 | 112,896 | **0** |
| **Total** | **252 window instances** | **1,008** | **338,688** | **338,688** | **0** |

A deterministic synthetic positive control constructs a complete state satisfying the original printer equations, exposes its exact native blocks at A and B, and requires the same reconstruction path to recover the planted full target. **The synthetic positive passes.**

The exact reproducer is [\`agents/agent6/k04_p951_trp2_record_window_donor_sft.py\`](../agents/agent6/k04_p951_trp2_record_window_donor_sft.py). Run from the repository root:

\`\`\`sh
python agents/agent6/k04_p951_trp2_record_window_donor_sft.py
\`\`\`

## Interpretation and limits

No same-offset, record-aligned TRP2 16-byte window pair supplies the two p951 gap blocks under the tested raw/untemper and endian interpretations. This is a complete negative for the stated finite donor family, not evidence that the p951 model is historically correct or incorrect.

The test does **not** cover cross-offset A/B pairs, arbitrary byte offsets, arbitrary word permutations, other binary-source windows, or unpreserved recorder/device buffers. Cross-offset pairs were deliberately not folded into this result: no source record indicates that the same four-word field layout should change between the two hypothesized gap positions.

No original coupon bit was recovered. The selected ACK payload remains unauthenticated as physical media; K04 and K08 remain missing, and combined REC8/1 acceptance remains incomplete. No original evidence, route, acceptance commitment, candidate, or verifier was modified.
