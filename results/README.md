# H-17 recovery | live decision map

*Updated 2026-11-16 09:17 UTC. This is a short decision map, not an event log. The detailed 16:11 UTC version is preserved in the [15 November decision-map archive](DECISION_MAP_ARCHIVE_THROUGH_20261115T1611Z.md); earlier chronology remains in [the pre-9-November research history](RESEARCH_HISTORY_THROUGH_20261109_0700.md).*

## Acceptance

**Six components pass:** K01, K02, K03, K05, K06 and K07. **K04 and K08 remain unresolved.** Combined REC8/1 acceptance is **INCOMPLETE**.

The [canonical candidate](../candidate.json), [unchanged acceptance commitments](../resources/acceptance.json), [source reduction summary](h17-recovery-status.md) and [official verifier](../resources/verify.py) define the acceptance boundary. A synthetic control, successful CI run, or exhausted search is not a recovered component. A commitment hit is a candidate; historical authenticity is a separate question.

## Required missing objects

| Slot | Complete object required | Unresolved relationship |
| --- | --- | --- |
| **K04** | A source-derived, accepted **16-byte component**, correctly related through the recorded route/mask to the historically selected PS-261003-0417 coupon | How the selected physical/production bytes relate to retained ACK2 dispatch bytes, including producer, copy stage and selector |
| **K08** | The accepted **16-byte HMAC-derived component** of Emily's complete, precisely normalized final envelope wording | Which author-final sentence was inscribed and which source-defined version/assembly rule produced it |

## Next research decisions

**K04 — construct the complete selected object.** Pursue a materially different deterministic producer, selector or copy-stage relation from actual available inputs. Before commitment testing, state the exact inputs, transformation, serialization, selector and all 16 output bytes. Use a meaningful historical whole-object control when one is available; its absence is not a gate for exploratory work. Do not reopen adjacent p950/p951/p952 donor, MT-offset, halfword, batch-jump or affine variants, unanchored free-byte replacement searches, or further N22-only fax-modem variants without a new observable, hardware identification or causal rule. See the [K04 recovery boundary](h17-recovery-status.md), [selected-object integrity audit](h17-ack-selector-integrity-audit.md), and [prior-art/equivalence map](h17-experiment-equivalence-gate.md).

**K08 — construct the complete final phrase.** The exact 12-word / motif-mask!=7 region of the conditional source-bigram graph is now exhaustively closed: **1,822,326,388** original-target comparisons across two disjoint shards, one in-domain synthetic positive found exactly once, and **zero original K08 hits**. See the [Agent18 shard](h17-k08-incremental-bigram-shard0-127-20261116.md) and [Agent1 shard](h17-k08-12word-mask-ne7-bigram-shard-127-331-20261116.md). Do not repeat this region. This does not constrain other lengths, masks or phrase constructions and does not authenticate the graph as Emily's authoring process. Pursue a distinct, bounded authoring, version-selection, copying or text-assembly rule that emits the full normalized phrase. N17/N18 are excluded labels; N23 refers to a margin but does not quote it. Do not extend generic paraphrase, poetry/page-word, or already-tested phrase-construction families without a new source-dated rule. The [author-final version graph](h17-k08-author-final-version-graph-20261112.md) records the current version boundary.

**Cross-slot recovery — open, but source-led.** A joint mechanism must have an independently supported relation that predicts a complete object. Prefer a withheld accepted whole component as calibration where possible. Do not turn common nonce/length coincidences into generic KDF or tag/block grids. See the [Agent6 joint-HMAC boundary assessment](../communications/agent17/20261115T220919466Z_agent6-joint-hmac-source-boundary.md).

## Bounded experiments worth reusing

These are scoped results, not global impossibility proofs:

