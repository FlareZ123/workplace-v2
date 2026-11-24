# H-17 archive recovery | live decision map

**Updated 24 November 2026.** This is the short decision surface, not a running experiment log. Detailed reports and reusable code remain intact. The prior cumulative map remains recoverable in Git history; the previous dated snapshot is [preserved here](DECISION_MAP_SNAPSHOT_20261121T2208Z.md).

## Acceptance

| Original REC8/1 commitment | Current state |
| --- | --- |
| K01, K02, K03, K05, K06, K07 | **PASS** |
| K04, K08 | **MISSING** |
| Combined REC8/1 | **INCOMPLETE** |

The unchanged [verifier](../resources/verify.py) and [commitments](../resources/acceptance.json) are authoritative. No accepted historical K04/K08 component has been recovered.

## K04 — complete selected 16-byte coupon

The selected route is ESC-N / PS-261003-0417 / RECOVER ACK attempt 2. The retained ACK2 payload XOR the route mask fails the original K04 commitment; a dispatch ACK does not authenticate the physical coupon. The preserved PS-0417 association is to the L-29/N five-tab set, not a proven individual ticket-to-spool foreign key. PS-0420 is WATCH-SPARE, not an authenticated same-account ESC-N control.

**Unvalidated workbook hypothesis, not an authenticated join:** if the original `mug-stock.xls` is independently available, the read-only probe can test two complete 16-byte K04 constructions from the eight K01-selected cells: (1) native little-endian BIFF8 `ixfe` indexes, and (2) effective XF `icvFore`/`icvBack` 7-bit palette-index pairs. The second is Agent21's original proposal; the first is a distinct raw-field alternative raised by Agent16. Candidate bytes, raw XF payloads and the K04 mask are redacted from probe output. The original probe tests all eight cells on one worksheet; the separate four-tab A/B/C/D interpretation remains unimplemented and unverified without an authenticated worksheet mapping. No surviving WN-14 record authenticates that K01's selectors address this workbook; the bookmark is only a locator. The original workbook is absent, so neither construction is a candidate or historical recovery. Thirteen synthetic tests pass in the [focused regression run](https://github.com/FlareZ123/workplace-v2/actions/runs/45442850407). See the [source proposal](../communications/agent50/20261124T015043Z_agent21-xf-index-bitfield-serialization-precision.md), [Agent16's raw-index note](../communications/agent21/20261124T153214Z_agent16_raw-xf-index-alternative.md), [read-only probe](../work/h17_k04_mug_stock_xf_probe.py), [candidate builder](../work/h17_k04_biff8_xf_candidate.py), and [tests](../work/test_h17_k04_mug_stock_xf_probe.py).

Agent14's [bounded L-29/N four-reference screen](h17-k04-l29-four-reference-coupon-screen-20261124.md) tested three visible-row selectors (tabs 01–04; conditional 01/02/03/05; and three positive North rows plus the explicit L-29/S guide-shim credit): 477 transformations, 332 unique values, no K04 commitment hit. This closes only those ticket/reference serializations, not the missing native PrevERP transaction fields or row-status attribution.

The [retired-profile bookmarks](../resources/evidence/h17-supplemental-office-files/retired-office-bookmarks.html) name the decisive missing K04 records: `R:/Finance/PrevERP/posted-items-26.xls` and `R:/Finance/PrevERP/reversal-register.htm`. They should establish native transaction references, row status and reversal links; the visible CSV is not a substitute. The same bookmark names `R:/Stores/returns/SEP26/index.htm`, the September cassette-return index, which could identify FA-17's print technology and discriminate the spent-ribbon route. No copy of these files is in the export. AX-7782 is a profile-refresh Bundle06 object that may contain them, but its contents are not verified.

Existing native-media and fail-closed direct-intake paths are ready for genuinely authorized originals; the read-only [AX-7782 joint intake](../work/h17_ax7782_joint_intake.py) accepts the complete 8 MiB object and runs transfer, K04 and K08 intakes without modifying the source. Its synthetic controls do not recover the missing coupon. The [native intake report](h17-native-coupon-caption-recovery-20261122.md), [direct-intake report](h17-final-direct-physical-coupon-caption-acceptance-cli-20261123.md), [L-29/N ticket boundary](h17-k04-l29n-set-vs-st112-ticket-boundary-20261124.md), [conditional PrevERP transaction-status source gate](h17-k04-preverp-transaction-status-source-gate-20261124.md), and [conditional four-fresh source model](h17-k04-fourfresh-all42-fullsource-counterexample-20261123.md) state the current limits.

## K08 — complete author-final wording

The final envelope inscription attributed to Emily is unquoted in the supplied export. No complete normalized phrase has passed the original K08 HMAC/commitment. OneNote, Word-revision, native Outlook MSG/compressed-RTF, workbook/OfficeArt, photo-metadata and thumbnail-cache readers are intake capabilities, not phrase recovery without the corresponding authenticated original. The [native K04/K08 intake bridge](h17-source-native-k04-k08-intake-bridges-20261122.md) is synthetic-regression-tested; historical recovery still requires the original source. The immediate objective is a deterministic rule that fixes **all** words of the terminal authored version, or an authorized original of that version—not another partial motif or locator.

The K08 workbook selector's CLI and JSON output are redacted by default, withholding the PS-0323 selector, nonce, target digest, cell values, phrases, HMACs, component digests and comment-author identity. The exact M10 comment check remains limited to an explicit or sole worksheet; no broad comment search is performed. Raw results require explicit in-process `reveal=True` for authorized local analysis and must never be logged or published.

Relevant boundaries: [OneNote intake](h17-k08-onenote-revision-intake-20261123.md), [Word tracked-revision path](h17-k08-word-tracked-revision-copy-path-20261123.md), [M10 selector](h17-k08-m10-margin-comment-selector-20261123.md), [photo XMP/IPTC](h17-k08-original-photo-xmp-caption-metadata-20261123.md), [EXIF intake](h17-k08-native-exif-caption-intake-20261123.md), and [thumbnail-cache scan](h17-k08-profile-thumbcache-integrated-scan-20261123.md).

## Work that can change acceptance

- **K04:** Produce all 16 bytes through a deterministic source-selected relation among surviving records, or passively intake an independently authorized native PS-0417 coupon/queue/spool original. State the operands and fixed rule, emit the complete object, then check the unchanged original commitment.
- **K08:** Determine the complete author-final text through a source-authored version-selection/editing rule, or passively intake the authenticated final caption/underlay. Normalize the full wording exactly, derive the HMAC component, then check the unchanged original commitment.

The [maintainer directive](../MAINTAINER_OVERRIDE.md) explicitly permits exploratory research under uncertainty. Missing originals are not a universal prerequisite for trying a genuinely different complete-output construction.

## Closed boundaries and evidence standard

- The [six-of-eight erasure-code test](h17-six-of-eight-erasure-code-test-20261124.md) is a bounded negative for the conventional GF(256), GF(2^16), GHASH GF(2^128), and systematic P/Q/Cauchy families it enumerated. Do not repeat generic field/parity sweeps without a source-derived field, coordinate or matrix relation.
- Use the [experiment-equivalence map](h17-experiment-equivalence-gate.md) for exact tested domains. It is a collision map, not a general research-permission gate.
- Keep these states distinct: **synthetic control** (implementation behavior), **original-source prediction** (predicts a retained historical control), **original commitment hit** (complete candidate matches the commitment), and **historical recovery** (also requires a defensible source/custody link).
- When a complete candidate exists, test it directly against the unchanged original commitment. Do not substitute parser self-tests, candidate counts, workflow volume or unrelated verification matrices for a candidate-producing result.

## Preservation boundaries

- The human-custodian inquiry is closed; do not contact that custodian again.
- Do not probe protected services, operate or alter facility equipment, or modify original evidence.
- Do not change the original commitments, verifier or canonical candidate to manufacture acceptance.
- Treat actual recovery components and newly received originals as potentially sensitive. Do not copy them into public reports, commits, Actions logs, artifacts or broadcasts.

## Start here

- [Official source inventory](../resources/START_HERE.md)
- [Evidence-derived recovery status and component definitions](h17-recovery-status.md)
- [Experiment-equivalence boundaries](h17-experiment-equivalence-gate.md)
- [K04 native coupon/caption intake](h17-native-coupon-caption-recovery-20261122.md)
- [K04 fail-closed direct intake tool](../agents/agent31/h17_verified_manual_intake.py) and [its report](h17-final-direct-physical-coupon-caption-acceptance-cli-20261123.md)

Detailed reports remain the evidence archive. Change this page only when acceptance or the best next research decision changes.
