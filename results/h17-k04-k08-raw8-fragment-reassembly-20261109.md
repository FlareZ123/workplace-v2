# H-17 raw-source two-fragment reconstruction: complete K04 and K08 target negatives

**Agent 6 | 9 November 2026 | Original supplied 46-member archive | Complete bounded test.**

## Mechanism

The retained print spool is explicitly a fragment reconstruction of uncertain physical integrity. A hypothesis different from correcting positions in the selected copied ACK is that a sixteen-byte selected coupon (or otherwise retained K08 binary component) was recorded as **two separated authentic eight-byte halves** elsewhere in the export.

Collect each distinct eight-byte sliding window across **41 original evidence files** under resources/evidence. For any intact source text field with at least sixteen hexadecimal characters, decode its full binary value if its digit count is even, then collect every eight-byte sliding window of that decoded value. Deduplicate and sort lexicographically. The encrypted BX25 PDF is excluded and never decrypted. The extraction includes literal text, raw binary and binary forms of genuine original hex fields.

There are exactly **42,698 unique** source fragments. Their sorted concatenation is 341,584 bytes, SHA256 **a14b1ee50ae0110b9d8b07cb246d8681697dddfe86cd89ee87e7b91c2329f6ff**. Reproduce with [the source-fragment extractor](../agents/agent6/k04_k08_raw8_mosaic_prepare.py).

## Original complete candidate construction and result

For **each ordered pair** of eight-byte fragments A and B, form the complete 16-byte hypothetical original object P=A||B. Exactly **42,698² = 1,823,119,204** ordered assemblies are tested, including same-fragment pairs, without guessing any byte.

For K04, compare full SHA256 of P XOR recorded mask **8556C8CB6140A7F9A5123AC7571BEE1C** with the unchanged original commitment **930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0**. For K08, compare full SHA256 of P directly against original K08 component commitment **285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747**. That binary K08 bypass is hypothetical; a hit would still need provenance independent of the lost author-final words.

Completed **1,823,119,204** assemblies for **each** slot, a total **3,646,238,408 full 16-byte SHA256 commitment checks**:

    COMPLETE fragments=42698 pairs=1823119204 k04_hits=0 k08_hits=0 planted_hits=1 elapsed=70.130

The optimized one-block SHA256 implementation was compared against independently computed OpenSSL SHA256 on ten distinct complete 16-byte strings before any original test. A separately computed synthetic complete assembly from real source fragment indices 7 and 42 was found **exactly once**. Five-thread local execution completed in 70.13 seconds. The canonical candidate, original archive, acceptance data and verifier were untouched. [Portable parallel source](../agents/agent6/k04_k08_raw8_mosaic_sft.cpp).

## Consequences and limits

The correct K04 or K08 component does not arise from the precise, unmodified **eight-byte source-fragment concatenation** class. This differs from earlier 16-byte literal-window scans and four-byte selected-ACK corruption repairs. The negative does not exclude reversed/reshuffled fragments, transformations, lost native printer objects, original values not present in surviving fragments, or Emily's final written sentence.

No selected coupon bit or final normalized caption word was authenticated. Original state remains six individual PASS values, K04/K08 missing and combined INCOMPLETE.

Do not rerun this exact ordered raw8+raw8 family. Source models predicting an intact same-role historical print object or reconstructing an independently attested author-final version should take priority over more untethered transformations.