- **K04:** [exact Romu printer-state reconstruction](h17-k04-romu-printer-exact-state-20261115.md); [all-21 direct-gap screen](h17-k04-unique-gap-source-block-pair-all-21-20261112.md); [transfer-batch projection](h17-k04-transfer-batch-jump-projection-20261112.md); [repeated-32-bit-XOR domain](h17-k04-repeated-fourbyte-xor-fullseed-20261115.md); [V.17/V.29 23-bit calling-mode scrambler](h17-k04-v17-v29-self-synchronizing-scrambler-20261116.md), [V.27ter seven-bit scrambler plus one-guard extension](h17-k04-v27ter-sevenbit-core-20261116.md), and [V.34 23-bit answer-mode scrambler](h17-k04-v34-answer-mode-scrambler-20261116.md) (all N22-only analogies; bounded exhaustive NO_MATCH, not evidence of ESC-N modem firmware). [North-ticket→PTW four-bay serial block](h17-k04-north-ticket-ptw-bay-serial-block-20261116.md) (candidate +304 locator; 28 complete constructions, no K04 hit). [Three-seam retained-fragment dislocation](h17-k04-three-seam-dislocation-20261116.md) (68.7B copied-coupon candidates, zero hits; separate route-mask branch cancelled before completion; do not resume this unanchored model).
- **K08:** [1–4-word exhaustive search](h17-k08-crew-fourword-exhaustive-20261114.md); [three-strand SCS](h17-k08-three-strand-scs-minimal-editor-20261115.md); [source-ordered maximal overlap](h17-k08-source-ordered-maximal-overlap-20261115.md); [clause-edit constructor](h17-k08-source-ordered-clause-edit-20261115.md); [complete-host Ransome scan](h17-k08-ransome-complete-host-5m-exact-span-20261115.md); [teal/blue image-bitplane intake hypothesis](h17-k08-teal-bit-image-intake-hypothesis-20261116.md) (conditional only: no target photographs are present, and ATEALBIT is not authenticated); [12-word / mask!=7 directed-bigram exhaustive shards](h17-k08-incremental-bigram-shard0-127-20261116.md) and [127..330 shard](h17-k08-12word-mask-ne7-bigram-shard-127-331-20261116.md) (1.822B comparisons, synthetic control passed, no original target hit; bounded negative only).

Do not repeat these exact inputs/rules/bounds. A genuinely different causal model remains eligible.

## Source boundary and reusable tools

The supplied export does not contain an authenticated original PS-0417 native job/coupon witness or Emily's final envelope face/margin and caption-revision history. These would be valuable passive witnesses if they arrive through an already-authorized custody transfer; they are **not prerequisites** for exploratory reconstruction from retained records. The human-custodian channel is closed. Do not reopen it, probe protected systems, or operate/alter facility equipment.

**Export coverage caveat:** `START_HERE.md` and `evidence/records-custodian.txt` characterize this bundle as a working preservation export, not the full incident record. Original mailboxes and devices are not included; quoted reply material may be omitted; and explicit gap markers are emitted only where the export tool could identify a gap. An absent marker is not a completeness certificate. Describe a record as absent from this export, not as proof it never existed or was destroyed.

**K04 profile and asset-card leads (unverified locators):** `retired-office-bookmarks.html` says BX25 scan copies travelled with an office profile refresh and points to the missing `R:\IT\desktop-move-2026.html` profile-replacement calendar. Separately, the print-fleet register explicitly maps `PS-261003-0417 → ESC-N → L-29/N → FA-17 → H17-POL-17/A3` and says the property references came from office asset cards; see the [asset-card source lead](h17-k04-office-asset-card-source-lead-20261107.md). The A3 card and September 2026 equipment-count sheet are absent from the export. This is a locator/route bridge only: it does not supply coupon bytes, prove the card contains the coupon, or establish any dated profile-refresh event or causal link to FA-17/PS-0417. The bookmark's calendar reference is an acquisition lead only; no supplied record dates the refresh or ties it to the selected job. The 16:45Z LABEL ACK and 18:02Z RECOVER ACK are different classes; WATCH-SPARE and ESC-S are different routes. No native PS-0417 `.SPL/.SHD` is present.

Existing read-only intake and test helpers are in [work/](../work/): [witness intake](../work/h17_witness_intake.py), [K04 binary-window intake](../work/h17_k04_binary_window_intake.py), [AX-7782 inventory](../work/h17_ax7782_object_intake.py), [K08 phrase scanner](../work/h17_profile_k08_phrase_scan.py), and [Sticky Notes intake](../work/h17_sticky_notes_intake.py), plus the conditional [teal/blue image-bitplane scanner](../work/h17_k08_teal_bit_image_scan.py) for an authorized original photo/profile set. Use them on new authorized bytes; do not rebuild speculative parsers or repeat source inventories.

## Execution and reporting discipline

- Check relevant current results, communications and the owning agents' memories for cross-agent overlap **before** a broad source-wide scan or expensive search. The equivalence map is useful prior art, not a substitute for checking newer work.
- Preserve one coherent report per distinct experiment. Batch corrections; do not turn every correction or synthetic control into a new result/commit.
- Classify outcomes accurately: original commitment hit; new target constraint; scoped model negative; synthetic implementation control; source/input failure; or timeout/unknown. An input failure is not a scientific negative.
- Reuse the existing parameterized CI runners. The workflow directory currently has **226 definitions**; do not add one-off wrappers. Preserve useful scripts and artifacts, and retire closed wrappers when touched rather than running another CI-count audit.
- Keep the research offensive. No source-attestation gate, arbitrary candidate cap or population-wide hold is implied.

**Success:** K04 PASS, K08 PASS, and combined REC8/1 PASS.
