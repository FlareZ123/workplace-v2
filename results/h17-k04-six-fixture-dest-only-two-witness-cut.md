# K04: two intact DEST-only witnesses exclude all six conditional donor-gap timelines

**Agent 44, 1 November 2026 ~21:15 UTC. Source-model discrimination, no original selected coupon recovered.** This is a sharper, compact consequence of the **existing** v1 Agent1 source-only `CLASS/DEST` nogood test. It isolates an independent destination-only failure shared across the six p950..955 cross-source/payload-compatible MT19937 examples currently used in v2's hypothetical two-gap coupon-parity acquisition map. The new contribution is the **two-witness cover without a CLASS-sampler assumption**; the underlying six contradictions are not newly discovered raw source bytes.

## Exact source and narrow producer premise

Original `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The first 128 ordinary rows carry four opaque little-endian 32-bit payload words and an independently retained `DEST` label. The six original row-start vectors are v1 `agents/agent5/k04_crosssource_six_vectors.json`, with disputed row129 at p=950..955. Row129 and its copied ACK payload are excluded.

Consider only the previously inferred **immediate post-payload DEST sampler**: after a four-word ordinary payload the *very next* MT draw is `getrandbits(2)`; codes 0=store, 1=desk, 2=bench are accepted, 3 is rejected and the sampler continues. Under this precise premise, the **first** printed output after row r must have high two bits either its original recorded DEST code or 3. This test does **not** assume how `CLASS` is generated, nor does it assume no further draws after a rejected DEST.

Using the standard untempered MT19937 word recurrence,

```text
X[t+624] = X[t+397] XOR twist(X[t], X[t+1])
twist(a,b) = (((a & 80000000) | (b & 7FFFFFFF)) >> 1)
             XOR (9908B0DF if b is odd else 0)
```

three intact source payload words at the indicated hypothetical state positions uniquely predict each hidden **first DEST** draw. Temper and inspect the highest two printed bits.

## Two original witness triples cover all six index fixtures

| Selected p | Original intact source words (zero-indexed printer rows/words) | First hidden DEST after | Predicted entire printed word | Predicted top2 | Recorded DEST; permitted first-draw codes |
| --- | --- | --- | --- | --- | --- |
| 950, 951, 952, 953 | row27 words2,3 and row80 word0 | row110, job PS-261003-0410, 16:10 UTC | `962FDB5A` | **2** | desk; **1 or 3** |
| 954, 955 | row16 words1,2 and row70 word0 | row100, job PS-261003-0400, 15:20 UTC | `5955C8C8` | **1** | bench; **2 or 3** |

In the first case, `X[s110+4]` is at index 831 for p950/953 and 829 for p951/952. In the second, `X[s100+4]` is at 756 for p954 and 757 for p955. The printed values are exact source-word consequences of each original indexed vector, irrespective of unknown selected coupon bits. In each case the predicted top2 is **neither** the accepted recorded code **nor** the only rejection code 3. A later DEST rejection path cannot fix an **invalid first** draw.

Thus, under an immediate post-payload two-bit DEST sampler, **all six fixture chronologies are impossible independently of whether the CLASS rule holds**. The older [v1 Agent1 six-fixture CLASS source falsifier](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-crosssource-six-fixtures-class-falsifier.md) already rejects each fixture on original row84's CLASS, but that is a *separate, stronger producer-specific assumption*; removing it does not rescue these six under the DEST-only premise.

## Reusable chronology no-goods beyond these six fixtures

These are restrictions on **relative positions**, not merely on the six currently published absolute starts. Write `s[r]` for the proposed first of four MT payload outputs at original printer row r. The first witness uses row27 words2/3 at `t,t+1`, row80 word0 at `t+397`, and predicts the forbidden first post-row110 DEST draw at `t+624=s110+4`. The necessary index equalities are `s80-s27=399` and `s110-s27=622`. Therefore any future model that adopts the same immediate DEST sampler must satisfy

```text
(s80 - s27 != 399) OR (s110 - s27 != 622)
```

The second uses row16 words1/2 and row70 word0 to predict the forbidden first post-row100 DEST draw. Its necessary offsets are `s70-s16=398` and `s100-s16=621`, yielding a second reusable necessary constraint:

```text
(s70 - s16 != 398) OR (s100 - s16 != 621)
```

Among the six existing vectors, the first rule excludes p950–953; the second excludes p953–955 (the overlap p953 is harmless). These are two **source-specific conditional producer no-goods**, not absolute constraints on real printer time or a claim that another chronology passes all intact-source checks. v1 Agent1's generic nogood generator already implements the underlying three-word recurrence/metadata test; the explicit two-pair cover here packages its most concise discriminator for future index solvers.

## Method, prior art and boundaries

Read-only independent JavaScript reimplementation used GitHub's unchanged original spool bytes and original six-vector JSON through the repository connector. It parses the 132 intact 16-byte payloads into four little-endian words, inverts standard MT tempering, reconstructs all hidden first ordinary DEST/terminal CLASS words from **exact** 3-word forward or inverse recurrence witnesses, and omits selected row129 completely. Its 6 total original contradiction counts exactly reproduce v1 Agent1's earlier **5,6,10,12,5,10** totals, providing a cross-implementation consistency control. Isolating **DEST-only** yields **3,2,3,6,2,4** contradictions respectively, so the two particular forward witnesses above form a minimal two-case covering statement for this six-vector set. No K04 mask, original slot commitment, K08 nonce, candidate or verifier was read.

Nearest executable source-pinned prior: [v1 Agent1 SFT](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent1/k04_crosssource_sampler_gate_sft.py) and [hidden-selector nogood generator](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent1/k04_hidden_selector_nogood_pruner.py); they supply synthetic actual-MT sampler controls and the original full contradiction counts. Current [v2 two-gap conditional target map](h17-k04-six-model-ordinary-gap-causal-cut.md) derives useful algebra only **if** one of the six proposed producer index sequences is historically valid.

The DEST sampler is empirically source-correlated, but **the historical print firmware and exact draw order are unpreserved**. A different producer, unrelated draw before DEST, independent tail stream, or a new index vector can avoid these conditional contradictions. This result does not disprove MT19937 globally, the mathematical target-parity identities, or a future independent printer-state trace. It does demonstrate why acquiring donor bits **indexed solely to these six currently falsified examples** would be low-value without a separately authenticated producer model.

**Original REC8 state remains six verified slots; K04 physical selected coupon authentic bits 0/128; K08 final authored normalized words 0; combined INCOMPLETE.** No source or acceptance file was modified.
