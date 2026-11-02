# Conditional p951 recorder AUX 13-bit next-draw side channel

**Agent 3 | 2 November 2026 ~17:57 UTC | Original-source cross-carrier positive, zero authenticated K04 bits.**

## Specific new source relationship

Agent2's recently published [p951 printer-only closure](h17-k04-p951-new-multicarrier-mt-witnesses.md) derives 968 complete and 306 partial MT19937 state words from **528 preserved ordinary/exceptional unselected printer payload words**, without reading the disputed row129 ACK2, source route mask, K04/K08 acceptance, or verifier. Original 4-byte node50 TRP2 control fields independently match eight of those 31/32-bit source state words.

This experiment tests an additional, **separately preserved original field** in those same TRP2 records: the auxiliary process reading, uint32 at offset16. The source format note calls it a raw process reading and supplies no actual RNG algorithm. An explicit, falsifiable *hypothesis* is that it was generated as `2000 + random.randrange(6000)` from the **next MT output after the control**, using CPython's genuine `getrandbits(13)` rejection sampling (codes 6000..8191 discarded). This is a historically **unauthenticated** computational model; the observed value range alone is no proof that recorder AUX was generated this way.

Each candidate is selected by a prior original **control-word match**, before looking at AUX. For each known-31-bit immediately successive state, tempering both possible missing-MSB completions reveals two candidate 13-bit codes.

| CRC-valid node50 seq | Control state index | Original AUX | Next known 13-bit possible draws | Conditional inference |
|---|---:|---:|---|---|
| 7 | -810 | 5899 | 6635 / 2281 | 6635 must reject, fixes next MSB=0; later draw unobserved |
| 12 | -775 | 7494 | 3869 / 7711 | 7711 must reject, fixes next MSB=1; later draw unobserved |
| 13 | -769 | 3201 | 5555 / **1201** | AUX=2000+1201, next MSB=1 |
| 24 | -683 | 6573 | **4573** / 223 | AUX=2000+4573, next MSB=0 |
| 25 | -677 | 6040 | 7882 / **4040** | AUX=2000+4040, next MSB=1 |
| 41 | -568 | 4823 | next fully known **6630**, rejected; following draw 6661 / **2823** | AUX=2000+2823 at second attempt, fixes second-next MSB=1 |

Two additional source-matched node50 records, seq45 and seq70, have no immediately following state word with at least 31 independently fixed bits. They are **undetermined**, not counted as passes or failures. Node49/event82 AUX values represent a different explicit recorder context and were deliberately not used to fit the node50 sampler.

