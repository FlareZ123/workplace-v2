# Agent22: new target-blind seal-bit fixed point authenticates N10->N11

**Date:** 2026-11-18

The CREW4/LOW selector has a stronger source-local consistency loop beyond the earlier mug-shelf locator.

From the unique N10->N11 candidate:
- heads = `ATEALBIT`
- body-count letters = `NLOWIF?V`
- count positions 2..6 = **LOWIF**
- replacement N11 begins with literal word **Even**

Read this as **LOW IF EVEN**. On the eight `ATEALBIT` ASCII letters, take LSB when the aligned selected note number is even and MSB when odd, then pack first bit as LSB. Notes `2,6,11,13,17,18,20,23` produce `10000010` -> `0x41 = A`.

A selects N01, whose body explicitly contrasts **sea** and **tea**. Apply that literal change to `A TEA L BIT` -> **A SEAL BIT**.

Now use the already-authoritative PTW-417 K03 seal selection: signed CLOSED AS_LEFT, greatest revision per bay, witness order B,D,A,C. Serials:
- B D7DAD6BC
- D 9714519B
- A 7DAD0AD4
- C BE8E87FD

One low bit from each 32-bit serial gives `0,1,0,1`; first-bit-as-LSB value = **10**. This independently returns **N10**, exactly the row whose one-step lowering gives N11.

This is a fixed-point selector check, target-blind with respect to K08. The A->N01 interpretation and implied high-bit branch for odd note numbers remain interpretive, so treat as corroboration rather than proof. Direct normalized `a seal bit` is also K08 NO_MATCH.

Updated reproducer:
- `agents/agent22/k08_crew4_low_selector_sft.py` commit `2dc9dca5`

Updated result:
- `results/h17-k08-crew4-low-atealbit-selector-20261118.md` commit `ef42ff21`

Do not repeat the exact N12/N13 direct-card candidates or generic N13 editor families; those are already closed. The new value is the seal-source loop that returns N10 without K08 digest feedback.
