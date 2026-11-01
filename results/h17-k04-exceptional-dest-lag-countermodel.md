# K04: exceptional-tail DEST lag has two competing exact four-control explanations

**Agent 6, 1 November 2026. Read-only original-source countermodel.** This responds to the new v1 Agent1 [late-tail DEST-lag SFT](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent1/k04_tail_lag_sft.py), which observed four source-tail transitions whose preceding payload last-byte high two bits equal the following `DEST` code, and one disagreement on the selected 18:02 ACK. **Result: the same four tail controls admit a distinct, similarly simple producer feature that agrees with the copied selected payload. The source cannot select either historical feature. No authentic K04 target bit or component is recovered.**

## Original observations and frozen small alternative family

The unchanged original `resources/evidence/print/spool-reconstruction.log` SHA-256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Treat `DEST` labels as codes `store=0, desk=1, bench=2`. The exceptional late rows are printer record indices 128–132, with selected 18:02 incident-date ESC-N job `PS-261003-0417`, ACK attempt2, at **index129**. Prior-to-late transition 127→128 and three other intact transitions 128→129, 130→131, 131→132 are the four positive controls from Agent1. The selected **payload** is withheld while fitting all features; the following record's DEST remains visible. For orientation, the copied selected payload is not an independent coupon-integrity witness.

A natural small competitor family to the last-word-high2 hypothesis is **every two-consecutive-bit slice of every one of the 16 payload bytes**: 16 byte locations × 7 shifts = **112 complete, parameter-free feature definitions**. For a feature `(byte_index,shift)`, predict `DEST(next row) = (PAYLOAD(prev row)[byte_index] >> shift) & 3`. Require all four late controls to match exactly, and compare against original ordinary adjacent `RECOVER→RECOVER` pairs without inspecting the selected copied payload or any commitment.

## Exact source-only result

| Feature (zero-based byte, right shift) | 4/4 late controls? | Same-class ordinary controls | Copied selected row129 agrees with next DEST=2? |
| --- | --- | --- | --- |
| **(15,6)**, Agent1 last-byte high2 | Yes | **2/11** | **No**: copied code3 |
| **(6,4)**, alternate middle-byte 2-bit field | Yes | **4/11** | **Yes**: copied code2 |

Full 112-feature histogram by number of late-control matches: **0:36, 1:52, 2:18, 3:4, 4:2**. Only the two rows above fit all four controls. In the original selected copied payload `A9A9DC5731A5E2AE879C47215C2559D5`, the byte6 bit slice `(0xE2>>4)&3` is **2**, and the byte15 bit slice `(0xD5>>6)&3` is **3**. The next row130 is `DEST=bench` (code2). Thus the two control-equivalent models give **opposite selected-copy interpretations**: one flags a discrepancy and the other flags none.

The entire ordinary comparator contains **11** adjacent pairs in which both records have `CLASS=RECOVER`. Among all **34** ordinary transitions whose preceding row is `CLASS=RECOVER`, the Agent1 feature matches **5/34**; across **127** ordinary-to-ordinary boundaries it matches **36/127**. These baseline rates do not authenticate a historically distinct late-tail generator.

A source-pinned read-only [single-file test](../agents/agent6/k04_late_dest_countermodel_sft.py) implements the complete 112-feature census, asserts a synthetic bit-slice control and all original counts, and reads the suspect selected payload only **after** the two perfect features have been determined. It does **not** read the route mask, K04 acceptance or verifier, issue a target SHA candidate, launch CI or modify the originals.

## Decision and provenance limitations

- The four late positives constitute a **retrospectively noticed small pattern**. Counting 112 nearby bit-slice features makes the feature-selection multiplicity concrete; neither feature is specified as a generator/serialization operation by the original emails or routes. The eight labels and payload fragments involved have no independent line-by-line checksum from the selected physical media.
- The alternate feature is an **existence counterexample to uniqueness**, not evidence that byte6 shift4 was the actual historical producer field. Its agreement with suspect copied row129 cannot itself authenticate that row. Conversely, the Agent1 feature's disagreement does not prove the last byte was corrupted.
- Agent1's original one-bit D5→95 repair has already failed unchanged K04 SHA256; it is unnecessary to rerun that hash or expand to a repair radius. Even if an original producer later selects the last-byte feature, it would constrain at most two of 128 coupon bits, leaving the required complete original K04 unknown.
- **Next decisive observation:** an independently preserved print-stage serialization/producer definition that chooses the actual byte/shift or an independent intact late exceptional heldout, followed by a separate historically authenticated selected-byte copy/repair mechanism. More scans of bit features or randomized candidate layouts on the same four controls cannot select historical truth.

**Status:** exact original six slots still PASS; **K04 independently authenticated selected bits 0/128**, **K08 exact final-caption words zero**, combined recovery **INCOMPLETE**. This is a model-ambiguity resolution that prevents a new conditional correlation from being mistaken for recovery evidence.
