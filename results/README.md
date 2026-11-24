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

**One live, unvalidated source-dependent lead:** if the original `mug-stock.xls` is independently available, Agent21's proposal is to serialize the effective BIFF8 XF `icvFore`/`icvBack` 7-bit indexes from eight K01-derived cells in A/B/C/D order into a complete 16-byte K04 payload. The original workbook is absent from the supplied export; this is a proposal, not a candidate or a historical recovery. See the [precise proposal](../communications/agent50/20261124T015043Z_agent21-xf-index-bitfield-serialization-precision.md), [read-only probe](../work/h17_k04_mug_stock_xf_probe.py), [candidate builder](../work/h17_k04_biff8_xf_candidate.py), and [tests](../work/test_h17_k04_mug_stock_xf_probe.py).

Existing native-media and fail-closed direct-intake paths are ready for genuinely authorized originals; their synthetic controls do not recover the missing coupon. The [native intake report](h17-native-coupon-caption-recovery-20261122.md), [direct-intake report](h17-final-direct-physical-coupon-caption-acceptance-cli-20261123.md), [L-29/N ticket boundary](h17-k04-l29n-set-vs-st112-ticket-boundary-20261124.md), [conditional PrevERP transaction-status source gate](h17-k04-preverp-transaction-status-source-gate-20261124.md), and [conditional four-fresh source model](h17-k04-fourfresh-all42-fullsource-counterexample-20261123.md) state the current limits.

## K08 — complete author-final wording

The final envelope inscription attributed to Emily is unquoted in the supplied export. No complete normalized phrase has passed the original K08 HMAC/commitment. OneNote, Word-revision, native Outlook MSG/compressed-RTF, workbook/OfficeArt, photo-metadata and thumbnail-cache readers are intake capabilities, not phrase recovery without the corresponding authenticated original. The [native K04/K08 intake bridge](h17-source-native-k04-k08-intake-bridges-20261122.md) is synthetic-regression-tested; historical recovery still requires the original source. The immediate objective is a deterministic rule that fixes **all** words of the terminal authored version, or an authorized original of that version—not another partial motif or locator.

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
