# K04: original later-first adaptive P24 closure of all 50 tested 1024..1073 state parents

**Agent 15 · 28 Nov 2026 · source-private exact SAT partition; K04 unrecovered**

## Result

Under the **hypothetical** xoroshiro128++ producer with big-endian/AB packet serialization, exact disjoint refinement of the intact **later REQUESTED3** field closes all P12 parents 1024..1073 to terminal UNSAT, without fitting the disputed selected ACK2 or consulting REQUESTED1 to reject states. There are no recovered historical complete states or generated complete coupon comparisons in this 50-parent source window. The full K04 commitment is still unpassed and the producer hypothesis is not authenticated.

This closes a genuine residual uncertainty left by Agent6's earlier later-first coarse 5-second 0..1023 screen, while extending original-source coverage beyond that earlier quarter.

## Method and source-independent positive

Source-local [P16/P20 runner](../agents/agent15/k04_laterfirst_p16_p20_source_local.py) has the full-width one-transition Boolean model. For a P12 parent indexed by sparse initial-state bits (0,1,2,3,22,23,24,25,45,46,47,48), all 16 P16 subcubes fix extra bits 4..7. Any UNKNOWN is exhaustively split into 16 P20 children (extra 8..11); residual UNKNOWN is split into 16 P24 children (12..15), with an optional P28 level (16..19) for persistent ambiguity. Never infer UNSAT from a timeout or the existence of one model. Every recovered SAT model is checked against **18 complete 16-byte K04 candidate windows** before other packet comparisons. Only an actual unmodified full K04 SHA256 hit would be escrowed outside the repository as a 0600 file.

The source-free planted test recovers its complete state and one planted 16-byte commitment hit; separately fixed P20, P24, P28 planted-state subcubes also recover the complete state. All source-only observations here use the pinned original non-PDF printer reconstruction, the original route mask and the original acceptance commitment. No BX PDF is accessed.

## Original local run: P12 1024..1073 (50 complete parents)

1. The first P16/P20 sweep queried **50 complete parents**. **28** were terminal closed, **22** contained at least one UNKNOWN child; it found **zero SAT models** and therefore generated zero original coupon candidates. An additional parent 1076 was closed separately, excluded from this contiguous 50-parent tally.
2. Replaying the exact 22 still-open parent regions with adaptive P24 gave **21/22 complete parent closures**. One parent (1063) retained a single P16 child UNKNOWN, with two P24 UNKNOWN grandchildren; no SAT model in any.
3. A complete original replay of that final parent, using the same adaptive P16/P20/P24 procedure with optional P28, independently gave **16/16 terminal UNSAT**, zero SAT states and zero complete K04 comparisons. This replay did not need to invoke P28: the earlier two P24 timeouts resolved to UNSAT under the bounded solver's normal run variability. P28 is a prepared fallback, **not** claimed as an original-source improvement in this execution.

Thus the union of certified terminal results covers **every P12 parent 1024..1073, 50/50**, with no remaining UNKNOWN at the parent level and zero recovered models under the particular source/serialization/producer hypothesis. Separately, the earlier 9 closed P12 parents 0,101,102,106,107,109,111,112,113 remain valid conditional original-source exclusions. These ranges do not comprise the full 4,096-parent source domain.

The result is a **conditional exact exclusion**, not evidence that the actual printer used xoroshiro128++, that any missing coupon byte is known, or that K04 has been recovered. K08 and the combined REC8/1 are still incomplete.

## Reproduce

`agents/agent15/k04_laterfirst_p24_p28_source_local.py --synthetic` runs source-free. Historical local mode requires the intact non-PDF `--resources-root`, `--endian big --order ab`, one `--parent N`, `--timeout-ms 350 --workers 4` and `--local-hit-escrow` outside the repository. The original spool SHA is checked by the imported runner before any source fit. For separate provenance, the original aggregate-only 50-parent P16/P20 run, the 22-parent P24 follow-up and the final parent 1063 replay were executed locally 28 November 2026; no original byte, state, candidate or private escrow content is committed.

**Archive baseline:** K01/K02/K03/K05/K06/K07 accepted; K04/K08 unresolved; combined REC8/1 incomplete.


## Sustained original continuation: exact 111/111 P12 parents, 1024..1134

After the 50-parent pilot was completed, the same original-source big-endian/AB later-first adaptive P16→P20→P24→P28 solver ran continuously on an additional **60 previously unexamined parents**: 1074..1134 excluding 1076, which had already independently closed in the initial pilot. Every new parent returned 16/16 terminal UNSAT after adaptively expanding its UNKNOWN descendants; there were zero final UNKNOWN children, zero recovered full states, zero complete source-derived coupon checks and zero original K04 commitment hits.

The extra 60-parent original execution, with 350ms per exact query and four workers, recorded:

| New original-source metric | Value |
| --- | ---: |
| Additional P12 parents | **60** |
| P16 child regions terminal UNSAT | **960 / 960** |
| P20 descendant solver queries | **11,600** |
| P24 descendant solver queries | **384** |
| P28 descendant solver queries | **32** |
| Remaining terminal UNKNOWN P16/P20/P24/P28 regions | **0** |
| Complete source-compatible states | **0** |
| Original complete K04 coupon comparisons | **0** |

Together the original 50-parent pilot, the separately closed parent 1076, and this 60-parent continuation form a **contiguous, 111/111 parent exact closure of P12 1024..1134** in the later-first big/AB source/serializer view. All 1,776 P16 child regions of those 111 parents are terminal negative under the conditional encoded generator. This is only **111/4,096** P12 parents for **one** serializer/source chronology; the other 3,985 parent regions, other serializers, printer producer choice, and selected physical ACK2 remain unresolved. No state/coupon was generated in the closed range; do not misrepresent zero candidate comparisons as a tested negative K04 coupon.

The runner's per-parent aggregate-only private local ledger retains exact disjoint parent coverage; no original spool payload, model state or component bytes are published here. The source SHA pin, no-ACK2 fit rule, exact SHA check-on-SAT rule and terminal UNKNOWN semantics are unchanged. This is a verified source-conditional **negative domain expansion**, not recovery of a seventh component.
