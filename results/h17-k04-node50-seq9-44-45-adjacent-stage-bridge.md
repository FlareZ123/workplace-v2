# K04: source-only three-recorder-stage adjacent metadata bridge (Agent28, 3 Nov 2026 UTC)

**Outcome:** New *conditional* original-source predictions under the existing p951 printer-only MT19937 model. Exact selected K04 coupon remains unrecovered; no new independently authenticated target bit. Original K08 remains unquoted.

## Method and observations

Reuse unchanged original spool, CRC-valid recorder, and Agent49's p951 printer-only symbolic GF(2) source rank **15,365**. Exclude the selected 18:02 ACK attempt2, all K04/K08 commitments, and all recorder metadata used as targets. For each of original node50 recorder sequences **9, 44, 45**, search MT native index -1100..-2 solely by comparing its original full CONTROL word against **at least 16 individually printer-fixed native bits**. Each selects exactly one original-source compatible index:

| Original seq | Control-selected native position | Additional source-predicted original fields | Independent metadata high bits checked |
|---|---:|---|---:|
| 9 | -793 | latch=1 at -794; AUX=2350 at -792 | 3 + 13 = **16** |
| 44 | -545 | event=28 at -547; latch=2 at -546; AUX=7700 at -544 | 6 + 3 + 13 = **22** |
| 45 | -540 | timestamp=`1791061742 + 217` at -543; event=26 at -542; latch=0 at -541 | 9 + 6 + 3 = **18** |
| **Total** | | | **56/56** |

The displayed source-predicted field values are **not** used to choose the CONTROL position. Each of their tempered MT high-bit outputs is completely printer-fixed in the relevant width; the observed original recorder fields agree exactly. Source files and acceptance values are read-only. This is a genuine cross-carrier *conditional source-derived match*, distinct from fitting a full selected ACK coupon or calling source key bits authenticated.

The **seq44→seq45 stage boundary** is especially coherent: MT positions -547,-546,-545,-544 contain seq44 EVENT, LATCH, CONTROL and AUX; positions -543,-542,-541,-540 then contain seq45 timestamp-code, EVENT, LATCH and CONTROL. This eight-position uninterrupted stage is a useful unit for hypothesizing producer sequence order. No assumption about seq44's own timestamp is supported by this fit. The model needs a globally consistent recorder stage/epoch and event ordering before making a claim about the selected K04 state.

## Controls and limits

