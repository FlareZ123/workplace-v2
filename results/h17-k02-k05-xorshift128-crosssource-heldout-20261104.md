# K02 selected diagnostics to K05 selected recorder: compact xorshift128 producer heldout

**Agent 34 | 4 November 2026 | Original source-only computation, no K04/K08 value recovered.** This attacks an independent producer hypothesis based on *chronologically adjacent, independently source-selected* records. It does not rely on the previously hypothesized 624-word printer MT state or retest earlier printer output-gap or copied-ACK repairs.

## Historical clue and proposed mechanism

The original K02 GOOD/HOLD telemetry selector chooses eight 16-bit `LT-204 DIAG_WORD` values during **21:13:40–21:13:47 UTC**. The source-selected K05 recorder values are node49/event82, four CRC-good latch CONTROL words at **21:14:00–21:14:07 UTC**. One plausible but unrecorded generator architecture is a *shared compact-state 32-bit PRNG* whose output was consumed by the telemetry and recorder streams only seconds apart. A working original model could predict K05 from K02 as an independent holdout and potentially guide subsequent source-stage reasoning.

The specific tested generator is **Marsaglia xorshift128** with four 32-bit internal state words, transition

```text
t = x ^ (x << 11)
(x,y,z,w) = (y,z,w, w ^ (w >> 19) ^ t ^ (t >> 8))
output = new w, arithmetic masked to unsigned 32 bits
```

This variant has a GF(2)-linear 128-bit internal state. The test derives exact output-bit linear expressions for each hypothetical emitted word and solves all original K02 training equations using GF(2). It then predicts original selected K05 words at each **gap 0..96 extra 32-bit outputs**, enforcing complete equality on every independently fixed K05 bit. The K05 source is withheld from training.

Two original K02-to-PRNG data interpretations are predeclared:

1. **Eight cropped words:** eight selected 16-bit K02 source values represent successive high or low 16-bit halves of eight 32-bit PRNG outputs, with two byte orders and normal/reversed sequence: **8 interpretations**.
2. **Four full words:** adjacent selected K02 halfwords are paired into four complete 32-bit PRNG outputs, with two byte orders, normal/reversed word order and swapped/normal halfword order: **8 interpretations**.

Each source-compatible fit predicts K05 as four successive 32-bit outputs for 97 possible future gaps and four K05 word views (little/big endian, normal/reversed latch order). This would be **16×97×4 = 6,208** full assignments if every K02 interpretation were source-compatible. The selected printer ACK2, K04/K08 commitments and route mask play no role.

## Executed original-data result

| K02 representation | Original training models | Contradict original K02 alone | Compatible models | Fully evaluated K05 holdouts | Exact full-bit K05 matches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eight cropped 16-bit outputs | 8 | **8** | 0 | 0 | 0 |
| Four paired 32-bit outputs | 8 | 0 | 8 | **3,104** | **0** |

Every four-full-word K02 interpretation determines **all 128** generator-state bits and thus all **128** K05 candidate bits. Across the 3,104 full original K05 checks, the **closest** state prediction still disagrees on **44 out of 128 bits** (model K02 `little/reversed/normal-half`, K05 `little/forward`, future gap71). The eight-cropped-original-data branch never reaches K05 comparison, as the K02 low/high-half samples themselves violate the selected xorshift128 recurrence in every representation.

These are original-source full-packet holdout comparisons, so they reject the explicitly specified shared compact emitter rather than only observing failure of some target commitment. They cannot establish independent physical-device entropy or refute arbitrary other PRNGs, different output extraction, nonconsecutive telemetry reads, or different generation timestamps.

## Original source pins and controls

- Selected K02 prehash bytes `E1A5E474BAD7E853A2E8C71D3317D507`, original telemetry SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`.
- Selected K05 raw fourword controls `FF8B78200A56E8586DCDA00EF01E4572`, original recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.

A planted synthetic 128-bit xorshift state passed two genuine holdout tests: training on four full 32-bit outputs gave rank128 and **128/128 correct independently heldout output bits**; training on eight successive low16 cropped outputs gave rank125 and **59/59 correct independently predicted future bits**. Both controls used a 13-word gap and the same source-expression, GF(2) elimination and holdout machinery. The original file digest pins and all exact negative/result counts are asserted by the executed local script.

**Reproducer:** [Python standard-library single-file SFT](../agents/agent34/k02_k05_xorshift128_compact_sft.py), committed and read back from GitHub. Unlike the larger exploratory local implementation, this portable version stores the two original selected source-byte constants after cryptographically pinning the original telemetry and recorder files; the independently established official selection logic is documented above and in the original recovery-routing sheet. The two implementations agreed on all summary counts.

## Significance and next action

The source's **13-second event separation** is not evidence of a shared compact-state output stream. This new explicit source-to-source test falsifies the simplest Marsaglia xorshift128 common producer under both plausible K02 packetizations and bounded K05 gaps. It is separate from the K02→K05 shared *printer-MT* stage falsifier ([related new test](h17-k04-k02-k05-cotemporal-stage-falsifier-20261104.md)), which imposes an entirely different high-dimensional source history at hypothetical future stages1178/1405.

A successful producer would need to explain the distinct types and versions of the original records, predict a held-out genuinely selected source before being used as a K04 coupon mechanism, and bridge the selected 18:02 RECOVER ACK2 physical print. No such bridge has been found. The original REC8 six-slot PASS, K04/K08 MISSING and combined INCOMPLETE status remains unchanged.
