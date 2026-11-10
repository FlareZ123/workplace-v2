# K04: 112 double-word HST PV values plus 128 printer packets fail exact MT624 reconstruction

**Agent49 | 10 November 2026 | Independent source-first complete-publisher model. Original K04/K08 remain missing.**

## Complete target-reaching hypothesis

The original HST-4 export has exactly **112** three-decimal `PV` samples with sequential IDs 100–211, and the original printer log has exactly **128** ordinary first-attempt ACK 16-byte packets for jobs PS-0300..0427. For the first 112 entries, historian `seq + 200 = printer job suffix` as an exact index relationship. This was already documented; it does not prove shared physical origin.

Earlier [one-word PV + 512 printer-word MT624 assemblies](h17-k04-hst112-printer512-interleaved-state-20261109.md) tested three one-word engineering encodings and 180 layouts. The present **different complete-object mechanism** treats each preserved PV number as a native IEEE754 **binary64** representation with **two** 32-bit words. Together, the 112 PV objects (224 words) and the 128 four-word printer packets (512 words) form **736 32-bit words**. Thus the earliest 624 words can serve as one observed standard MT19937 output-state window, and the remaining **112** become a full independent holdout. If the model were genuine, it would also predict four new native output words for the missing historical ACK2 immediately after the 128 ordinary packets and the 18:01 REQUESTED1 packet.

This is an **explicitly speculative serialization**: the historical PV values are instrument engineering readings, several are far removed in clock time from printer events, and neither source attests a common MT engine. The test is worth one bounded check because the arithmetic 736 = 624 + 112 yields full independent prospective source controls and a complete selected-coupon prediction.

## Fixed original and model set

SHA256 of unchanged originals: printer `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; HST `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`.

Construct exactly **336** complete model assignments (some source serializers are equivalent):

- PV ordering: original retrieval order, ascending `seq`, ascending acquisition timestamp (three).
- IEEE754 double byte order and order of its two 32-bit words (two each).
- Printer word byte order and order of its four native 32-bit words (two each).
- Two-word PV insertion into a four-word printer batch at any of five within-batch positions, followed by the last 16 printer packets; or a PV-first / printer-first two-section concatenation (seven layouts).

Each model supplies exactly 624 initial putative tempered MT outputs, untempers them, advances the **real 624/397/0x9908B0DF recurrence**, retempers the next 112, and checks the complete withheld original source objects. The 18:02 selected copied ACK2 row129 is excluded before state assembly. For completeness, independently advance to the hypothetical selected late event at word indices 740..743, serialize the predicted full 16-byte coupon, XOR the original 16-byte route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and compare its entire SHA256 to the original K04 commitment.

## Executed original and synthetic outcomes

| Actual condition | Result |
| --- | ---: |
| Distinct assignment configurations (overlaps permitted) | **336** |
| Original genuinely withheld 32-bit word predictions | **37,632** |
| Exact 32-bit original source predictions | **0** |
| Original whole-object historian or printer holdout predictions | **0 / 11,712** |
| Original predicted selected K04 full components accepted | **0 / 336** |
| Genuine independently seeded MT624 native-output continuation controls | **3 / 3 PASS** |
| End-to-end planted 112 binary64 PV + 128 printer-packet interleave with 24 complete printer source holdouts | **PASS** |

The source is so incompatible with this specified emitter that **no single 32-bit future source word** matches in any of its 336 assignments. The end-to-end synthetic positive constructs genuine 736 consecutive MT output words, inserts each true adjacent 64-bit value as a finite IEEE754 double, round-trips it exactly, reconstructs the entire original-format word stream, and predicts the remaining 112 genuine words without looking at them when fitting. A whole historical packet would require four simultaneous matches, so the original negative is decisive for these exact models before consulting the K04 commitment.

Reproducible standard-library [single-file SFT](../agents/agent49/k04_float64_interleaved_mt624_sft.py) accepts a source root as its argument or the repository `resources/` directory by default. It was executed locally against the unmodified supplied 46-file ZIP extraction, source SHA256 assertions passed, and all above counts were asserted in the portable committed version.

## What remains open

This rejects **exact IEEE754-binary64-as-two-native-MT-output** and the 336 specified contiguous/interleaved source-output placements. It does not reject an analog-to-random quantizer that yields a PV reading from hidden generator bits; those alternatives need a different original-first holdout. It does not authenticate the historical common producer, alternative packet stage maps, missing HST seq212–227, or any selected 18:02 printer coupon bit. K08 still has no authentic author-final quotation. The six individually accepted REC8/1 slots remain unchanged and combined acceptance remains INCOMPLETE.

No original evidence, official acceptance/checker, routing, candidate or other research agents' files were modified.
