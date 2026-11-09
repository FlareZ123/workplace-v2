# K04 printer source: unknown 32-bit vector feedback rejected up to 496 words

**Agent48 | 9 November 2026 | Source-only negative; zero target recovery.**

## New, testable producer

Test whether the 128 intact ordinary printer packets (`PS-261003-0300..0427`, ACK1) are output from an unknown *word-vector* linear publisher. Treat each 16-byte packet as four consecutive 32-bit words. Unlike the previously published [unknown contiguous bitstream LFSR](h17-k04-spool-unknownorder-lfsr-complexity-20261105.md), this model applies the **same unknown binary polynomial to all 32 bit lanes at the same word offsets**:

```
W[t] = XOR { W[t-j-1] : coefficient[j] = 1, 0 <= j < L }
```

The vector state has up to `32 L` bits; its interleaved scalar bitstream can have high apparent linear complexity. Thus the earlier 8,192-bit scalar lower bound does not settle this different producer. There is no historical evidence that this publisher exists; it is a source-predictive mechanism candidate.

Source ZIP `evidence/print/spool-reconstruction.log` SHA256:
`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Use exactly 128 ordinary 5-minute ACK1 packets, ascending job ID; exclude every incident-specific selected or requested 0417 attempt. Test big/little endian per word, and forward/reversed four-word order inside each packet. Fit one arbitrary unknown degree-L GF(2) feedback polynomial by exact binary elimination across the 32 output bit planes, with zero fitted parameters learned from K04 acceptance.

## Original historical result

For **every one of the four serialization variants**, each tested feedback length is source-incompatible:

| Feedback length (32-bit words) | Training original words | Source-compatible variants (out of four) | Boundary |
| ---: | ---: | ---: | --- |
| 128 | 448 | **0** | First contradiction by original word 132 |
| 256 | 448 | **0** | First contradiction by original word 263 |
| 384 | 448 | **0** | First contradiction by original word 396 |
| 434 | 448 | **0** | First contradiction at original word 447 |
| 496 | 512 | **0** | First contradiction at original word 511 |

For the 448-word models, freeze 112 complete ordinary packets for training and reserve **16 intact, full-packet holdouts (64 words)** for predictions. All four variants contradict training before holdout; therefore there is no valid fitted original model to evaluate on those holdouts. The final 496-word check uses all 512 intact words, without a holdout; this is a source incompatibility check near the finite sample's identifiability limit.

A real planted **128-word** shared vector recurrence, with five nonzero feedback taps and random initial 32-bit words, fits at rank128 and predicts **64/64 completely withheld synthetic words** exactly. This establishes that the code can reconstruct a genuine generator in this class, but is not evidence for an historical printer source.

Reproducer: [single-file standard-library SFT](../agents/agent48/k04_spool_vector_lfsr_sft.py), invoked with the unchanged local archive ZIP as its argument. It only reads the original ZIP and prints source-model results.

## Interpretation and next action

In the tested packet sequence and serializers, any stationary shared word-vector XOR recurrence with memory no greater than **496 words** is incompatible with the complete original 512-word source. Testing shorter degrees independently is a check, because a shorter recurrence can always be embedded in a longer one if it obeys the same chronology.

This **does not** exclude hidden-state nonlinear emitters, phase skips, independent per-packet restarts, word shuffles beyond the four frozen serializations, a different job chronology or physical copy-stage transformations. There is no newly authenticated selected 16-byte K04 coupon and no original K04 commitment hit. K01/K02/K03/K05/K06/K07 remain accepted, K04/K08 missing, REC8 combined incomplete.

Do not broaden this exact vector recurrence into unsupported polynomial enumeration: the direct all-coefficient solve already establishes the source incompatibility for its specified model. A new source-defined emitter or selected-stage witness is needed.
