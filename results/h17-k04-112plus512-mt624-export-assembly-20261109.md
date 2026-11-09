# K04: complementary 112 historian PV plus 512 printer words as one MT624 state

**Agent 8 | 9 November 2026 | Original K04 NO_MATCH.**

## New complete-object hypothesis

The local HST-4 freeze has **112 PV records** (seq100–211), and the ordinary printer stream has exactly **128 complete 16-byte packets** (=512 32-bit words). The combined total, **624 native 32-bit words**, is the MT19937 state size. This exact arithmetic suggests a falsifiable *alternative retrospective export-assembly* model: the historian PV values and ordinary printer payloads were two serialized sections of one MT19937 output stream, with the late printer coupon emitted subsequently.

This is a **numerical coincidence plus speculative assembly hypothesis**, not a historically attested bridge. The native historian readings are 3-decimal process values; they have never been authenticated as raw MT words. In the genuine timestamps the PV acquisition occurs after the late printer jobs, so PV-first is only plausible if the export assembler reorders source generation.

## Frozen full-source construction

Use all 112 unmodified PV rows, either in seq, acquisition-time or file order. Represent each as one complete 32-bit word by each of three explicit codecs: IEEE754 float32 bit pattern, integer millivalue (PV ×1000 rounded), or integer rounded PV.

Convert each of the 128 ordinary acknowledged first-attempt printer 16-byte packets to four 32-bit words, with either endian and normal/reversed word order. Put the 112 historian words before or after the 512 printer words. **3×3×2×2×2=72** complete models with exactly 624 words each.

Untemper the 624 observed 32-bit words into a full MT19937 state, and generate the next **1024** native words. At each of 1021 four-word windows, serialize a complete 16-byte hypothetical coupon.

**Independent whole-object source controls:** exact original complete 16-byte late ESC-S PS-0448 ACK1 and WATCH-SPARE PS-0420 ACK2 packets, neither used to fit the generator. The suspect PS-0417 attempt2 copied bytes are also excluded from state fitting. For every predicted entire coupon, XOR the original K04 mask and check full 256-bit original K04 SHA256 commitment. The source SHA256s and original acceptance SHA256 are pinned in the SFT.

## Executed result

- 72 fully constructed 624-word MT states.
- 73,512 complete future coupon assignments (72 × 1021).
- **Zero exact 16-byte late-source holdout predictions** across both authentic heldout ACK packets.
- **Zero original K04 SHA256 commitment matches**.
- Positive synthetic MT state cloning and future 36-word exact-output checks at four separate stream offsets, including a twist boundary: **PASS**.

The [single-file standard-library SFT](../agents/agent8/k04_pv112_mt624_directstate_sft.py) reproduces the complete original-source test from unmodified repository evidence. The local execution used the separately attached original ZIP extraction whose SHA256s match.

## Decision

The exact 112+512=624 count by itself does **not** establish a historical publisher. The selected printer coupon cannot be reconstructed by these 72 direct-native-word archive-assembly models, which also fail both independent complete late ACK controls.

Do not inflate the count coincidence into a production claim or extend source-uncued PV codecs and permutations without a predictive source witness. This trial adds no authenticated K04 selected bit. Six slots remain PASS, K04/K08 remain MISSING, and combined REC8/1 remains INCOMPLETE.

## Independent repository execution

Manual GitHub Actions source replay [run 42589351287](https://github.com/FlareZ123/workplace-v2/actions/runs/42589351287) completed **SUCCESS** on 9 November 2026 at 08:54:47 UTC with both complete original evidence tests and synthetic controls. This confirms the checked-in portable Python SFT runs against the unmodified repository source. It does not improve historical source-model credibility or add an accepted recovery component.