The strongest exact accepted-value observations are seq13,24,25 (first candidate) and seq41 (second candidate after the original model's observed rejection). The seq7 and seq12 inferences are **partial**: the rejection is consistent, but the accepted later value is not independently predicted. Even the four exact readings were examined retrospectively; they are not truly preregistered blinded predictions. The match pattern is nevertheless a useful and unexpected second-field source discriminator.

## Consequence for conditional K04 state

The six above 31-to-32-bit completions occur at conceptual MT indices **-809, -774, -768, -682, -676, -566**. Independent exact recurrence closure after inserting only those six source-conditioned bits increases individually fixed state bits from **35,782 to 35,852**, complete 32-bit state words from **968 to 975**, and partial 32-bit state words from **306 to 302**. All original intact printer words remain consistent; there are no new source contradictions.

**Every selected K04 row129 state mask remains `00000000`** at p951 positions 951..954. Thus there is no original selected coupon bit, no recovered K04 component, no K08 exact final caption, and no new official verifier pass. The additional 70 closure-fixed bits are conditional, not 70 independent original observations.

## Important existing contradiction and limits

**This precise p951 printer index fixture already fails an original printer CLASS witness under a separately proposed ordinary-row terminal sampler**: v1 [all-six p950..955 class falsifier](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-crosssource-six-fixtures-class-falsifier.md) identifies row84's reconstructed last CLASS code3 while its recorded CLASS is LABEL code0. The new AUX agreement cannot silently remove that conflict. At least one assumed source index or one hypothesized producer/metadata rule would need revision. Preserve both as competing conditional constraints.

Prior v1 [Agent3 AUX13 investigation](https://github.com/FlareZ123/workplace-v1/blob/main/agents/agent3/k04_trp2_aux13_donor_note.md) rejected three **consecutive same-node/event** AUX runs as independent printer hidden-state donors. The within-record, control-first then rejection-sampled AUX pairing tested here is a different, tighter mechanism and does not contradict the earlier scoped negative.

### Reproduction and next discrimination

[Source-only executable](../agents/agent3/k04_aux_sampler_p951_sft.py) imports [Agent2's spool/recorder-pinned p951 closure](../agents/agent2/20261102_k04_multicarrier_p951_sft.py). It verifies native CPython `randrange(6000)` rejection behavior across 500 synthetic draws, original spool and recorder hashes and recorder CRCs, then asserts the exact source codes, six bit assignments, +70 closure bits, and zero selected-word masks. Neither source file nor official acceptance inputs are written.

The most informative future test would **independently index a currently unanchored node50 control value** (or a second AUX stage) using a heldout source emission sequence, then predict its complete original AUX field before inspecting it. A new indexed donor reaching row43→44 and row96→97 or a defensible seeded-state producer remains necessary for K04.

## Follow-up: three sequence-bounded AUX candidate positions

A separate source-only [monotone-index reproducer](../agents/agent3/k04_aux13_monotone_index_sft.py) takes the six conditional bit completions above and searches **unanchored** node50 original AUX readings between the eight independently matched control-sequence anchors. It requires at least six MT draws per successive sequence, an explicit *hypothetical* lower bound consistent with known seq12→13 and seq24→25 spacing. It further requires the candidate control position to be compatible with **at least one printer-derived state bit**, and the immediately following state to have at least 31 known bits and an accepted 13-bit process-code match.

Among 56 unanchored sequence records, the frozen source/candidate geometry yields 109 possible accepted-code positions. Three records match: **seq54 AUX=2876** at candidate state position **-459** (13-bit value876), **seq55 AUX=6663** at **-452** (value4663), and **seq63 AUX=5571** at **-397** (value3571). Each candidate's control-position state match is just **one bit**; these are therefore **candidates for new indexed anchors, not independently confirmed control-word matches**. The two nearby seq54/55 proposed controls are seven MT outputs apart. Another AUX coincidence, seq39 at -584, is rejected by the independently reconstructed **complete** corresponding control-state mismatch.

As a retrospective calibration, shuffling only the 56 original AUX labels across their fixed control/candidate sets in **100,000 seeded permutations** produced at least three coincidences in **51** trials (empirical tail frequency **0.00051**). This null is conditional on the searched p951 geometry, AUX sampler, six-draw floor, selection rules and retrospective design; it must **not** be interpreted as a historical producer-verification probability. Its positive result is a useful prioritization signal for additional source witnesses.

These three AUX-index hypotheses were inferred using their own recorded readings, so **do not reintroduce their 13-bit matches as independent new constraints in a claimed recovery**. Confirm an independently matched control word, a source-defined draw schedule or a previously uninspected field at a heldout node50 sequence before promoting them into state ancestry. Selected K04 output masks remain four zeros, and no accepted key has changed.

## Independent original EVENT and LATCH fields sharpen the record-stage model

A new [source-only event/latch SFT](../agents/agent3/k04_node50_event_latch_stage_sft.py) deliberately omits all AUX-inferred state bits. It starts solely from the p951 printer-derived output states and the originally matched node50 control positions, then tests two **other independent fields in those same original TRP2 records**. The proposed immediately pre-control generation sequence is `event=1+randrange(39)` (6-bit rejection sampler, codes 39..63 rejected), followed by `latch=randrange(4)` (3-bit rejection sampler, codes 4..7 rejected), followed by the control's full 32-bit output. Native CPython sampler synthetics pass.

- **seq24, recorder row3, control -683:** printer-only state at **-685** retempers to high6 **7**, predicting original `event=8`; at **-684** high3 **1** predicts original `latch=1`. The next control state -683 matches original four bytes `09CAAF96`. Its following AUX code at -682 is the separately reported original `6573=2000+4573`. This is a **four-field, four-consecutive-output source relationship**, conditional on generation order.
- **seq45, recorder row39, control -540:** printer-only states at **-542** and **-541** give high6 **25** and high3 **0**, exactly predicting original `event=26` and `latch=0`. The control itself matches 31 original state bits.
- **seq70, recorder row26, control -339:** output at **-341** has high6 code **57**, which would be rejected by a 0..38 event sampler; the next full output at **-340** has high3 **0**, predicting original `latch=0`. The accepted earlier event draw is not independently observed, so no exact event prediction is claimed.

These **five correct original field-value predictions plus one observed rejection** arose from independent original event/latch fields, and the original seq24 four-stage consistency is substantially more informative than an isolated AUX match. They were identified retrospectively after a p951/source review, so they remain computational evidence conditional on the MT index geometry, field-generation law and absence of extra hidden draws. They do not authenticate the physical historical producer or resolve the separately documented row84 CLASS contradiction. No target output word or official REC8 pass changes.
