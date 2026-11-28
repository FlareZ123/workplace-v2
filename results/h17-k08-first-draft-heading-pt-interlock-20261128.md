# K08: STOW14-selected First draft independently emits the PT payload boundary

**Agent 42 | 28 November 2026 | target-blind cross-program interlock | final wording unresolved**

## Result

The source program now has a second, independent construction of the final overlap address **PT**.

The already source-selected chain is:

`STOW14 -> column 14 -> LEN -> LOW BIT 2 -> N02`

N02 is explicitly labelled **First draft for the crew board**.

Apply the established heading **HEAD low-bit** channel to that fixed heading. Its six word-initial A1Z26 parities are:

`0,0,0,0,1,0`

packed first-bit-as-LSB:

`16 -> P`

N20 is note **20 = T** in the fixed A1Z26 namespace. Pair the newly emitted P with N20's coordinate T:

**PT**

This reproduces the same address independently emitted by the AX-7782 transfer path, where `50D4` has even parity and decodes as 7-bit ASCII **PT**.

## Matched source control

There are 19 colon-prefix headings in N01..N24. Under the same HEAD low-bit calculation:

- headings evaluated: **19**
- headings with HEAD value 16: **1**
- unique match: **N02 First draft**

No K08 target, nonce or candidate phrase is read.

## Boundary check

Read PT by the established A1Z26 address convention:

`P=16, T=20 -> N16/N20`

Their unique maximal exact common normalized span has length two and begins at zero-based N20 word position 19, exactly the already-established source-visible prohibition boundary used to terminate the fixed semantic payload.

Thus the First-draft branch predicts a pre-existing payload boundary rather than merely landing on a thematically plausible note.

## Unified address picture

The same-invocation MHI result already generates the first three changing address coordinates:

- addressed-note HEAD parities from MHI -> **A**
- HEAD(MHI) -> **M**
- LOW BIT(MHI) -> **E**

N20 supplies the invariant **T**, producing:

`AT / MT / ET`

The present First-draft heading supplies **P**, producing:

`PT`

The transfer parity path independently supplies the same PT. The full address-head sequence **AMEP** therefore has a source-local generation route with a held-out cross-carrier confirmation on its final coordinate.

This is stronger than the prior state in which AMEP was primarily consumed as an observed address pattern.

## Connection to the version lineage

The chain now joins the source-selected version structure directly to the payload program:

`STOW14 -> LEN -> N02 First draft -> heading HEAD=P -> PT stop boundary`

Separately:

`THE -> N02 First draft + N01 photograph`  
`MHI -> N06 Second desk draft + N01 photograph`

and the First/Second ordinals over N01 reproduce the independently fixed AT span.

The remaining unresolved edge is still the terminal author-final version operation. This interlock does not emit any missing N23 wording and does not change K08 acceptance.

## Reproducer

`agents/agent42/k08_n02_heading_pt_interlock_sft.py`

The source-pinned SFT reproduces STOW14, column-14 LEN, N02, the unique heading HEAD=16 value, note20=T, independent transfer PT, and the PT overlap boundary. It reads no K08 target or nonce.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.
