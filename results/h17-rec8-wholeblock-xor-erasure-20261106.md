# REC8: arbitrary whole-component XOR-parity two-erasure recovery (6 November 2026)

**Agent34 | original acceptance unchanged | exact source-conditioned model negative.** Six original components K01, K02, K03, K05, K06 and K07 still PASS. K04's historical print coupon and K08's final author phrase remain unknown; combined verifier still INCOMPLETE.

## A different self-contained recovery hypothesis

A possible forgotten parity layer on the eight-component archive would let the six known 128-bit blocks recover **both** missing blocks without the original K04 physical coupon or the unquoted K08 margin. Prior [non-systematic RS(8,6)](h17-rec8-crossslot-reed-solomon-two-erasure-candidate.md), [RAID6 P+Q](h17-rec8-systematic-raid6-two-erasure-20261104.md) and [2-adic affine recurrences](h17-rec8-modular-affine-firstorder-two-erasure-20261104.md) test specific field coefficients or recurrences. This experiment instead tests **every possible XOR of whole known 16-byte components**. It covers any system of **two independent 0/1-coefficient parity-check equations** over whole 128-bit blocks that makes K04 and K08 uniquely recoverable, irrespective of the order or identity of the two parity rows.

For two parity equations, write their unknown-column coefficient matrix as a 2x2 invertible binary matrix. The inverse is also over GF(2), so both missing blocks must be XORs of subsets of the six independently accepted known blocks. Thus each missing slot has at most **2^6=64 possible exact complete components** under this entire architectural assumption. This proof does not require choosing the parity equations or ranking guesses; a SHA256 check of the 64 values is exhaustive for the named model.

## Actual source experiment

The immutable source commitment file has SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`; the K04 route sheet has SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`. Verify the official six authentic 16-byte component values against their **six complete original SHA256 slot commitments** first.

In four possible input views, permit K02 and K07 to use their accepted 16byte component or their independently extracted physical prehash 16byte block. For every view enumerate all64 six-block XOR subsets (including zero). For K04 separately test the XOR-subset as final component, and an alternative **physical-coupon** interpretation by XORing the full unaltered route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; for K08 test XOR-subset as the final HMAC-reduced 16byte component. Compare every candidate to the complete 256bit official slot SHA256 commitment. The K08 phrase itself is not reconstructed or assumed to be a 16byte string.

| Original experiment | Observed |
| --- | ---: |
| Known original REC8 slot commitments | 6/6 PASS |
| Source-prehash/accepted-input views | 4 |
| Binary subset masks per view | 64 |
| Complete target candidate assignments | **768** |
| Distinct K04 full candidates | **288** |
| Distinct K08 full candidates | **144** |
| Authentic K04 SHA256 matches | **0** |
| Authentic K08 SHA256 matches | **0** |
| Planted two-equation XOR erasure and physical-mask positives | **5/5 PASS** |

[Portable source-pinned Python 3 reproducer](../agents/agent34/rec8_binary_xor_parity_sft.py). A local equivalent executed on the supplied unmodified 46-member ZIP produced exactly these counts; remote source was pushed and fetched for verification. The model's synthetic positives use genuinely planted missing blocks and solve independent parity-check equations before mask reduction, with direct full-block digest comparisons.

## Limits and implications

The complete no-hit rules out **unknown two-row whole-block XOR parity without outside constants or nonlinear per-slot transforms**. It does not reject arbitrary bit-level GF(2) mixing matrices, parity involving an unrecovered master secret, a genuine historical coupon or an actual final handwritten caption. The archive's source route sheet does not assert parity relationships, so this is an explicitly speculative architectural hypothesis, tested once rather than adopted as historical fact.

This closes a simple untested gap in the independent-slot assumption with a proof-level candidate-space bound. It adds **zero authenticated K04 bits and zero verbatim K08 words**. Future work should seek an original selected-stage producer/copy witness or an author-final literal; enlarging unconstrained parity matrices would lose the reduction's explanatory power.
