# K04: complete-packet falsifier for CLASS/DEST-multiplexed xoshiro128** issuer streams

**Agent 39 | 28 November 2026 | original-source, commitment-first finite model test; no missing component recovered**

## Mechanism, not another global PRNG name sweep

The 128 ordinary print jobs have two independently retained categorical routing fields, `CLASS` and `DEST`. Earlier continuous-stream fast-PRNG tests joined **all** jobs into one hypothetical writer, possibly with constant interpacket skips. A different producer architecture could maintain **separate xoshiro128** states for each of the observed source categories; incoming jobs would advance only their own stream. This is a source-determined multiplexing hypothesis, not a claim about printer firmware. Under that premise, a retained complete packet gives four native outputs, algebraically revealing that channel's 128-bit state, and the *next packet from the same group* is a full 128-bit independently retained historical prediction.

The test freezes three channel classifiers: `CLASS` alone (3 observed groups), `DEST` alone (3), and the **ordered pair `(CLASS,DEST)`** (all 9 observed pairs). For each, test 32-bit little/big-endian native words and original/reversed four-word packet order: **12 complete models**. Each group gets an arbitrary independent 128-bit initial state; groups need not be synchronized in their global chronology. There is **zero state fitting against the selected disputed RECOVER ACK2**, no checksum-based source search, no unknown state seed dictionary, and no variable group-specific skip parameter.

The original 133-row printer reconstruction is pinned at SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Only the original first 128 ordinary records are used for group inference; the 18:01 REQUESTED1, disputed 18:02 ACK2, and 18:03 REQUESTED3 are excluded during inference. Their `CLASS=RECOVER DEST=bench` label is used only after fitting, to select the corresponding group for a complete coupon attempt.

## Exact source inversion and controls

xoshiro128** emits `rotl32(state[1]×5,7)×9 (mod 2^32)`; multiplication by 5 and 9 is invertible modulo 2^32, and rotation is invertible. Each of four consecutive original outputs therefore reveals the then-current `state[1]` exactly. The state transition is GF(2)-linear. The runner builds and exactly inverts the resulting four-observation 128×128 GF(2) map (full rank **128**) to recover a unique complete initial state from each group's **first** observed 16-byte packet. It then predicts all subsequent complete packets in the same category, never refitting on held-out packets.

A fully separate, seeded synthetic source generating **150 interleaved packets per test** from independent stream states passed every complete-packet replay for **all 12 category/serializer models**. This jointly tests output inversion, GF(2) basis reconstruction, per-group routing and packet order. No synthetic fixture contains historical source bytes.

## Original-data outcomes

| Grouping | Group count | Native serializer views | Unfitted complete packets per view | Full 16-byte source matches in all views | Original K04 commitments |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CLASS` | 3 | 4 | 125 | **0 / 500** | **0 / 4** |
| `DEST` | 3 | 4 | 125 | **0 / 500** | **0 / 4** |
| `(CLASS,DEST)` | 9 | 4 | 119 | **0 / 476** | **0 / 4** |
| **Total** |  | **12** |  | **0 / 1,476** | **0 / 12** |

The **very first** independently retained subsequent packet fails for every cohort and serializer. Neither the exact first intact PS-0417 REQUESTED1 nor its later REQUESTED3 is reproduced in any model. For an acceptance-first possibility, every fitted group state is nevertheless advanced one modeled packet for REQUESTED1; its *next* complete 16-byte packet is reduced through the **unchanged original route mask** and compared to the **full original K04 SHA-256 commitment**. No candidate matches. Those twelve target checks are conditional, not authenticated physical coupon reconstruction.

## Decision boundary

This excludes one narrowly defined **CLASS/DEST-multiplexed, uninterrupted four-output xoshiro128-starstar issuer**, not all multiplexed generators or all categorial routing relationships. A program can reset states, consume other draws between records, use longer states or different output transforms, or have a physically distinct selected-coupon copy stage. The completed model fails authentic complete-packet holdouts before any interpretation of ACK2 provenance is needed. Repeating it with extra target offsets would not address the first source failure; a future variant must propose a **source-specified skip/reset/copy relation that predicts a new intact packet**.

This does **not** recover historical K04 bytes, a final K08 wording, or another REC8/1 PASS. Existing K01/K02/K03/K05/K06/K07 remain the previously accepted six components; K04/K08 remain MISSING and combined acceptance INCOMPLETE. Original files, `candidate.json`, commitments and verifier were not changed.

## Reproducer

[`agents/agent39/k04_classdest_mux_xoshiro128ss_sft.py`](../agents/agent39/k04_classdest_mux_xoshiro128ss_sft.py): Python standard library. From repo root:

```bash
python agents/agent39/k04_classdest_mux_xoshiro128ss_sft.py
```

The default root is `resources/`; `--root <extracted-export-directory>` may be used for an authorized equivalent local export. Output is only aggregate model counters; it does **not** print original packet bytes, reconstructed states, coupon candidates, route mask, acceptance hash or source-derived output words. No public CI was run with original-source candidate values.