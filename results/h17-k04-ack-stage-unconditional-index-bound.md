# H-17 K04: source-only absolute selected-index bound (21+3 ACK graph)

**Agent 31 | 30 October 2026 | conditional mathematical finding, no recovered coupon.**

## What is genuinely new relative to prior art

[V1 Agent28's earlier 30 October work](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent28/k04_ack_stage_span_sft.py) discovered three original 31-bit reverse-word MT boundary matches and demonstrated **62 source-equation-compatible selected starts 919..980**, while explicitly fixing the example end-to-end span at `s132-s0=991`. The stronger result here is that **no arbitrary end-span assumption is needed**: the original 21 fullword plus three boundary equalities, together with four-output minimum gaps between ACK events, already impose both lower and upper endpoint and selected-index bounds.

The graph result is **unconditional only within this necessary-source-equation model**, with no assertion that a genuine MT stream reproduces all original printer payloads or that the selected coupon shares that physical stream. It is a source-to-target *index* theorem, not a recovery of its bytes.

## Original-source-only constraints and proof certificate

Pin the unchanged original `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Retain 128 ordinary ACKs and late ACK rows 131/132. Exclude REQUESTED rows 128/130 entirely from both observed payload equations and same-generator four-word ordering budgets. Treat selected ACK row 129 as a **present missing event** but never read its copied payload, route XOR mask, acceptance hash or any desired original target word.

Under the **hypothetical** reverse-4-word/little-endian MT19937 serialization, rediscover the 19 ordinary plus two late fullword identities `X[t+624] = X[t+397] XOR twist(X[t],X[t+1])`, and the three original row-start boundary identities when `X[t]` preceding a row is hidden but 31 output bits are source-observable. The three boundary triples, first reported by v1 Agent28, are:

- `(21,74,2,105,1)`
- `(22,75,2,106,2)`
- `(39,93,3,123,1)`

Each exact identity supplies a pair of row-start equalities. Keep only the **130 ACK row starts** `0..127,129,131,132`; require each successive ACK start difference to be at least four words. Encode every equality as two opposite difference-constraint edges and each ACK order requirement as one lower-bound edge. This creates a source-only integer difference graph with no fixed total-span edge.

The greatest lower bounds from three independently selected graph origins give:

| Target difference | Longest-path source-only lower bound | Reversed longest-path source-only upper bound |
| --- | ---: | ---: |
| `s132-s0` | 930 | 991 |
| `s129-s0` | 919 | 980 |

For instance, anchoring `s0=0` yields `s132>=930` and `s129>=919`; anchoring `s132=0` yields `s0>=-991` and anchoring `s129=0` yields `s0>=-980`, giving the corresponding upper bounds. Every endpoint is attainable under the graph; an **independent integer linear-programming optimization** using SciPy/HiGHS returned precisely min/max 930/991 and min/max 919/980 for these two variables, optimizing without any fixed span beyond `s0=0`.

These are **source-graph absolute bounds**, unlike the earlier 62-candidate observation conditioned on a chosen total span991. The graph itself makes 991 its maximum possible span.

## Held-observation fixed witness and MT control

A separate witness establishes that all **62** selected index values can be realized with the **same starts for every one of the 130 observed nonselected ACK rows**, not merely with separate reshufflings of intact records. Freeze a feasible vector with `s0=0, s127=915, s131=984, s132=991`. Leave all 130 observed row positions fixed and set only `s129=k` for each integer `k=919..980`. All 24 observed source equalities, every ACK gap floor and all fixed observed positions remain unchanged in each of the 62 cases.

An actual seeded CPython MT19937 **synthetic control** uses this single vector and a fixed complete generator state to generate 130 four-word intact rows. It reproduces *identical* known rows for every case but yields **62 distinct 128-bit synthetic selected-event coupons**. Thus even a perfectly reconstructed same-stream generator state cannot choose between these target coupons without a separate selected-event index/consumption witness. These synthetic coupons have no claim to be historical.

Reproducer: [one-file source-gated and synthetic-controlled certificate](../agents/agent31/k04_ack_fixed_observed_62_sft.py), relying only on the [same-directory source parser](../agents/agent31/k04_ack_chronology_sliding_certificate_sft.py) and Python standard library. Local output:

```text
SOURCE-ONLY ABSOLUTE BOUNDS: final ACK 930..991, missing ACK 919..980
TRUE-STREAM CONTROL: fixed entire MT state and 130 known outputs; 62 distinct missing-event coupons
AUGMENTED: original 21 fullword + 3 masked 31-bit constraints PASS
FIXED 130 OBSERVED ACK starts; only selected r129 changes
Selected start 919..980: 62/62 feasible; bounding ACK r127=915, r131=984
No source-to-selected producer/copy bridge and no target coupon bits recovered
```

## Scope and target action

This is **not** 62 full-MT-consistent histories of the real printer. In the fixed observed-source vector, an additional all-original fullword consistency check finds 112 contradictory recurrences among 133 geometrically forced tests, even though the selected 21 and three partial identities pass. Alternative actual source geometries or producers remain open. The intended historical printer generator, exact selected ACK2 stage, original media integrity and copied mask are not independently authenticated.

No K04 selected coupon bits have been authenticated (**0/128**). No exact final K08 keeper-caption words have been acquired. The six original completed slots stay PASS, and combined REC8 remains **INCOMPLETE**. Further source-only MT relation collection or alternate initial placements cannot replace an independently dated **ESC-N / PS-261003-0417 / 18:02 RECOVER attempt2** coupon/copy or certified event-output-index rule. The failure of a copied ACK candidate under SHA256 remains distinct from any genuine original coupon.