Original spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, original recorder SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`. Reproducer [source-only single-file test](../agents/agent28/k04_node50_9_44_45_stage_sft.py) imports Agent49's exact p951 printer-only basis, selects positions with only CONTROL and asserts all **56 independent withheld field high bits**. It passes with the preserved original resources.

This evidence is retrospective and conditional on a hypothesized shared p951 MT producer and CPython-style rejection samplers; its eight position bridge is **not** evidence of the complete 72-record historical program. Other original source observations contradict some rigid global stage hypotheses (Agent25's seq46→47 all-epoch failure, Agent46's seq14→15 rigid-stage counterexample). For example source-fixed timestamp code -548 is 316, whereas seq44's timestamp under the seq45 epoch would require 55, so extending the displayed bridge one step earlier *without a different stage explanation fails*. Do not propagate these local matches into missing selected coupon bits.

**Next discriminant:** Freeze a shared event/latch/control/AUX order from this source-positive adjacent segment, derive a precise rule for timestamp and any extra draws using independent intact record boundaries, then predict a wholly new sequence without retrospectively fitting its control. If such a producer schedule also indexes actual target-informative state windows, combine it with the GF(2) quotient work.

No official K04/K08 verifier hit claimed. K01,K02,K03,K05,K06,K07 previously PASS; combined still INCOMPLETE.

## New three-record rejection-sampler construction (3 November, Agent28)

The previous eight-position seq44→45 bridge suggested a timestamp mismatch at MT -548. A deeper *whole-stage* interpretation resolves that specific mismatch without altering the original source: high six tempered bits of printer-fixed output -548 equal **39**, and `randrange(39)` rejects code 39. Thus -548 is a **rejected EVENT44 draw**, with the accepted original event code27 at -547.

Continue backward from the control-only seq43 anchor -552. Original source fixes high six codes **49** at -555 and **52** at -554, both rejected by `randrange(39)`. Original EVENT43 code12 can be accepted at -556, timestamp43 code9 at -557 and latch43 code1 at -553. The original seq43 AUX code5464 and seq44 timestamp code55 leave two exact five-field sampler paths:

| Branch | Seq43 AUX | Seq44 timestamp | Extra rejection before seq44 event27 |
| --- | --- | --- | --- |
| A | -551 rejected, -550 accepted | -549 accepted | -548 code39 rejected |
| B | -551 accepted | -550 accepted | -549 rejected, -548 code39 rejected |

Both then share seq44 event -547=27, latch -546=2, control -545, AUX -544=5700, and seq45 timestamp -543=217, event -542=25, latch -541=0, control -540. Both branches satisfy all original source-derived GF(2) constraints and the available rejection inequalities; no extra unobserved draws are required in the three-record segment. They remain alternatives because the printer-only source has no individually fixed output bits at -551/-550/-549.

[Branch reproducer](../agents/agent28/k04_node50_three_record_branch_sft.py) imports the original printer-only basis, selects the three control sites without metadata, constructs both exact sampler stage paths, inserts source-derived native/full and field-high-bit constraints, and tests consistency. Each branch raises rank **15,365→15,405**, i.e. **40 independent additional conditional source equations**. The selected row129 p951 residual quotient remains **128/128** under either branch. This is genuine new cross-carrier model information, still unable to recover an authentic K04 bit by itself.

The precise repair here is classification of the -548 byte pattern as a sampler rejection rather than an incorrect timestamp prediction. It strengthens the local stage mechanism. It does not resolve external epoch attribution, stage paths for the remaining 69 recorder records, nor the existing seq46→47 counterexample under its tested index assignments. Use this segment to derive a globally testable stage order with a new withheld original control prediction.

## Five-record source-stage extension: exactly nine viable histories, rank +76 (3 Nov 00:15 UTC)

A new finite-state source-only dynamic program starts after *independently indexed* seq41 CONTROL at MT -568, with its original AUX=4823 (sampler code2823). Original source fixes high13 at -567=6630, correctly **rejected** by `randrange(6000)`; high13 at -566=2823, correctly accepted. The next preserved node50 records must consume contiguous MT words through seq44 AUX at -544, with seq45 start at -543. Hold original chosen control sites seq43=-552 and seq44=-545, but use the **original** sequence42 CONTROL only for consistency at a conditionally selected position.

Within each field, permit 0..8 explicit CPython rejection-sampler draws, with fixed field order `timestamp / event / latch / control / aux` and epoch 1791061742. Exhaustive dynamic programming over that bounded window yields **exactly nine** source-only feasible complete stage histories. All nine have these *identical* positions for seq42: timestamp -565, event -564, latch -563, CONTROL **-562**, AUX -560 after a rejected AUX draw -561. Printer-only source already fixes high13 at -560 to **1986**, exactly matching original AUX42=3986. This position is chosen from source stage metadata and the outer controls; at -562 the printer-only native CONTROL mask is zero, so no independent full-control prediction is claimed.

All nine retain seq43 timestamp -559, latch -553, CONTROL -552; seq43 event accepted at -558, -557 or -556 with 4, 3 or 2 preceding/after-stage latch rejections as permitted. Seq43 AUX and seq44 timestamp have the two earlier branch alternatives, yielding the product 3×3=9 paths. Each imposes the actual selected original full seq42 CONTROL at -562, original stage codes and control words, and survives simultaneous GF(2) consistency plus every posterior rejection inequality. **Every path increases printer-only GF(2) rank 15,365→15,441 (76 independent equations), while the disputed K04 target row129 remains 128 free native directions.**

[Reproducer: exact finite-stage DP, nine histories and rank check](../agents/agent28/k04_node50_five_record_dp_sft.py). It includes an out-of-window falsifier: after original seq45 control -540, the only source-compatible seq45 AUX exits are -538,-537,-536. The same strict timestamp-first order has **zero** complete seq46 stages starting at any of these three points through index -414, even when the seq46 CONTROL index is not fixed and up to eight rejection draws per field are allowed. Thus a global strict generator/epoch hypothesis is contradicted by the original next record. The nine local positives are evidence for a bounded stage mechanism, not the historically complete producer.

This boundary should redirect work to a **new source-specific stage reordering or recorded-vs-emitted field rule** with a falsifiable heldout transition, rather than artificially filling unknown state words or treating the 76 conditional equations as an actual recovered target bit. The sixth verified components and untouched commitments remain unaffected.
