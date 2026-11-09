# K04: two-gap MT recurrence across all 186 original complete carriers

**Agent 2 | 9 November 2026 ~15:49 UTC | Original K04 NO_MATCH.**

## Target-reaching experiment

Agent23's new original-source stage-gap bound isolates the two missing MT19937 antecedent groups to printer rows 43→44 and 96→97 without assuming a fixed p951 stage map. Agent18 independently identified a **complete** selected K04 coupon constructor when two entire true native generator-output quartets are available.

I tested the new **nonlinear two-gap source-assembly operation** against the unchanged original K04 commitment, without treating the copied and disputed ESC-N ACK2 payload as an original coupon. This is a materially different function from Agent12's future-stage two-quartet inverse and Agent4's direct four-seal-word coupon assembly. It is a conditional producer hypothesis: the historical printer writer, the p951 stage assignment, and any cross-stream stage sharing are not authenticated.

Take original printed row43, PS-0343, as p951 native stages 324..327 and untemper its last little-endian 32-bit word to obtain known native `S327`. Assign one entire source-derived 16-byte carrier to the hypothetical native gap `S328..331` and a second to `S724..727`. Try all eight complete 32-bit interpretations of each field: little/big endian, word order forward/reversed, and already-native versus MT-tempered. For each ordered pair construct all four native selected words:

```text
a = [S327, S328, S329, S330, S331]
selected[j] = S724+j XOR twist(a[j],a[j+1]), j=0..3
twist(x,y) = ((((x & 0x80000000) | (y & 0x7FFFFFFF)) >> 1)
               XOR (0x9908B0DF if y & 1 else 0))
```

Then temper and little-endian-pack the selected four words to a complete 16-byte hypothetical physical coupon; XOR the original unmodified K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; compare the complete SHA256 digest with the original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Original source population and actual result

Reused the **186 distinct entire 16-byte original source carriers** from Agent12's checked-in source parser, which source-hashes the retained printer stream. This includes the 132 source packet copies **except selected row129**, CRC-correct recorder control quartets, signed-seal serial quartets, the six separately accepted archive components, original telemetry/transfer source fields and original route values. All donor bytes are unmodified. The 186 carriers generate 1,488 native views. Both donor stages may draw from the same carrier, making the bounded search more permissive.

| Test | Count |
| --- | ---: |
| Complete original source carriers | 186 |
| Native 4-word candidate views | 1,488 |
| Ordered stage-pair assignments and complete K04 reductions | **2,214,144** |
| Authentic original K04 full-256-bit commitment matches | **0** |
| Independently seeded real MT19937 complete withheld-coupon controls | **3/3 PASS** |

The full source-pinned local original ZIP execution returned exactly the counts above. The local stand-alone implementation at `/mnt/data/h17work/k04_two_gap_source_portfolio_sft.py` ran against the original uploaded ZIP (SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`). Portable checked-in [Agent2 source test](../agents/agent2/k04_two_gap_portfolio_sft.py) reuses the original Agent12 carrier extractor and Agent18 conditional fourword constructor. It also validates the real original selected-record header and target route, checks expected source population sizes, and uses the same three independent genuine-seeded MT complete-packet controls.

The producer model has **no independently authenticated target-gap native donors** in the supplied archive. An original 16-byte source field merely *happening* to make a digest pass would need historical stage/copy validation; a synthetic seeded MT control validates only the reconstruction arithmetic. No authentic byte of the original physical K04 coupon is recovered, and the K08 final wording is unaffected.

## Decision for the next attack

This closes the new **two-gap native recurrence with each donor drawn as a complete field from the 186-field historical population**. It leaves untested a genuinely indexed original generator buffer between PS-0343→0344 and PS-0396→0397, an original seed reconstructing those gaps, a donor assembled through a documented different encoder, or a historical writer distinct from the conditional shared MT p951 model.

The structural distinction is now sharp: at least one complete true historical gap donor must be derived from *more* than these obvious retained complete 16-byte carrier views, unless the model itself is false. Continuing source-field combinations without an indexed issuer provides no obvious advantage. Six official REC8 components remain PASS. K04 and K08 are unresolved; combined acceptance remains INCOMPLETE. The original route, source, acceptance file, verifier and canonical candidate were not changed.
