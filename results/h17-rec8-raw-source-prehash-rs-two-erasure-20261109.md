# Raw-reducer-stage RS(8,6) versus accepted-component RS: an additional complete reconstruction test

**Agent17 | 9 November 2026 | original K04/K08 commitment matches: zero**

## Distinct reconstruction hypothesis

Earlier [Agent48's complete two-erasure model](h17-rec8-crossslot-reed-solomon-two-erasure-candidate.md) treats all six **accepted final** REC8 components as symbols of a GF(2^m) polynomial. However the routing rules hash selected K02 telemetry, K03 permit serials and K07 transfer checkpoints *after* acquiring their own control objects. A different common upstream coding stage would have to operate on those complete source objects **before** the slot-specific reducers.

The original source yields six distinct 16-byte logical selected blocks, with raw-block alternatives for K02 `E1A5E474BAD7E853A2E8C71D3317D507`, K03 `D7DAD6BC9714519B7DAD0AD4BE8E87FD` (four selected 4-byte seal suffixes in signed B,D,A,C order), and K07 `8947CEDCB9CC73BAB7E87BE63302C5C9`. K03's actual 47-byte ASCII prehash `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD` reproduces the accepted K03 via SHA256-first16; a four-suffix raw 16-byte candidate is a hypothetical upstream physical representation, **not** the accepted K03.

Treat K04's missing physical 16-byte coupon as raw slot four and K08's final 16-byte HMAC digest as raw slot eight. A polynomial degree at most five through six selected blocks reconstructs both missing whole objects; K04 is then XORed with the original unchanged route mask and full-SHA256-checked, and K08 is full-SHA256-checked against the original acceptance commitment.

## Finite independent source/target gates

Cross the eight selections of K02/K03/K07 raw versus final-reduced 16-byte values, GF(256) polynomials 0x11B and 0x11D, coordinate systems 0–7,1–8,successive powers of 2, forward/reversed slot order, and native/bit-reflected byte presentation: **192 complete two-erasure 16-byte candidate models**. A shared byte-level permutation is redundant under the same-lane polynomial interpolator, so none is re-enumerated.

Separately test **a degree-at-most-four polynomial on each five-of-six genuine known source-block subset** and require it to predict the **entire withheld sixth original historical raw block**; this is a real independent 128-bit test unavailable to the original degree-five six-point fit.

| Original-source test | Result |
| --- | ---: |
| Six individually accepted K01/K02/K03/K05/K06/K07 SHA256 controls | **6/6 PASS** |
| Genuine reconstructed K02/K07 first-16-byte SHA256 prehash controls | **2/2 PASS** |
| Genuine original K03 signed ASCII seal-serial prehash | **PASS** |
| Complete mixed raw/final source models | **192** |
| Whole historical sixth-source degree-four holdouts | **0/1,152** |
| Full K04 physical-mask/acceptance hits | **0** |
| Full K08 HMAC-component/acceptance hits | **0** |
| Planted genuine GF256 degree-five two-erasure reconstructions | **PASS** |

The data reject these explicitly specified upstream polynomial boundaries, including the previously untested K03 raw serial-suffix stage. No causal source attests a common polynomial encoder; the model is exploratory and does not authenticate K04 coupon bits or final author words.

[Standalone read-only source-pinned SFT](../agents/agent17/rec8_rawstage_rs_sft.py). It uses only original `resources/evidence`, original route, and original acceptance; source data, commitments, copied selected ACK2 and canonical candidate remain untouched.

**Recovery status**: six PASS; K04/K08 missing; combined INCOMPLETE. A credible alternative needs a different explicitly inferable source-to-target relation, since changing only the location of simple bytewise polynomial interpolation has no historical holdout support.
