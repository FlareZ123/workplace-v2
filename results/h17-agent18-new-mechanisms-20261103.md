# H-17: six new mechanism classes and their target-facing outcomes (Agent 18, 3 November 2026)

**Status: no additional recovered REC8 component.** K01/K02/K03/K05/K06/K07 remain individually PASS. K04 and K08 remain unresolved, combined acceptance INCOMPLETE. This is a concise map of this invocation's distinct experimental contributions, for subsequent researchers to avoid repeating them.

## Genuine decision-relevant findings

The original K04 spool's 18:02 ESC-N RECOVER ACK2 **copied** opaque 16-byte payload produces a rejected component when XORed with the original 16-byte route mask. The genuine physical media content is unverified. A 256-bit acceptance commitment supplies a complete yes/no decision for a **specific finished candidate**, but not a new coupon byte if all candidates fail. The original K08 source describes the final caption's scene and editorial intention, while withholding its exact final words. Its HMAC/slot commitment similarly evaluates completed normalized phrases without revealing the wording.

Two separate mechanism families were therefore explored rather than relying on one long producer lineage:

| New model | Source/target tests actually performed | Authentic outcome | Reproducer and detailed result |
| --- | ---: | --- | --- |
| Recovered-slot-seeded CPython producer | **983,040** full K04 masked-coupon hashes, plus exact intact/copy replay | No real K04 or source hit; planted generator PASS | [SFT](../agents/agent18/k04_crossslot_seed_sft.py) |
| Selected-only UTC clock-reseeded CPython producer | **14,154,352** full K04 hashes over original day seconds and selected-event milliseconds | 0 matches; planted nonzero offset PASS | [SFT](../agents/agent18/k04_selected_clock_reseed_sft.py), [report](h17-k04-clock-reseed-selected-only-producer.md) |
| Per-print-job cross-slot HMAC-SHA256 producer | **380,160** exact intact 128bit printer replays and **2,880** complete selected K04 hashes | 0 printer and K04 matches; synthetic withheld source/coupon PASS | [SFT](../agents/agent18/k04_hmac_perjob_sft.py), [report](h17-k04-crossslot-hmac-perjob-producer.md) |
| Original LT204 all-revision MT output-stage chronology | **3,339,936** labelled source-stage assignments; **22,183** informative first-half stage/stride layouts | No ≥3 intact source halfword matches; source-derived heldout synthetic PASS | [SFT](../agents/agent18/k04_lt204_interleaved_stage_sft.py), [report](h17-k04-lt204-interleaved-32stage-geometry.md) |
| Serial 16bit additive LFSR source copier | **2,621,440** full K04 SHA256 checks | 0 matches; genuinely seeded full-coupon positive PASS | [SFT](../agents/agent18/k04_lfsr_scrambler_sft.py), [report](h17-k04-lfsr-serial-bitstream-scrambler.md) |
| Serial differential/NRZI and modular symbol codec at source, mask, reduced stages | **24,192** full K04 hashes over **7,110** distinct complete coupons | 0 original matches; nontrivial planted complete coupon positive PASS | [SFT](../agents/agent18/k04_differential_codec_sft.py), [report](h17-k04-differential-symbol-copier-channel.md) |

A seventh editorial hypothesis, short **direct-address invitation** captions from Emily's older envelope style plus her final sea/night/table cues, was checked as **254,266** normalized complete K08 HMAC+SHA256 candidates. None matched original K08; source N02 HMAC and planted full-caption positives passed. [Read-only K08 SFT](../agents/agent18/k08_direct_address_editor_sft.py).

## Why these outcomes do not license broader conclusions

- The generators above are *hypotheses* conditioned on exactly the stated seeding, message, mask, source chronology or copier transformations. The original company records do not attest any of these algorithms, seeds, polynomials or field identities as historical producer truth.
- Complete negative candidate checks are valuable for excluding the *tested* finite families. They recover **zero independently authenticated physical K04 selected bits**; posterior confidence that the retained ACK was physically right does not increase from arbitrary speculative failures.
- The LT204 test concerns whether original 16bit diagnostics can function as **independently witnessed future-source MT donor words** under a definite interleaved emitter. It uses no selected coupon bytes while fitting, and a failed donor test does not falsify unrelated true printer producers.
- The K08 phrase experiment has no authenticated final wording. A separate actual historical blind generative holdout run by Agent49 found **zero exact recalls of either labelled draft** with a frozen small language model, followed by zero original final commitment hits; see [Agent49 broadcast](../communications/broadcast/20261103T0619Z_agent49-two-nibble-mask-and-k08-historical-recall.md). Our own attempted workers-based independent holdout returned MCP 404 and is **not** a calibration success.

## Productive next discriminators

A new original printer coupon/copy-stage checksum, or an independently archived producer state/seed with trustworthy capture-event mapping, could turn the exact K04 slot hash into a genuine recovery test. Under the conditional p951 MT producer, [Agent14's constructive n613 theorem](h17-k04-p951-cpython613-any-128bit-coupon-real-seed.md) demonstrates that the 132 intact packets permit **every** missing 128bit coupon, so merely refining that same source-only long-seed model cannot select the historical one. [Agent39's seven-donor affine synthesizer](h17-k04-p951-affine-seven-donor-coupon-synthesis.md) can test an **independently indexed** target-reaching 224bit future donor if one becomes available.

For K08, the decisive missing witness is a historically attested version of Emily's exact **final margin or envelope inscription**. New human-like paraphrase grammars without a successful heldout rewrite law are low-yield; their candidate volume does not authenticate a phrase. A different and testable editorial dependency would need earlier labelled drafts as controls and must be frozen before checking original commitment.

The repo's original `resources/`, route rules, acceptance commitments, canonical `candidate.json` and `verify.py` were never edited in these experiments. Every substantive test has its own source and finite-scope report, linked above. This synthesis does not assert an accepted seventh or eighth component.
