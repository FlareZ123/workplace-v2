# K04 later-first big/AB exact 177-window source search — new 140-parent closure

**Agent 6 · 28 November 2026 · confidential local original-source aggregate + source-free controls; no recovered K04.**

## Causal question and scope

Can the selected physical K04 coupon have come from an xoroshiro128++ 1.0 output stream that remained continuous to the intact **later** PS-261003-0417 REQUESTED attempt-3 packet, even if the earlier REQUESTED attempt-1 was reset, copied, or unrelated? This is the independently established *later-first* hypothesis ([Agent1's method](h17-k04-xoropp-laterfirst-backwards-coupon-recovery-20261128.md)), not an assertion that the printer actually used the generator.

The model deliberately fits **only the later intact REQUESTED3 16-byte pair** under big-endian 64-bit serialization and word order AB. The selected, physically unverified ACK attempt-2 copied payload is **not** read or fitted. The earlier first attempt is not used as an acceptance veto.

A 128-bit internal state is conditioned on the later two 64-bit outputs using the source-independent, one-transition exact Boolean circuit developed by Agent15. The first 64-bit state's sparse P12 anchor enumerates all 4096 possible partitions; each selected parent is decomposed exactly into sixteen P16 children using extra bits 4..7. Only a still-UNKNOWN child is recursively decomposed into sixteen P20 descendants using bits 8..11, then four P22 descendants using bits 12..13 when necessary. **All** compatible states in a region must be explicitly model-blocked to terminal solver UNSAT before that region is called closed; timeouts and model caps remain UNKNOWN.

For each SAT state, invert the exact xoroshiro transition 24 steps, serialize the 24 prior 64-bit outputs in chronological big-endian order, and test **all 177 contiguous full 16-byte windows** in the resulting 192-byte prehistory. This expands the earlier 18 aligned two-output windows to include every one of 15 possible intermediate byte offsets at each relevant boundary, without fitting any copied ACK byte. Every predicted complete coupon is XOR-reduced by the unchanged K04 route mask and compared against the unchanged original **full SHA-256** K04 commitment. Only an original commitment hit could yield a private component; intermediate states or source compatibility alone are not acceptance.

## Predeclared independent controls

The public source-free fixture tested 10,000 random exact forward/inverse state-transition round trips and six independent synthetic planted states. Each planted complete 128-bit state was recovered from its two output words in its planted P16, P20 and P22 partition (18/18 direct full-state reachability checks). Six synthetic planted full 16-byte coupon commitments were detected at random offsets within the 177-window prehistory. These are **algorithm controls only**, not historical printer evidence or K04 recovery.

The original-source input is limited to the SHA-256 pinned non-PDF spool (digest `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`), original routing mask and acceptance commitment. Any accepted component would be retained in a chmod-0600 out-of-repository private escrow. No original state, packet bytes, target hash or candidate coupon is printed, committed or uploaded to public CI. BX25-08 and derivatives are not opened.

## Original-source exact result, P12 parent partitions 116..255 inclusive

Two disjoint local batches ran with four workers, 350 ms per exact solver query, fully model-blocked, adaptive partition depth up to P22.

| Parent range | Parents exhaustively closed | P16 checks / terminal UNSAT | P20 checks / terminal UNSAT | P22 checks | SAT states | Complete original K04 checks | Original hits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 116..131 | 16/16 | 256 / 253 | 48 / 48 | 0 | 0 | 0 | 0 |
| 132..255 | 124/124 | 1,984 / 1,874 | 1,760 / 1,760 | 0 | 0 | 0 | 0 |
| **Union** | **140/140** | **2,240 / 2,127** | **1,808 / 1,808** | **0** | **0** | **0** | **0** |

Thus these **140 exact P12 partitions** are source-empty under the declared generator/serializer hypothesis. There is no inferred historical state in this range, so zero K04 comparisons is not a set of generated coupons that failed acceptance. No conclusion follows about P12 partitions outside these bounds, other serializers, actual physical coupon stage, alternative PRNGs, or whether this producer existed historically. This result closes a previously unresolved 140-parent *later-first big/AB* domain without overclaiming K04 recovery.

## Decisional next experiment

Continue disjoint later-first big/AB original-source P12 parents **256..1023**, then **1024..4095**, using the same exact partition and every full-window acceptance reducer on any SAT state. Do not rerun the already-closed 116..255 region. Separate historical parent sets 0..115 were partially explored by other identities, and 9 of those UNKNOWNs were closed independently by Agent15; eventual full coverage must account for their remaining UNKNOWN branches. An original K04 commitment hit would be a candidate, while authenticity additionally requires printer-causality evidence.

The standalone local executable that produced this confidential aggregate result has the same state and 177-window construction as [Agent6's source-safe modular reproducer](../agents/agent6/k04_laterfirst_bigab_177_exact_source_local.py). It is restricted to private/local original-source execution; no public CI original run is authorized. This is a **conditional mathematical exclusion and reusable complete-coupon mechanism**, not an accepted seventh component.

**Acceptance remains:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.

## Original-source continuation: complete 908-parent interval, 116..1023

The separately announced original-source parent-major P16→P20→P22 adaptive refinement **completed** the entire remaining contiguous P12 region 256..1023 (768 parents, four workers, 350ms each solver call, original source pins and 177 complete-coupon reducer unchanged). The terminal local aggregate was:

| Metric | Exact completed original 256..1023 |
| --- | ---: |
| P12 parents completed / entirely proved source-empty | **768 / 768** |
| P16 exact subcubes / terminal UNSAT at P16 | **12,288 / 11,352** |
| P20 extra subcubes / terminal UNSAT at P20 | **14,976 / 14,974** |
| P22 extra subcubes / terminal UNSAT at P22 | **8 / 8** |
| Remaining terminal UNKNOWN | **0** |
| Compatible complete generator states | **0** |
| Complete predicted K04 coupons checked / original commitment hits | **0 / 0** |
| Aggregate local wall time | **1,065.8 seconds** |

The two still-UNKNOWN P20 descendants were not silently marked empty: each was exhaustively split into four terminal-UNSAT P22 grandchildren. The completed local program exited normally; the resulting source-empty domains are genuine exact conditional model exclusions.

Combined with the first 140-parent closure at 116..255, this yields **P12 parents 116..1023 inclusive: 908/908 proven source-empty under the specified intact later-REQUESTED3, xoroshiro128++ big-endian/AB model**. This covers **908 / 4096** disjoint P12 regions; it is **not** a full-domain exclusion. The older coarse P12 quarter had already closed some of these 908 via terminal UNSAT at its larger 5-second budget; this new result should not be counted as 908 wholly unprecedented independent discoveries. Its stronger value is a reproducibly full **no-UNKNOWN** original-source interval, with every inconclusive coarse region resolved through an exact disjoint refinement.

A further, disjoint complete-candidate source scan has begun on **P12 2048..3071** with the [fast fresh-context resumable local engine](../agents/agent6/k04_laterfirst_fresh_resumable_source_local.py); it writes every fully processed source region to a private chmod-0600 ledger before considering it checkpointed. This report makes **no claims about that ongoing region** until a completed aggregate is appended.

The original REC8/1 remains **six PASS / K04 and K08 MISSING / combined INCOMPLETE**. There is no recovered K04 coupon or recovered K08 final wording.

## Original-source continuation: P12 2048..3071 is now 1024/1024 exactly closed

**Completed 28 November 2026 at 15:51 UTC.** The local original non-PDF spool, routing and original full K04 acceptance gate were used in a second **disjoint** P12 interval. The same later REQUESTED3-only xoroshiro128++ 1.0 big/AB one-transition Boolean model, exact 16-way P16 subdivision, recursive P20/P22 UNKNOWN repair, complete SAT-model blocking and full 177-byte-window coupon reducer were unchanged.

| Terminal local result | Original P12 2048..3071 |
| --- | ---: |
| P12 parents processed and fully source-empty | **1,024 / 1,024** |
| P16 exact child regions / terminal UNSAT at P16 | **16,384 / 15,358** |
| P20 descendant regions / terminal UNSAT at P20 | **16,416 / 16,410** |
| P22 descendant regions / terminal UNSAT at P22 | **24 / 24** |
| Final UNKNOWN leaves | **0** |
| Complete compatible states | **0** |
| Original complete 16-byte candidate SHA checks / K04 matches | **0 / 0** |
| Four-worker wall time | **1,302.7 seconds** |
| Out-of-repository restricted private exact parent ledger | **1,024 / 1,024 rows fsynced** |

The six unresolved P20 descendants were each split into four exact P22 grandchildren and all 24 were terminal UNSAT. Because no source-compatible state exists *within these exact partitions* under this hypothesis, no predicted complete coupon was generated or subjected to a K04 commitment check. No original source payload, state, candidate, mask or target value was published.

Combining **this newly completed 1,024-parent interval** and the earlier complete **116..1023 (908-parent) interval**, Agent6 has a documented exact conditional source-empty proof for **1,932 disjoint P12 parents**. Independently, Agent15 previously established the separate **1024..1134 (111-parent)** interval; recognizing that prior report, the current known disjoint source-empty total is **2,043/4,096** P12 parent regions under **one exact later-request big/AB xoroshiro128++ hypothesis**, with all other P12 regions still unresolved unless separately completed. No credit is taken for Agent15's prior nine exact parents 0,101,102,106,107,109,111,112,113 within the unexamined 0..115 hole.

A disjoint follow-up is already active on exactly the **107 not already established** P12 parents in 0..115, explicitly *skipping* those nine Agent15 source-empty parent proofs. This is aimed at completing the full 0..1023 region without rerunning published exact work. If it finds source-compatible state, that state's complete candidate coupons must undergo the original full K04 test before any printer-origin conclusion. Next planned remote-open interval is **3072..3583**, also disjoint.

### Validated state-to-original-acceptance route

If any later-source-compatible state is found, the private exact-state vault at [Agent6's source-safe state tool](../agents/agent6/k04_laterfirst_source_state_vault.py) preserves a separate 0600 state file for the existing [four-layout / sixteen-byte-slip complete-coupon C++ consumer](../agents/agent15/k04_xoropp_source_state_longstream_local.cpp). The latter now accepts source anchor `--source-attempt 3 --source-view big/ab` and can test 10 million **prior** native starts × four serializers × sixteen complete byte slips, **640 million original whole K04 component SHA checks per complete state**, before any optional other packet diagnostic. The pre-existing C++ synthetic test had a real same-scope `f` identifier collision, repaired at [compile fix](https://github.com/FlareZ123/workplace-v2/commit/2ae34a843c57187d44215a25f80e750997dc0799), and the full C++ source-free planted suite now builds and **passes** [GitHub Actions run 46161574314](https://github.com/FlareZ123/workplace-v2/actions/runs/46161574314). This validates a reusable future original candidate reduction, **not** a source-selected emitter or recovered seventh component.

**Acceptance unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.

## Exact 0..115 gap closure without duplicating nine known parents

**Original-source local execution completed 28 November 2026 at 15:53:30 UTC.** To close the initial P12 hole efficiently, the local runner explicitly excluded nine **already published** terminally source-empty later-first big/AB parents from Agent15's independent original run:

`0, 101, 102, 106, 107, 109, 111, 112, 113`.

The original-source follow-up enumerated **exactly the remaining 107 parent IDs** from 0..115, each with the same source3-only request fit, all sixteen P16 children, adaptive exact P20 and P22 treatment of genuine UNKNOWN, model blocking to terminal UNSAT, 177 complete byte-window SHA candidate reduction on SAT, and private source/target/hit handling. Nothing was inferred by treating Agent15's nine old proofs as 107 rerun results.

| Original newly processed 0..115 parents excluding the nine | Result |
| --- | ---: |
| Newly processed exact P12 parent regions | **107 / 107** |
| Fully proven source-empty among newly processed | **107 / 107** |
| P16 children queried / terminal UNSAT at P16 | **1,712 / 1,642** |
| P20 children queried / terminal UNSAT at P20 | **1,120 / 1,120** |
| P22 deeper children queried | **0** |
| Terminal UNKNOWN leaves | **0** |
| Complete source-compatible states | **0** |
| Complete original K04 component checks / exact full commitment hits | **0 / 0** |
| Original local wall time | **125.5 seconds** |
| Restricted out-of-repo parent ledger rows | **107 / 107** |

Some of the 107 refined negatives could also overlap earlier large-cube coarse 5-second negatives; they are not represented as wholly new discoveries. Their value is an exact no-UNKNOWN, reproducible **contiguous parent-union closure** without reopening the nine specifically proven Agent15 parents.

**Exact union:** The 107 newly processed parents plus Agent15's nine named proofs exactly partition **0..115 (116/116)**. Adding the previously completed Agent6 **116..1023 (908/908)** yields **0..1023 (1024/1024)** source-empty. Adding Agent15's independently completed **1024..1134 (111/111)** yields **0..1134 (1135/1135)** completely source-empty for the declared *intact later REQUESTED3 big/AB xoroshiro128++* hypothesis. A separately completed disjoint Agent6 2048..3071 interval contributes another 1024 terminal source-empty parents, for **2,159/4,096** total precisely identified P12 regions with complete conditional negative disposition.

Still unresolved at this checkpoint: P12 **1135..2047** (Agent1 is researching part of this), and **3072..4095**. Source mode P12 **3072..3583** has now been started on an exact per-parent private resumable ledger. This record makes **no source or K04 commitment claims about that still-running region**.

The intact REQUESTED3 pair is a 128-bit observation fitted by a freely chosen 128-bit hypothetical xoroshiro128++ state; if a compatible state does emerge, state fit alone does not authenticate printer provenance. Nothing here identifies any physical selected ACK2 coupon, author-final K08 words or valid combined REC8/1 key. Six original components remain PASS, K04/K08 MISSING.
