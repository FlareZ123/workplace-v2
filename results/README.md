# H-17 recovery — live decision map

**Updated 2026-11-19T15:52Z by Critic.** The detailed 14:23Z map is preserved verbatim in [the 19 November decision-map snapshot](DECISION_MAP_SNAPSHOT_20261119T142355Z.md). This page is the short decision surface; detailed experiments remain in their linked reports.

## Acceptance state

**REC8/1: K01, K02, K03, K05, K06 and K07 PASS; K04 and K08 unresolved; combined acceptance INCOMPLETE.** The unchanged [original verifier](../resources/verify.py), [acceptance commitments](../resources/acceptance.json), and [canonical candidate](../candidate.json) remain authoritative. Do not edit them to manufacture a pass.

The maintainer's [directive](../MAINTAINER_OVERRIDE.md) confirms solvability and permits exploratory mechanisms under uncertainty. A candidate commitment hit is valuable experimental evidence; historical authenticity is a separate question. Do not turn provenance requirements into a universal barrier to testing.

## K04 — construct the complete selected 16-byte object

**Required output:** the 16-byte component for the selected ESC-N / PS-261003-0417 attempt-2 physical coupon, using the recorded mask and selection semantics.

The retained RECOVER/ACK2 payload is dispatch evidence, not proof of the rendered or printed coupon bytes. The source-bounded 133-payload XOR screen and the direct PTW-417 serial-quartet screen are bounded no-hits; neither excludes a materially different producer-to-render/copy relation.

**Next research question:** identify a source-dependent, deterministic relation from producer through dispatch and rendered/copy stage to physical selection that emits all 16 bytes. State the changed assumption and exact source fields before compute. Do not reopen generic MT/PRNG, seed-pool, chronology-only, donor, or arbitrary copied-ACK byte-repair families without a new discriminator.

Evidence:
- [Retained-spool XOR screen](h17-k04-retained-spool-xor-screen-20261119.md)
- [PTW-417 direct serial-quartet screen](h17-k04-ptw417-serial-coupon-screen-20261119.md)
- [Metadata/MT producer portfolio](h17-k04-metadata-producer-portfolio-20261117.md)
- [Experiment equivalence gate](h17-experiment-equivalence-gate.md)

## K08 — source-authored final caption/version path

**Required output:** Emily's complete final recovery-envelope caption, normalized exactly under the [routing rule](../resources/evidence/recovery-routing.json), then checked with the original HMAC procedure.

The custodian note defines K08 as the personal caption on the recovery envelope, distinct from the commissioning and standby envelopes. MAIL-11 excludes the N17/N18 labels and says the wording was worked out from desk notes and photograph captions. N10 identifies the photograph "after the last cup"; N23 says the envelope remembers the words Emily finally put on it. The surviving notes supply context but not the final inscription.

**Current conclusion:** no source-authored operation in the supplied export emits the complete text. The defensible version-selection operation is to obtain the original N10 photograph or its native caption sidecar/catalogue record, extract its actual IPTC/XMP caption field and explicit revision/history if present, select the final saved version associated with the recovery-envelope wording, then apply the unchanged K08 normalization and HMAC. The direct authoritative alternative is the original recovery envelope or a faithful image/transcription of its handwritten caption. IPTC/XMP history is a testable hypothesis, not an assertion that such metadata exists.

**Required next input:** an independently authorized copy of the original recovery envelope (or faithful image/transcription), or the original N10 photograph plus its caption sidecar/catalogue record and revision history. Do not continue phrase grammar, note-ID locators, book scans, or workbook-coordinate branches without a new source field. Do not contact the closed custodian channel or access protected services.

Evidence:
- [Source-authored final caption/version path](h17-k08-source-authored-final-caption-version-path-20261119.md)
- [Factorized full-chain audit](h17-k08-factorized-full-chain-joint-20261119.md)
- [LOW BIT full-specificity review](h17-k08-lowbit-full-specificity-review-20261119.md)
- [Direct-adoption candidate check](h17-k08-lowbit-carrier-candidate-check-20261119.md)
- [Author-final version graph](h17-k08-author-final-version-graph-20261112.md)
- [Source-triple control](h17-k08-n20-source-triple-null-20261119.md)

## Experiment standard

A new experiment should answer, in one reproducible report:

1. **Changed assumption:** what inherited model is being challenged?
2. **Exact inputs:** which source objects, fields, roles and stages are used?
3. **Deterministic construction:** what complete 16-byte K04 value or complete normalized K08 text is emitted?
4. **Frozen choices:** what field boundaries, ordering, encodings, parser rules and normalization are fixed before checking the target?
5. **Controls:** what positive, negative, matched and (where available) held-out controls test the mechanism?
6. **Acceptance:** what does the untouched original verifier/HMAC report for every complete candidate?
7. **Interpretation:** what does the result actually exclude, and what materially different next attack does it enable?

Use one owner and a substantive adversarial reviewer where useful. Preserve all candidate outputs and control frequencies. Batch a complete experiment, independent challenge and any decision-changing synthesis update into one checkpoint. Reuse existing runners; do not create a one-off workflow for each assertion or parameter tweak.

## Custody and integrity boundary

The working export is not a completeness certificate. If an independently authorized local original is supplied, use the existing read-only intake tools. Do not repeat the closed custodian inquiry, access protected services, reconnect to protected shares, or operate or alter facility equipment. Preserve original evidence and do not change the candidate, commitments or verifier.

## Research entry points

- [Evidence-derived component definitions](h17-recovery-status.md)
- [Prior-art and experiment-equivalence index](h17-experiment-equivalence-gate.md)
- [Required evidence for the final two components](required-evidence-for-final-two.md)
- [Detailed 19 November decision-map snapshot](DECISION_MAP_SNAPSHOT_20261119T142355Z.md)
- [Maintainer directive](../MAINTAINER_OVERRIDE.md)
- [Reusable read-only intake and recovery tools](../work/)
