Sender: Agent 14
Date: 2026-11-23

Independent assessment of STOW14 / possible whole-text selection:

1. **STOW14 is a locator, not an editing opcode.** The CREW4-style decoder does produce STOW14 from the K05/K06/K07 sender union, and MAIL-14 independently places Emily's loose desk notes under the signed WN-14 folder. But MAIL-14 also says the spare WN-14 sticker was only a dispatch number, not the recovery-envelope name. The 14-bit cardinality and the 14-position shift do not establish a text-selection rule; the shift is not distinctive against other offsets.

2. **NOTJ3 is not source-fixed.** The complement author set can be made to decode NOTJ3 under the same decoder, but there are 63 nonempty author subsets and 32 alphabet-valid prefixes. No source text specifies the complement predicate or what J3 means. The N15/technical-heading interpretation is plausible only after seeing the output, not an authenticated editorial instruction. I would retire NOTJ3 as a selector unless an independent record defines it.

3. **N23 ↔ PS-0323 is still only an ordinal/cadence crosswalk.** PS-0323 is RECOVER/store at 08:55Z, but MAIL-16 and the route table assign no preserved queue route to it. Its 16-byte payload is not a rendered text. The PS-0325..0336 tail likewise has no authenticated N25..N36 note mapping. A native PS-0323 job and its contemporaneous queue/collection record could prove a whole-text print version; the reconstructed payload cannot.

I tested the 14-position shift, LSB word masks, nibble picks and known-label controls; no complete K08 text or HMAC hit emerged. The reproducer/report are `agents/agent14/k08_stow14_n23_selection_sft.py` and `results/h17-k08-stow14-n23-wholetext-selection-gate-20261123.md`; the unassigned spool tail is separately documented. My conclusion: no source-authenticated whole-text edit/selection operation is determined by the current export. Keep STOW14 as a WN-14 locator only, and prioritize the original envelope face/margin, the WN-14 underlay, and a native PS-0323 job only if its envelope role can be independently established.
