# K04: exhaustive seven-bit source-ACK correction shell

**Agent 15, 9 November 2026. The original K04 target has zero matches in all 94,525,795,200 complete seven-bit corrections.** The existing six recovered REC8 components remain intact. No seventh accepted component was recovered.

## Concrete target and model

The selected original route is ESC-N, PS-261003-0417, 3 October 2026 18:02 UTC, RECOVER, ACK attempt 2. The preserved spool reconstruction contains copied 16-byte payload `A9A9DC5731A5E2AE879C47215C2559D5`, whose integrity is explicitly uncertain. The unchanged routing mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives baseline K04 component `2CFF149C50E54557228E7DE60B3EB7C9`. The original acceptance commitment is SHA-256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The previously completed independent v1 [0..6-bit exhaustive test](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-bitflip-bound.md) excluded exactly 5,699,195,233 complete candidates. This experiment tests the next **entire** Hamming shell: every 128-bit correction with exactly seven changed bit positions, including arbitrarily many flips within the same bytes. XORing the recorded mask commutes with a bit correction, so the test represents complete hypothesized physical coupons under the copied-ACK/mask model.

## Original execution and controls

The [single-file C++17/OpenSSL/OpenMP search](../agents/agent15/k04_sevenbit_complete_sft.cpp) uses the original immutable 16-byte candidate and 32-byte target. It partitions combinations by their smallest bit index (0..121). Each partition enumerates the remaining six indices in ascending order and independently asserts its cardinality `C(127-low,6)`. This covers every seven-bit tuple exactly once.

A separate seven-bit planted candidate, with bit indices `121,122,123,124,125,126,127`, is independently SHA-256-hashed using OpenSSL's public SHA256 API, then searched using the same lower-level one-block SHA256 transform as the original target. This control must be found exactly once.

Executed locally against the original unchanged target on four CPU workers. Full terminal summary:

```text
START k04_exact7 expected=94525795200 threads=4 planted=2CFF149C50E54557228E7DE60B3EB737
LOW_DONE 120/122 low=121 checks=1 original_hits=0 synthetic_hits=1 elapsed=1170.3
COMPLETE checked=94525795200 expected=94525795200 original_hits=0 planted_hits=1 elapsed=1170.316
```

All **122/122** partition count checks succeeded. **94,525,795,200/94,525,795,200** full original K04 SHA256 comparisons completed with **0 hits**. The planted true SHA256 seven-bit candidate was recognized **exactly once**. Wall time was 1170.316 seconds. The 122 per-partition results are logged in the current execution archive and can be reproduced by the committed source.

## Interpretation

Under the copied selected ACK and recorded mask, the true original K04 component, if one exists, differs from that baseline by **at least eight bits**. This follows only from the finite Hamming-ball search and the target acceptance commitment, not from a validated physical error model. There is no independent attestation that the copied bytes contain the correct physical coupon with independent bit flips; large copy-stage changes, incorrect stage selection or independently generated output are unaffected.

This excludes **one genuinely new complete target candidate space** beyond the already executed v1 six-bit shell. It provides **no authenticated K04 physical coupon bits**, no K08 final words, and no combined REC8/1 acceptance. Further expansion to the eighth Hamming shell without a source-backed fault rate or independent copied/physical control is a model-prior decision, not automatic progress.