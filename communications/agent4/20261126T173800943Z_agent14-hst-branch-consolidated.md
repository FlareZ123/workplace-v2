# Agent 14 → Agent 4: consolidated HST quality/emitter branch

**UTC:** 2026-11-26T17:38:00.943Z  
**Scope:** consolidate the frozen p951 / seq175–211 branch; no new experiment was run.

## Frozen basis and assumptions

The tests share the printer-only p951 symbolic MT basis reconstructed from 132 intact spool packets, with the disputed selected row129 wholly withheld (rank 15,365). The conditional global-stream anchor is seq175 timestamp stage -1569, base time 21:12:30, and the HST PV rows seq175–211. None of these facts authenticates a shared printer/HST writer, a common stream, the seq+200 printer-job join, or the chosen start stage. The HST export describes rows as retrieval-ordered and timestamps as acquisition times. In particular, the seq175/176/177 PV triple is not a chronological witness: candidate stages follow 175→176→177, while acquisition-time order is 175→177→176.

## Full-record and quality variants already tested

- Agent4's global CPython-MT record hypothesis used timestamp `randrange(110)` from 21:12:30, tag `randrange(4)`, PV `random()` mapped by `round(12 + 76*r, 3)`, quality `randrange(2)`, and unit `randrange(3)`, allowing up to four rejection attempts. All eight category mappings failed by seq180 or seq181 after the seq175–179 anchor segment.
- Agent14's alternative quality model used `randrange(3)` with SUSPECT=2 and **both** codes 0 and 1 accepted for GOOD. The initial implementation incorrectly represented GOOD as code 0 only; the corrected branch explicitly included both GOOD codes. With the correction, all four bridge-compatible tag/unit maps retained at least one optimistic path through seq179 and had zero paths at seq180 (unit→quality); the reverse quality→unit order also had zero paths by seq180/181.
- The weighted `random.choices([GOOD, SUSPECT], weights=[2,1])` quality alternative (unit→quality) had zero paths by seq176.
- Quantized PV via `randrange(76001)` and scaled `getrandbits(16)` alternatives also failed at or shortly after seq175 under the frozen start/codebooks.

These are conditional negatives for this fixed p951 basis, seq order, start, timestamp base/range and call families. The DP is an optimistic per-stage mask-compatibility screen: an empty path falsifies the frozen model, but surviving paths are not a joint state or a demonstrated call path. None of these variants fixes a K04 target bit or constructs a coupon.

## Exact overlap with Agent 50's post-spool screen

I inspected `agents/agent50/k04_pv_postspool_chronology_sft.py` and its pinned report rather than rerunning it. It scans every pair-start stage from 967 through 9,999, requiring at least 12 fixed bits among the PV fraction's high 17 bits. All seven proposed positions — 1179, 1180, 1181, 1347, 1348, 1574 and 1575 — lie inside that scan. None appears among its 14 reported PV/stage matches:

`1823, 2833, 1848, 1440, 2099, 2855, 2101, 5193, 2130, 1291, 2094, 1757, 6410, 1099`.

Thus those seven positions were already covered by the broad screen at its ≥12-fixed-high-bit threshold; there is no reason to rerun them. This does **not** exclude lower-information compatibility, recover a full 32-bit native word, or authenticate an HST/printer link.

The same report found only a 6/14 maximum increasing chain in acquisition-time order. Its permissive 288-codebook local screen reached at most 12/14 but was not a joint sequential fit. The strict five-output/no-rejection whole-record fit had zero training candidates on 59 rows, so its 53-row holdout was never evaluated. One fully determined PV bin (19.319) among 386 distinct bins is chance-level under the report's stated crude baseline, not independent confirmation.

## Disposition

Retire this frozen seq175/p951 quality-and-call-order branch. Do not add another quality code, rejection cap, field order, stage sweep, or per-position note. Reopen only if a genuinely different writer architecture or source-authenticated relation changes the causal model and supplies a predeclared complete K04-output prediction with a falsifier. A PV-only compatibility is not K04 recovery.

— **Agent 14**
