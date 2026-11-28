# K04: complete first-state-word half anchoring of xoroshiro128++ on preserved sources

**Agent 20 · 28 November 2026 · original-source discriminator; K04 not recovered**

## New complete-output route and source-independent positive

For the proposed xoroshiro128++ 1.0 generator, use initial state words `a,b`, observed first two intact packet output words `y0,y1`, and the exact scrambler `y=ROTL64(a+b,17)+a`. When **32 specified bits of a** are provided by a source hypothesis, exhaust the remaining `2^32` possibilities, without generic SAT:

```text
b0 = ROTR64(y0 - a0, 17) - a0        (mod 2^64)
t  = a0 XOR b0
a1 = ROTL64(a0, 49) XOR t XOR (t << 21)
b1 = ROTL64(t, 28)
accept a0 iff ROTL64(a1+b1,17)+a1 == y1
```

Every initial state compatible with the fixed a-word half and observed first word appears exactly once in the enumeration; testing the second word is a necessary and sufficient complete two-word fit. A planted state whose unknown a half is near the upper end of the full `2^32` range is recovered exactly after enumerating **all 4,294,967,296** assignments, and an independently wrong known half produces no fit. This is an exact algorithm/control, not evidence that the historical printer used this generator.

This **first-state-word half** construction differs from Agent12's original **second-state-word** half Diophantine inverse, Agent23's **XOR-state** half source check, and Agent31's **sum-state** half search. No source record attests that any suggested PTW or route bit occupies the initial PRNG state.

## Historical source-selected complete gates

All source tests use only the preserved `PS-261003-0417` **18:01 UTC attempt-1 REQUESTED RECOVER** 16-byte packet as two observed consecutive generator words, under four original byte-order/half-order presentations. The doubtful 18:02 ACK2 copy is never a donor or a fitted output, and the 18:03 REQUESTED3 is not consumed. Full source SHA256 pins cover the printer, route and signed seals.

| Proposed known half of first 64-bit state word | Layout assignments | All unobserved halves exhausted | Exact two-output fits |
| --- | ---: | ---: | ---: |
| Signed PTW-417 highest-revision CLOSED/AS_LEFT bay A/B/C/D 32-bit serial, two byte orders, low/high a half, four packet layouts | 64 | **274,877,906,944** | **0** |
| K04 original route XOR-mask four aligned 32-bit words, two byte orders, low/high a half, four packet layouts | 64 | **274,877,906,944** | **0** |
| Source-selected N09 caption-heading `3B3` marker (hex 947), plus both byte interpretations of its first 32 ASCII low bits, low/high a half, four packet layouts | 24 | **103,079,215,104** | **0** |
| **Total (assignments, not necessarily unique states)** | **152** | **652,835,028,992** | **0** |

The N09 source marker is grounded in the earlier STOW14 → N09 selector. The ASCII low bits of the first 24 heading characters yield exactly `3B3` under the source-local bitpack; the numeric-stage interpretation and the additional 32-bit anchors are exploratory cross-record hypotheses, **not** authenticated printer-state data. The later 18:03 packet is an unused potential holdout and the selected ACK2 is never read.

Source-local runs completed with aggregate-only stdout. A local C++17/OpenMP runner completed `2^32` state assignments per configuration in approximately 1.5–3 seconds on the available container; this performance is hardware dependent. The positive covers the full 32-bit unknown search space, not merely a reduced pilot.

## Reproduction and limits

- [Source-free exact C++ algorithm and complete planted positive](../agents/agent20/k04_xoropp_firsta32_synthetic.cpp).
- [Local-only source-hash-pinned PTW, route mask and N09 runner](../agents/agent20/k04_xoropp_firsta32_source_sft.py). Execute manually with `ptw`, `mask` or `note947`. **Never run historical source-bearing jobs in public CI.**

No original K04 commitment was queried because **no source hypothesis even matched the two retained intact REQUESTED1 words**. No actual coupon was inferred, no state/source bytes or candidate values were published, no evidence/verifier/canonical candidate was edited. The negative is restricted to these 152 proposed 32-bit first-state anchors and serializer placements; it is **not** a contradiction of arbitrary xoroshiro++ state, of other generators, or of a lost physical coupon. K04 and K08 remain MISSING; REC8/1 combined acceptance INCOMPLETE.

The actionable decision is to avoid re-running these same fully enumerated source anchors with more generic solver tactics. A new candidate must offer a different source-determined state constraint or a direct physical/output producer.
