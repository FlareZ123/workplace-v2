# K04: printer job-number discontinuity imposes a native-stage consumption ceiling

**Agent 24 | 5 November 2026 | a new source-conditioned clock-model exclusion, not a recovered coupon.** The six previously accepted REC8/1 slots remain K01, K02, K03, K05, K06, K07. K04 physical coupon and K08 exact Emily caption remain missing; the original combined verifier remains INCOMPLETE.

## New question

May the printer job suffix be used as a count of every four-draw, 16-byte native MT19937 payload generation between the ordinary print cohort and the later incident jobs? This would be tempting for bridging the missing 18:02 K04 ACK2, because there are several unrepresented job numbers and the archive says missing exports are not completeness certificates.

This investigation uses an **exact source-derived *upper bound* on possible native-stage separation** to reject a strong, precisely defined version of that idea. It differs from repeating fixed p951 seed search, treating all 20 skipped IDs as real spool emissions, and merely checking the native MT recurrences again. The bound is applied to an unseen-job production hypothesis which had not been part of the source graph's old 917..971 selected-stage calculation.

## Original event facts

The unmodified `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, contains:

| Original row | UTC on 3 October 2026 | Job suffix | Attempt / state / class |
| ---: | --- | ---: | --- |
| 127 | 17:35 | **0427** | attempt1 ACK LABEL/RECOVER (original metadata supplies class) |
| 128 | 18:01 | **0417** | attempt1 REQUESTED RECOVER |
| **129** | **18:02** | **0417** | **attempt2 ACK RECOVER, selected K04; value withheld** |
| 130 | 18:03 | **0417** | attempt3 REQUESTED RECOVER |
| 131 | 18:24 | **0448** | attempt1 ACK RECOVER |
| 132 | 18:25 | **0420** | attempt2 ACK RECOVER |

**Correction of shorthand:** row127's actual class is **RECOVER**, as the source log explicitly shows; only the job number and the complete 16-byte payload matter to the bound.

There are 20 integers strictly between suffixes 0427 and 0448: **0428..0447**. Their existence as *issued physical print jobs in this time interval* is a hypothesis. The archive does not guarantee that each identifier was issued, executed, survived, or consumed one sequential PRNG block.

## Source-first calculation

Withhold the entire selected row129 payload before any native word decoding. Untemper the other 132 intact four-lane original packets to obtain **528** native 32-bit source words. Independently rediscover:

- **42** exact 31-bit source MT triple relations from [Agent13's source-unindexed precursor method](h17-k04-stagefree-31bit-hidden-predecessor-bridges-20261105.md).
- **15** exact 31-bit second-order four-sum instances, with **4** lane-reinforced groups comprising **9** identities, using [Agent1's source-unindexed second-order method](h17-k04-stagefree-secondorder-31bit-4sum-bridges-20261105.md).

Each relation provides exact native-stage differences among source packet starts; monotone packet order adds at least **four native outputs per retained 16-byte packet**. Construct a graph with equality edges in both directions and chronological lower-bound edges. Bellman-Ford shortest-path difference bounds yield:

| Packet starts | Feasible native-output stage gap, conditional on one continuous writer |
| --- | ---: |
| row127 to row131 | **16..71** |
| row128 to row131 | **12..66** |
| row128 to row130 | **8..62** |
| row127 to row128 | **4..59** |
| row128 to row132 | **16..70** |
| row0 to row132 | **929..983** |

These are **interval bounds**, derived from the source numerical identities and the chosen at-least-four-output chronology. They are not independently observed absolute printer draw positions, and feasibility of every interior integer is not asserted. The older illustrative p951 stage map has row131 minus row127 = **17**, inside the source-derived 16..71 interval; it is used only to check known relations after source discovery.

## A newly excluded complete numbering-to-draw hypothesis

Assume **all 20 intermediate suffixes 0428..0447** were emitted as distinct 16-byte coupons between the source packet starts of rows127 and131, on **the same native MT generator**, each consuming at least four fresh 32-bit outputs.

Between row127's start and row131's start there are already three observed attempts at rows128,129,130. Including the four draws of row127, the complete hypothesis demands at least

```text
4 × (row127 itself + 3 intervening observed rows + 20 presumed extra jobs)
  = 4 × 24
  = 96 native draws
```

The original source graph permits **at most 71**. Therefore this specific all-20-emitted sequential-clock explanation is **mathematically inconsistent with the 42+4 reinforced source relations**, conditional on the MT model and chronology assumptions. It cannot be used to advance or select K04's missing output stage.

A more granular capacity deduction: four observed packet transitions already consume at least **16** of the 71 possible draws, leaving at most 55 additional draws. Thus at most **13 extra complete four-draw packets** could fit; **at least seven of the 20 skipped numbers cannot correspond to extra four-draw packets in this same stream/time interval** under the stipulated model. Skipped identifiers may have been preallocated, used for jobs executed earlier or elsewhere, never emitted, or lost through an entirely different writer; the surviving export does not decide.

This does **not** reject a general MT19937 producer, prove printer job IDs correspond to consecutive generations, authenticate the copied 18:02 physical medium, or recover any selected coupon bit. It excludes only the definite extra-emission rule above. The assumption that every selected JOB/ATTEMPT must consume new outputs is itself a producer hypothesis, so the 13-packet capacity is not a literal count of vanished records.

## Reproduction and controls

[Portable repository-native SFT](../agents/agent24/k04_jobnumber_stagegap_sft.py) reads the exact original spool, omits selected row129's copied payload, imports the two independently published numerical source-discovery routines, discovers 42 triples and 4 reinforced quartet groups, and recomputes both directions of the shortest-path stage bounds. It asserts the **16..71**, **96**, and **13** figures, with a source-native p951 reference-relation control evaluated strictly after the source-first deductions.

An independently implemented local source-only reproducer against the user-supplied original ZIP yielded **42** triples, **4** reinforced groups, gap **16..71**, maximum extra **13**, and all reference-relation assertions passing. This committed shorter SFT was read back byte-for-byte from GitHub; a separate remote CI run has not been claimed. Neither original resource, mask, acceptance commitment, `candidate.json`, nor `verify.py` was changed.

## Cracking consequence

Treat recorded **packet emission** as the only permissible native clock evidence. Job-number gaps and time gaps alone cannot fill the unprinted MT words needed for an end-to-end selected 18:02 coupon. The high-value new witness remains a source-authenticated, timestamped actual producer event/draw count, untouched physical north coupon or print-media checksum, or complete independently indexed native output donor. The verified original **K04 remains 0/128 authenticated bits**; K08 remains without its exact terminal caption.
