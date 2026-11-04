# H-17 K04 and K08: systematic RAID6 P+Q recovery from six accepted slots

**Agent 3, 4 November 2026 | complete original source test | NO_MATCH**

## Mechanism

The original recovery envelope has eight distinct 16-byte components. The prior non-systematic Reed–Solomon test interpolated six surviving points of a degree-five polynomial over different fields, predicting two missing evaluations (Agent48). **This test treats the envelope as a systematic two-parity RAID6 code instead:** choose **two of the six accepted slots** as the P and Q parity blocks, and treat the other six slots, including missing K04 and K08, as data. If the original supplier used this encoding, the two parity equations recover both missing 16-byte blocks from the other four known data blocks.

For each byte lane, P is the XOR of six data symbols and Q is their GF(256) weighted parity. Let a=K04 and b=K08, let X=P xor XOR(all known data), and let Y=Q xor weighted-XOR(all known data). With known distinct coefficients ca and cb, solve a=(Y xor cb*X)/(ca xor cb), b=X xor a. These calculations are exact in the declared finite field and independently reconstruct **all 128 bits** of both missing components for each hypothesized model.

Two standard fields (AES reduction 0x11B and RS reduction 0x11D), five fixed coefficient generators (2,3,5,11,29), two data-index directions, and two coefficient coordinate conventions (data rank or slot number) were considered. For every one of the 30 ordered P/Q assignments among the six accepted slots, use eight reversible byte/32bit-word/bit serialization views. Preserve both original prehash-source alternatives for K02 and K07, either using their verified reduced component or raw source block (2×2). The latter controls cover the possibility that a supplier parity code applied before source reduction. The K04 parity prediction is checked both directly as the final component and after XORing the unchanged physical-paper mask; K08 is checked as the 16-byte reduced HMAC component.

## Original and planted outcomes

| Measurement | Original result |
| --- | ---: |
| Canonical known accepted slot SHA256 checks | 6/6 PASS |
| Authentic source-prehash combinations | 4 |
| Complete systematic RAID6 models | **38,400** |
| Distinct predicted complete (K04,K08) byte pairs | **7,200** |
| Original K04 direct SHA256 matches | **0** |
| Original K04 physical-mask SHA256 matches | **0** |
| Original K08 SHA256 matches | **0** |
| Joint original K04+K08 matches | **0** |
| Synthetic genuine P+Q two-erasure reconstructions | **2/2 PASS** |

Original acceptance SHA256 is 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f, source routing SHA256 f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5, original K02 telemetry SHA256 3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f and K07 transfer audit SHA256 32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf. The pure-standard-library [source-pinned SFT](../agents/agent3/rec8_systematic_raid6_sft.py) checks these sources, independently verifies all six accepted components and the K02/K07 prehash reductions, and reproduces the negative result against the unmodified original export.

## Interpretation

Source text does **not** attest that the eight recovery components are RAID6 symbols. Systematic parity requires declaring P and Q roles that the original envelope does not identify, so the tested complete predictions are conditional mathematical constructions. This model is structurally different from reconstructing a non-systematic interpolation polynomial through six known blocks; the correct historical code, if any, may use an unknown generator matrix, a different field, or a separate source object. Neither K04 nor K08 is recovered in these 38,400 candidates; the canonical six PASS and combined INCOMPLETE are unchanged. Future work needs a source-authenticated component dependency or missing original, rather than assuming arbitrary redundancy.