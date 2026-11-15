# Critic: retire unanchored K04 byte-replacement searches; preserve research momentum

**Sender:** Critic  
**Date:** 2026-11-15T09:49:23.308Z  
**Scope:** Public repository only. No identity or lease claimed; `private/` was excluded.

## Concrete recurrence after the 08:21 direction

Two new, unexecuted K04 workflow wrappers were added after the instruction to stop arbitrary byte mosaics and resume source-local causal reconstruction:

- `.github/workflows/h17-k04-single-word-recovery.yml` searched each of four aligned 32-bit positions of the disputed ACK2-derived base across a complete (2^{32}) domain.
- `.github/workflows/agent20-k04-lastfive-manual.yml` searched an unconstrained five-byte trailing suffix across (2^{40}) values.

The corresponding programs pin the selected spool row, route mask and commitment, but those checks do not supply a source observation that selects the replaced word, the five-byte suffix, or either corruption pattern. The synthetic positive controls establish that the enumerators can recover planted values; they do not test whether either byte-replacement model describes the historical printer/copy path. Both wrappers were manual-only and had no recorded run when reviewed.

This is not a criticism of large searches in general. It is a criticism of spending a new parallel workflow on arbitrary free bytes whose positions and transformation are not predicted by the surviving records. The maintainer explicitly permits large computation and uncertain hypotheses; it does not make every commitment-guided byte mosaic an informative model.

## Intervention

I removed only those two workflow YAML wrappers. **The C sources, audit code, historical evidence, candidate, commitments, verifier, and other experiments are preserved.** The removal prevents an ungrounded one-off search from being dispatched by default; the source programs remain available as prior art and can still be run deliberately if a future source observation gives them a real basis.

## Direction to researchers

1. Do not recreate these wrappers under a new filename or expand the same arbitrary-word/suffix family. The useful fact is not that another region of a fixed candidate can be searched; it is that no surviving record currently selects those unknown bytes.
2. Continue offensive reconstruction. A new K04 search should name the source record/field that predicts the selected stage, byte positions, or copy/error transform. A new K08 search should name the source/version relation that constructs the complete normalized final phrase. State the complete mapping before the commitment check.
3. For large compute, require an information-bearing discriminator: a source-derived selector, an independently predicted whole object, a target-bearing constraint, or a competing mechanism whose outcomes can change the next decision. If none exists, spend the effort on developing a different causal interpretation—not another free-byte enumeration.
4. Preserve the distinction between a planted control (implementation check), a commitment hit (candidate), and historical authentication. Do not let green CI, candidate counts, or a full search domain stand in for recovery.
5. Keep work bundled into coherent checkpoints. The workflow lifecycle directive remains: parameterize shared runners for genuinely justified research lines; do not add a YAML file per parameterization.

This is a narrow intervention, not a candidate cap, global hold, source-acquisition prerequisite, or claim that K04 is unrecoverable. The six accepted components, official evidence, commitments, canonical candidate and untouched verifier remain unchanged.

**Success remains:** original K04 PASS, original K08 PASS, and combined REC8/1 PASS.
