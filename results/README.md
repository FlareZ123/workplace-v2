# H-17 archive recovery | live decision surface

**21 November 2026, 22:08 UTC | Critic consolidation.** This entry point replaces a 69 KB accumulating experiment log. [The complete previous map is archived verbatim](DECISION_MAP_SNAPSHOT_20261121T2208Z.md). Keep substantive experimental reports intact and linked; add to this surface only when a result changes a live decision.

## Acceptance

| Status | Components |
| --- | --- |
| Original commitments **PASS** | K01, K02, K03, K05, K06, K07 |
| Original commitments **MISSING** | K04 and K08 |
| Combined REC8/1 | **INCOMPLETE** |

[Unmodified verifier](../resources/verify.py), [commitments](../resources/acceptance.json), [canonical six-pass candidate](../candidate.json), and [exact component construction/acceptance specification](h17-recovery-status.md). Do not edit these to manufacture a pass.

The [maintainer directive](../MAINTAINER_OVERRIDE.md) explicitly confirms solvability and encourages **exploratory research under uncertainty**. Unknown source provenance is not a global prohibition on new mechanisms. Keep original-commitment hits distinct from historical-source authentication.

## K04: produce and check the full selected 16-byte coupon

The incident-date route is **ESC-N / PS-261003-0417 / 18:02Z RECOVER ACK attempt 2**. The retained ACK2 payload XOR the route mask produces a rejected candidate. Dispatch ACK does not authenticate the rendered coupon. The original attempt-2 request, native output and copy/media witness are absent. [Source/attempt crosswalk](h17-k04-ps0417-crosswalk-and-attempt-boundary-20261119.md).

**Current solver decision:** the xoroshiro128++ first-pair idea is **unvalidated**, not eliminated. A prior 64-prefix audit gave 24 UNSAT, 40 UNKNOWN, zero SAT under tested constraints; recent first-pair planted inversions likewise timed out UNKNOWN, so no selected K04 coupon was emitted. These findings are *solver-observability limits*. [64-prefix original audit](h17-k04-64prefix-all-job-disposition-audit-20261121.md); [most recent execution diagnosis](../communications/broadcast/20261121T2049Z_Critic_solver-ownership-and-control-gate.md).

**21 November 22:53 UTC closure of the canonical direct-borrow solver attempt:** Agent50 integrated Agent35/Agent36's t0-only borrow inverse into the existing first-pair Z3 runner (commit [`51f6862`](https://github.com/FlareZ123/workplace-v2/commit/51f6862799c24267dd5081b8078135e9a3394330)), then fixed an off-by-one forward-output indexing defect (commit [`1968fd1`](https://github.com/FlareZ123/workplace-v2/commit/1968fd1a63e60ab6aa55f6214a7e821f0c141a11)). Pure-Python inverse identities passed 10,000 randomized 64-bit state checks and corrected outputs 0–5 matched a six-output known-state vector. The single existing [gated CI run 44958642050](https://github.com/FlareZ123/workplace-v2/actions/runs/44958642050) returned **UNKNOWN/timeout at 300.004 s on its unseeded planted positive control**, `control_pass=false`; every source-view job was skipped. **No source candidate was emitted or hashed; K04 commitment status is NOT_EVALUATED**, not MISS. The direct-borrow encoding is mathematically checked but has not demonstrated unseeded inversion liveness; close this particular fixed-budget Z3 implementation rather than increase timeouts, duplicate backends or dispatch the old 64-prefix matrix. The broader hypothesized PRNG source relation remains unproven, not experimentally falsified. Future effort needs a materially different complete-coupon source producer/copy-stage constructor or a truly new inversion mechanism with a successful unseeded planted control.

## K08: derive the exact full author-final phrase

The trimmed export does not quote Emily's final recovery-envelope inscription. Its exact normalized words are necessary for the source-defined HMAC16 derivation and original commitment. A scene description, historical slogan, locator, paraphrase, or one-word hit is insufficient. [Source-authored text/version boundary](h17-k08-source-authored-final-caption-version-path-20261119.md); [prior-art equivalence map](h17-experiment-equivalence-gate.md).

**New 21 November signal:** an exploratory union of K05–K07 source-mail authors decodes the 24 crew-note author bits as **STOW14** under the existing CREW4-style code. A separate selected-note bit extraction gives **LB10**. These are conditional, postselected **locator hypotheses**, not complete final wording or a K08 commitment hit. The STOW14 reading is consistent with MAIL-14's explicit statement that Emily's loose notes lay under signed WN-14, outside its controlled-copy sleeve. LB10 is better read as LOW BIT / N10-photo locator than a literal cell in the bookmarked `.xls`: LB is column 314, while Excel 97–2003 `.xls` is limited to 256 columns (A–IV); see [Microsoft's compatibility limits](https://support.microsoft.com/en-us/excel/worksheet-compatibility-issues). Reconsider a literal LB10 cell only if an acquired file's signature proves a newer OOXML format or a non-cell named reference. This does not replace Agent50's separate M10 hypothesis. [Original STOW14 construction and limitations](h17-k08-k05-k07-stow14-source-author-mask-20261121.md). Develop only a genuinely source-linked **whole-phrase constructor or author-final version rule** from these leads; do not multiply tail-bit/word-grammar/page-word candidates.

Potential native final-text carriers, if independently authorized, are the envelope face/margin, WN-14 loose notes and underlay with version history, or the separate photo-caption archive. The latter has a more specific locator: N14 is explicitly labelled **“Sunrise photograph”** and authored by Gabriel; N10 is Emily's reference to the photograph she revisited after the last cup. The identity between those references is plausible, not authenticated; seek the N14-associated original image plus Emily's final-caption sidecar/version record rather than treating N10 as a verified image ID. The bookmarked `mug-stock.xls` remains a separate conditional carrier with M10 as the bounded workbook candidate. PS-0323 rendered output is a candidate only with a signed envelope-to-job link.

## Shared evidence and decisive future inputs

**AX-7782 / IR-261003-H17 / Bundle06** is the selected retained incident copy. The export has only **two-byte checkpoints**, not the eight 1 MiB chunks, original directory manifest or object history. Do not assert it contains K04/K08: chronology and contents remain unknown. Preserve any independently authorized 8,388,608-byte source object and manifest unchanged; [joint read-only intake](../work/h17_ax7782_joint_intake.py) and [chronology caveat](h17-ax7782-native-copy-source-lane.md). Original native spool/job and paper-envelope/profile materials are separate conditional routes. [Precise missing-record request](h17-missing-evidence-request.md).

The custodian inquiry is closed. Do not recontact that channel, access protected R:/SharePoint, operate equipment, or alter preserved source evidence. The encrypted BX25 office PDF does not authenticate an incident-day coupon/host or Emily's text.

## Publication and experiment decision

A research checkpoint should change one of: **complete K04 bytes, complete K08 phrase, newly observed source object, mechanistic relation, or a discriminating withheld control**. State exact retained inputs, frozen transform, output, unchanged commitment result and narrow excluded domain. A synthetic PASS, UNKNOWN/timeout, locator or finished workflow is not target recovery. Use existing tested runners; batch code, controls, review and decision-changing report once. Do not turn the live map into a chronological append-only log.

For detail: [full previous map](DECISION_MAP_SNAPSHOT_20261121T2208Z.md), [19 November map snapshot](DECISION_MAP_SNAPSHOT_20261119T142355Z.md), [research reports](./), [reusable programs](../work/), [official records](../resources/).
