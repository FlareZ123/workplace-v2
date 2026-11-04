# K04: source-model alignment follows competing records more strongly than accepted records

**Agent 6 | 4 November 2026.** New exact two-control cross-carrier match, and a caution about claiming recovered selected objects from the large p951 MT19937 printer-source fit. This uses the original intact printer rows only; the printer ACK2 selected packet, K04 mask, all target commitments and verifier are excluded from the fit.

## New RC-17 printer-source relation

Read the original twelve footer strips for RC-17 revisions B (withdrawn), C (approved), D-draft (unissued). Original RC-17 file SHA256 `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d`. The printer source is the existing 132-intact-row hypothetical native p951 basis of rank 15,365, printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Scan every native source stage -1100..1040, both byte orders, for individual RC-17 strip words agreeing with at least 13 independently source-fixed tempered bits.

**Exactly two original strips match, and they occupy adjacent generator stages:**

| RC-17 | Strip as printed | Native source stage | Known matching bits | Accepted K06? |
| --- | --- | ---: | ---: | --- |
| Withdrawn revision B / VERIFY | `C130C9BB` | **-186** | **32 / 32** (little endian) | No |
| Withdrawn revision B / PURGE | `759E0027` | **-185** | **26 / 32** (little endian) | No |

Every one of the four approved C strips, the remaining two B strips and all four D-draft strips has **zero** 13+-bit exact matches under the same stage/byte-order scan. The accepted K06 component is exactly the four approved C strips in service order: `5DBF40EE52FAAED9A536D3326CF0D95A`. The two genuine B-source matches add **one independent GF(2) state bit** to the printer-only basis (rank 15,365→15,366); four missing K04 selected native words at stage951..954 remain **128/128 free**.

The 32-bit B VERIFY source agreement is a strong source-level cross-file discriminator within this specific model; it does not validate the producer's actual historical implementation. The model/position family was explored after observing original printer data, and these strips are from an independently supplied source file.

[Reproducible SHA-pinned read-only SFT](../agents/agent6/k04_k06_rc17_prng_selector_sft.py).

## Combining the new K06 result with distinct original K05 and K07 selection controls

The earlier [node49 12-stage lattice](h17-k04-node49-interleaved-latch-lattice-20261104.md) exhibits **eight** exact printer-source matches among seq200/900/990 candidate controls at stages -324..-313. Yet the immutable K05 selector chooses **seq300..303** (highest CRC-valid sequence in the window), which has no exact original printer-source stage with >=11 fixed bits in -1100..1040. Thus the strongest node49 alignment is also on *nonselected* K05 variants.

For the independent K07 transfer chain, the prior [Agent6 original AX-7778 stage holdout](h17-k04-ax-transfer-joint-stage-holdouts.md) and [Agent6 persistent work](../agents/agent6/memory.md) establish a source-consistent high16 phase at -157..-142 for **AX-7778**, a drill, while the same consecutive-stage producer family fails source-consistent holdout constraints on later AX-7781/7782/7783. The actual K07 selection is the committed, non-dry-run **AX-7782**. This is a model-specific negative for the other transfers, with different halfword semantics from K05 and K06, not an exhaustive exclusion of all K07 source relations.

Together these three selectors give a reproducible **selected-versus-alternative asymmetry**: model-perfect or partially predictive source alignments exist in discarded revisions, old rows or drills while the correct independently accepted sources resist the tested shared-p951 producer interpretation.

The apparent stage sequence across different files also **does not respect event timestamps**: October 3 node49 records at 21:14 align to negative stage -324..-313, the much earlier issued RC-17 B strips to later stage -186/-185, and October 3 transfer drill to -157..-142, while printer packets are placed at 0..963. A single physically time-monotone printer-to-recorder RNG feed is therefore not established by these cross-file native matches. Replayed fixtures, batch generation and different stage epochs are alternate explanations.

## Decision for K04 reconstruction

The p951 original-source model is useful for diagnosing artificial/shared encoding structure, but the **actual source-object selection boundary is the central unresolved issue**. A low-rank model that matches rejected rows impressively can fail on all selected values. Before using another generator-stage prediction as the missing 18:02 ACK2 physical coupon, require an independent original selected-stage bridge or an invariant transfer/copy rule validated on intact source objects. Do not promote K04 by interpreting an unrelated matching decoy as the selected payload.

This result **does not recover K04 or K08**. Six original components pass; K04/K08 missing, combined REC8/1 INCOMPLETE. No immutable source, accepted candidate, or verifier changed.
