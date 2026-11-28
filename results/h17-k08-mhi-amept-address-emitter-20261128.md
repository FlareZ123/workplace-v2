# K08: N20 MHI emits AME, transfer emits P, closing the AT/MT/ET/PT address generator

**Agent 42 | 28 November 2026 | target-blind address-generation closure | terminal final-version edit still missing**

## Material result

The four address pairs `AT / MT / ET / PT` were already known to recover the fixed N20 semantic payload, but the varying coordinate sequence **A/M/E/P** had been consumed as an observed decoder input rather than generated from one compact source mechanism.

The new N20 `MHI` branch closes the first three coordinates directly.

N20 is note **20 = T** in the established A1Z26 namespace. Its fixed raw first-24-character LOW BIT head emits **MHI**.

From that same source-emitted token:

1. **A** — A1Z26 `MHI` addresses N13/N08/N09. Their first body-word initials are A/B/N. Taking their A1Z26 low bits gives `1,0,0`, packed first-bit-as-LSB = **1 = A**.
2. **M** — the established HEAD operation on the emitted token itself gives **M**.
3. **E** — whole-token ASCII LOW BIT of `MHI` is **5 = E**.

Pair each with the emitter row N20 = **T**:

**AT / MT / ET**

The independent transfer-side source program supplies the fourth pair. MAIL-13 fixes AX-7782; the already-derived `ATTEMPT TAILBIT LOW IF EVEN` operation selects the alternating attempt bytes, whose low bits pack to `50D4`. Both bytes have even parity and decode as 7-bit ASCII:

**PT**

Therefore the complete address set is now generated source-only as:

**AT / MT / ET / PT**

with varying coordinate sequence **AMEP** and invariant coordinate **T**.

## Independent payload check

Apply the existing A1Z26 address rule and unique-maximal-common-span extraction:

| Address | Notes | Span length | SHA-256 |
| --- | --- | ---: | --- |
| AT | N01/N20 | 2 | `556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0` |
| MT | N13/N20 | 5 | `a9bb20e02706cf2079ed0a11b3fededd1c9325edeea5925734f7592ca7c943c9` |
| ET | N05/N20 | 2 | `44359e21492d788147966d8c0bc5beb2f4f4d0d05dd36f3ff36a0cd36a349907` |
| PT | N16/N20 | 2 | `9ad80878ed715fd6a1b1bf2b353e344a3dda762a4f3f5c713ccb2dad3d01d88f` |

In N20 those spans start at zero-based word positions **6 / 8 / 13 / 19**. Taking N20 from the AT start through the word before the PT boundary yields the independently established **13-token fixed payload**, SHA-256:

`4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`

No K08 nonce, acceptance target or candidate file is read anywhere in this derivation.

## Why this changes the mechanism picture

Before this result, the address heads `AMEP` were useful but partly exogenous: downstream work could consume them, and Agent14 could use their structure to reach N06, but the source program did not explain why the first three coordinates should be exactly A/M/E.

Now one independently unique N20 raw LOW BIT emission explains them through already-active operator types:

- addressed-note HEAD low bits -> A;
- token HEAD -> M;
- token LOW BIT -> E.

The independent transfer side supplies P and simultaneously supplies the same fixed T coordinate. The resulting address set reproduces the already-fixed payload fingerprints rather than being chosen for readability.

This is a source-program closure, not a statistical claim that these operators were uniquely inevitable among every conceivable transform. The important control is that every downstream text fingerprint and the 13-token payload were fixed before this composition.

## Connection to the draft/photo lineage

The same MHI-addressed triple also yields the newly reported **N06 Second desk draft + N01 photograph** branch. Separately, source-emitted THE yields **N02 First draft + N01 photograph**, and first/second ordinals over that shared photograph reproduce the AT span fingerprint.

Thus the same source-local machinery now connects:

**first/second draft lineage -> shared photograph -> AT**  
**N20 MHI -> A/M/E -> AT/MT/ET**  
**transfer parity -> PT**  
**addresses -> fixed N20 semantic payload**

The remaining missing edge is no longer the address generator. It is the final authoring/version operation from this calibrated editorial structure to the exact N23 keeper wording.

## Boundary

This does not assert any K08 final word and does not change the accepted candidate. K01/K02/K03/K05/K06/K07 remain accepted; K04/K08 remain missing.

Do not spend follow-up work searching alternate `AMEP` coordinate explanations unless they predict a stronger independent control. The productive frontier is a source-selected terminal version/edit operator consuming the now-generated fixed payload and/or fixed N02/N06/N01 lineage.

## Reproducer

`agents/agent42/k08_mhi_amept_address_emitter_sft.py`

It pins crew notes, MAIL-13 and transfer audit; reproduces MHI, A/M/E, PT, all four addresses, all four span fingerprints, their N20 positions and the fixed payload fingerprint. It never reads K08 target material.
