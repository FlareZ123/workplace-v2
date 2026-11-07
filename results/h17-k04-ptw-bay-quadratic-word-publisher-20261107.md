# K04: quadratic PTW/PS same-suffix word-publisher falsifier

**Agent 44 | 7 November 2026.** A new, bounded source-paired producer experiment. It recovers no K04 bytes and does not authenticate a common issuer.

## Question

The original export contains 27 one-to-one numeric-suffix coincidences: PTW-390 through PTW-416 each has one 32-bit seal serial, and the printer spool has one ACK1 packet PS-261003-0390 through PS-261003-0416. Earlier work tested per-bay affine word publishers and digest-plus-pad constructions. This experiment asks whether a nonlinear quadratic publisher could map the original serial and its permit number to one 32-bit word of the same-suffix printer packet.

The equal-suffix join is a candidate relationship, not an explicit source cross-reference. The test therefore requires genuine held-out printer words before any target use.

## Frozen source and method

Original source SHA256 pins:

- `maintenance/seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

For each bay independently, the first three permits in ascending numeric order train the quadratic map. The remaining original pairs are held out: A has 5, B has 1, C has 6, and D has 3. Four 32-bit words are considered at each printer packet position.

Two field models were tested:

1. **GF(256), bytewise:** independent degree-two maps for each byte lane, AES polynomial (x^8+x^4+x^3+x+1) (0x11B). The serial byte order and each output word's byte order are independently tested in both orientations.
2. **GF(2^32), whole-word:** a degree-two polynomial maps the full 32-bit serial to one full 32-bit packet word, using irreducible polynomial (x^{32}+x^7+x^3+x^2+1) (0x10000008D). Input modes are the serial alone, serial XOR permit number, serial plus permit number modulo (2^{32}), and serial minus permit number modulo (2^{32}). Input and output word byte orders are both tested.

All model fitting excludes the selected PS-0417 ACK2 packet, its K04 mask, and both K04/K08 commitments. The program also includes independently planted quadratic source histories to check the interpolation and prediction implementation.

## Results

| Model | Complete models | Original held-out 32-bit predictions | Exact predictions |
|---|---:|---:|---:|
| GF(256) bytewise quadratic | 64 | 240 | **0** |
| GF(2^32) whole-word quadratic, four serial/ID input modes | 256 | 960 | **0** |

The GF(256) models produced 6 coincident bytes across 960 predicted bytes. The GF(2^32) models produced 15 coincident bytes across 3,840 predicted bytes and 15,348 differing bits across 30,720 predicted bits, consistent with chance-level byte/bit agreement. No complete 32-bit held-out word was predicted by any model. Synthetic positive controls passed.

The source-paired publisher hypothesis is therefore rejected for these exact quadratic families. The result does not exclude other source transformations or prove that the equal-suffix join is the historical issuer relationship.

## Decision

Do not use the PTW-417 serials to manufacture K04 candidates from these models. No selected target payload or acceptance hash was consulted, and no authentic K04 bit was gained.

Reproducer: `agents/agent44/k04_ptw_bay_quadratic_word_publisher_sft.py`. Run from the repository root with Python 3; it uses only the standard library and leaves all source, acceptance, candidate, and verifier files untouched.
