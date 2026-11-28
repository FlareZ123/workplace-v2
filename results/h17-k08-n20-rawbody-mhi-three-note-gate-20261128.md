# K08: source-selected N20 LOW BIT head independently emits MHI -> N13/N08/N09

**Agent 10 | 28 November 2026 | new source-only 3-note selector, not an author-final text emitter**

## Source-fixed observation

N20 (Emily's source-selected three-motif editor brief) is already selected independently by the AT/MT/ET/PT overlap decoder, before this test. Reuse the **existing ASCII LOW BIT** operation and the established first 24 character / first-bit-as-LSB packing convention from the N09-heading 3B3 path. Unlike the earlier note-word window permutation, this reads the **raw post-label body**, not body tokens, and fixes character origin to the first character (no offset search).

The first 24 source characters of N20 are "I wanted the line to hol". Their 24 ASCII low bits, grouped first-bit-as-LSB, decode to exactly the uppercase bytes:

**MHI** = 0x4D 0x48 0x49.

Existing A1Z26 numbered-note semantics give **M=13, H=8, I=9**, selecting the three original source records:

- **N13:** Emily's end-of-night desk/scene recollection, previously independently selected by the N09 heading and N06 overlap paths.
- **N08:** Jason's *Window photograph* caption, the window/water source role named by the envelope author's purpose and photo-captions trail.
- **N09:** Zoey's *Caption for the galley board*, already independently selected by STOW14/N23 and the AES/SHA/AES note-operator path.

This is a **source-address selection**, not a rule for concatenating these captions, not evidence Emily adopted any exact segment, and not a K08 component.

## Whole-corpus control

Pin the original 24-entry crew-note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Parse each record's raw first line, strip its colon-prefix label where present, and take the same **first 24 raw post-label body characters**, packing exactly three LSB octets. Among all **24/24** numbered note bodies, **N20 is the only one whose resulting three octets are all uppercase ASCII A..Z**. The N20 MHI result is exact and the A1Z26 addresses all exist. No other offsets, body windows, byte orders, glyph classes, target digest, nonce, printer, or PDF were used.

This specificity is a finite corpus census, **not** a statistical p-value after accounting for all agents' exploratory operator searches. The N20 source selection predates the inspection; the 24-bit/three-character convention is inherited from existing work, so the within-program relation is reproducible without target feedback.

## Consequence

The already established K08 source-program chains reach **N13 and N23**, but do not emit author-final wording. MHI supplies one new **independently fixed three-source donor identity**: Emily's N13 source scene plus Jason's N08 window/photo and Zoey's N09 galley/cup. It may help a future source-authenticated final-version operator identify which original photographs/captions or revision records to join, if those are recovered.

Do **not** turn MHI into an arbitrary one-word-per-note permutation or infer missing final wording from the three addresses. The current K08 HMAC slot remains MISSING and no seventh component is asserted.

Reproducer: [source-only gate](../agents/agent10/k08_n20_rawbody_mhi_gate_sft.py), reads only crew notes and prints the exact selector, role control and uniqueness count. This test deliberately does **not** read original K08 commitment, nonce or final phrase.
