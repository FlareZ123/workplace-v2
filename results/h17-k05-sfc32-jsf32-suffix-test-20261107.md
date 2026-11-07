# K05/PS0300–0303: bounded SFC32 and JSF32 direct-state test

**Owner:** Agent 18  
**Date:** 2026-11-07  
**Status:** bounded negative; no new component recovered  
**Reproduction:** python agents/agent18/k05_sfc32_jsf32_suffix_sft.py

## Hypothesis

The selected K05 recorder records have sequence numbers 300–303 and four 32-bit control words. The first four spool jobs are PS0300–PS0303, each with a 16-byte payload. Given the numeric suffix join, a bounded possibility is that the four K05 words are a 128-bit four-word state for a small 32-bit PRNG that emits the four printer payloads. The reverse and per-job state interpretations are also testable without inventing a seed.

## Source and implementation controls

The SFT pins the original TRP2 and spool files by SHA-256, validates TRP2 CRCs, applies the existing K05 selector (node 49, event 82, UTC window 21:14:00–21:14:08, greatest valid sequence per latch), and reads only PS0300–PS0303.

Selected controls in latch order are FF8B7820, 0A56E858, 6DCDA00E and F01E4572, all at 21:14:02 UTC with AUX 4318. The four spool payloads are PS0300 at 07:00, PS0301 at 07:05, PS0302 at 07:10 and PS0303 at 07:15 UTC. The numeric suffix match is therefore not a same-time event join.

The implementation follows the public SFC32 and JSF32 reference algorithms. Positive controls pass before source testing: SFC32 state (1,2,3,4) reproduces the five-word reference vector; JSF32 with its documented 0xF1EA5EED/zero seed state and 20 warm-ups reproduces the ten-word reference vector. The test uses the direct four-word state only, with no arbitrary seed derivation or skip search.

## Bounded tests

For SFC32 and JSF32, the SFT tests:

1. K05's four control words as the initial state, emitting 16 words compared with the four consecutive 16-byte spool payloads. Both input byte orders, forward/reversed state-word order, both output byte orders and forward/reversed output order are covered.
2. PS0300's four payload words as the initial state, emitting four words compared with the four K05 controls. The same endian and word-order variants are covered.
3. Each PS0300–PS0303 payload independently as a four-word state, emitting one word compared with its same-suffix K05 control.

## Result

No exact match. Across 32 direct K05-state interpretations, every candidate differs in all 16 compared words. Across 32 reverse PS0300-state interpretations, every candidate differs in all four control words. Across 16 per-job state interpretations, every candidate misses all four paired controls.

This excludes the direct four-word-state interpretation for these two common 128-bit PRNGs under the tested byte/word orders. It does not exclude an arbitrary transform, a separately derived seed, or a source-defined interleaving; none is justified by the current records. Do not expand this into a general PRNG sweep. The numeric suffix join remains a locator hypothesis, not evidence that the recorder and printer share a generator.

## References

- SFC32 and JSF32 implementations/reference vectors: https://github.com/bryc/code/blob/master/jshash/PRNGs.md
- Bob Jenkins JSF background and state model: https://www.pcg-random.org/posts/bob-jenkins-small-prng-passes-practrand.html

**Outcome:** no new component value recovered; K04/K08 remain unresolved.

**Confidence:** high in the bounded computational negative and source selection; low in any causal TRP2-to-spool relation.
