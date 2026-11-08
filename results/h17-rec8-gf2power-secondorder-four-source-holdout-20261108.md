# H-17 REC8: four-source GF(2^w) quadratic erasure reconstruction with two blind historical holdouts

**Agent 18 | 8 November 2026 | Original K04/K08: zero matches.**

## Complete-target hypothesis

An alternative to the independent physical coupon and final personal caption would be a common second-order finite-field recurrence across the eight archive components, permitting both missing values to be recovered from the accepted six. No surviving route text says the eight components form a code or recurrence. This experiment tests an **explicit alternative archive architecture** with a complete candidate/holdout prediction, rather than a target-only byte repair.

Split each 16-byte slot into independently evolving lanes of width 8, 16, 32, 64 or 128 bits over an irreducible characteristic-two polynomial. Each lane follows
`X[n] = a*X[n-1] XOR b*X[n-2]`.
Allow **different a,b per lane**, a substantially more flexible mechanism than a shared-coefficient second-order recurrence. As an independently more restrictive subcase, test one shared a,b across all lanes.

The historical K01,K02,K03,K05 values alone determine a unique lane pair a,b whenever the native division denominators are nonzero. Writing `x1,x2,x3,x5` for four known lane symbols, a *characteristic-two* identity eliminates the unobserved K04:

`a^2=(x1*x5 XOR x3^2)/(x1*x3 XOR x2^2)`;
`a=sqrt(a^2)`;
`b=(x3 XOR a*x2)/x1`.

Every nonzero element has exactly one square root in GF(2^w). Thus **K06 and K07 can be reserved as genuine whole-source historical holdouts**: neither their values nor the unknown K04/K08 commitments are needed to determine the producer coefficients. The resulting recurrence predicts K04, K06, K07 and K08 in one causal calculation. Models failing either full original K06 or K07 are not accepted as historical producer explanations, even if they happened to hit a missing-slot digest.

## Frozen source and field variants

The six original source-accepted 16-byte values are checked against the six unchanged acceptance SHA256 commitments. The code holds K06 and K07 out of the coefficient fit and uses no original printer ACK2 copied payload or guessed desk phrase. It checks nine irreducible binary fields:

- 8-bit: `0x11B`, `0x11D`.
- 16-bit: `0x1100B`.
- 32-bit: `0x10000008D`, `0x104C11DB7`, `0x1000000AF`.
- 64-bit: `0x1000000000000001B`, `0x1000000000000001D`.
- 128-bit: `0x100000000000000000000000000000087`.

For each field, two word-endian layouts and two whole-block byte orientations are tested. Common versus independent lane coefficients are compared. These are fixed conventional representations, not arbitrary per-slot masks.

## Original full-candidate outcome

| Source/target observable | Actual result |
| --- | ---: |
| Original accepted components individually validated | **6/6** |
| Planted complete eight-slot histories recovered from K01/K02/K03/K05 | **144/144** |
| Original independent-lane complete models | **36** |
| Original shared-coefficient models consistent with four source slots | **0** |
| Original K06 + K07 entire 16-byte historical holdouts predicted correctly | **0/36** |
| Original K04 full 256-bit commitment matches | **0/36** |
| Original K08 full 256-bit commitment matches | **0/36** |

The full 16-byte K04/K08 candidate values for each of the 36 original models were actually constructed and compared against the original slot SHA256 commitments. No approximate or prefix comparisons were used. Every planted test generated the complete 8-slot sequence from its own synthetic first two states and coefficients. The solver recovered the coefficients and both erased slots exactly from just its four allowed inputs, then predicted K06 and K07 without viewing them.

This result is a **bounded source-plus-target falsification**: the enumerated finite-field second-order erasure scheme cannot reproduce the six authentic components. It does not establish historical independence of the components or exclude unknown reducers, a different recurrence order, source-specific pretransforms or other field structures. The original route makes no such recurrence assertion. No original K04 physical coupon bits or author-final K08 words were recovered.

Nearest prior art: [shared bytewise GF(256) order-3 recurrence](h17-rec8-crossslot-gf256-order3-recurrence-20261107.md), [shared bytewise GF(256) order-4 recurrence](h17-rec8-crossslot-gf256-order4-recurrence-20261108.md), [modular integer second-order ring recurrence](../agents/agent47/rec8_mod2power_secondorder_recovery_sft.py), and [GF(2^w) Reed-Solomon degree-five erasure interpolation](h17-rec8-crossslot-reed-solomon-two-erasure-candidate.md). The new incremental scope is **independent lane coefficients, order two over GF(2^w), exact four-source square-root fitting, and full K06/K07 holdouts.** Do not count overlapping shared-coefficient subcases as a newly established research direction.

## Reproduction

[Standard-library, original acceptance-pinned single-file SFT](../agents/agent18/h17_rec8_gf2power_squaregap_sft.py). Run the script from the repository; it reads `resources/acceptance.json` without changes and checks its own control and result counts. No source archive, candidate, mask, nonce or verifier was changed.

Six original slots remain PASS; K04/K08 MISSING and the original combined REC8/1 result remains INCOMPLETE.
