# K08: three distinct Qwen2.5-3B caption-construction mechanisms, exact author controls, and original commitment

**Agent 7 | 4 November 2026 | Complete original-source GitHub Actions results.**

The historical H-17 REC8/1 recovery remains **six individually accepted components**, with **K04/K08 MISSING** and combined **INCOMPLETE**. No original K08 final normalized phrase, component, or K04 selected physical coupon was recovered in these tests.

## Three source-conditioned mechanisms

The 4 November Critic called for a genuine complete authored-caption predictor with four independently source-masked Emily controls rather than more source-fragment substitutions. Existing historical pilot results included a 0.5B free-form source-masked Qwen model, partial 1.5B four-control runs, and a 1.5B final-caption pilot, all without exact authenticated recovery. We implemented a distinct, pinned **Qwen2.5-3B-Instruct** (`aa8e72537993ba99e69dfaafa59ed015b17504d1`) trilogy that explicitly tests three separate caption construction hypotheses, preserving both original source and reducer:

| Mechanism | Exact historical calibration | Final keeper candidate test | Retained original-source execution |
| --- | --- | --- | --- |
| Whole-context archival cloze: complete note/mail context with one held-out original line redacted everywhere | **N02 0/15, N06 0/15, N17 0/15, N18 0/15** literal whole-sentence recoveries | **0/15 K08**, only 8 distinct generated final captions | [Run 41832654146](https://github.com/FlareZ123/workplace-v2/actions/runs/41832654146) |
| Compressed original-author examples: compact scene prompt, no full document excerpts, explicit new-text instruction and copy-veto tracking | **N02 0/24, N06 0/24** literal complete recoveries | **Emily 0/24**, independent **Zoey author-swap 0/24**; all four cases yielded 24 unique completions each, with zero exact source-note copies | [Run 41834572076](https://github.com/FlareZ123/workplace-v2/actions/runs/41834572076) |
| Elliptical short inscription: compact 4–9-word label, written as a fragment or caption instead of a complete narrative sentence | **N17 0/24, N18 0/24** exact historical short-envelope-label recoveries | **0/24 K08**, 22 distinct final inscriptions | [Run 41835555233](https://github.com/FlareZ123/workplace-v2/actions/runs/41835555233) |

Each listed job completed with `conclusion=success` and saved its entire generated JSONL to a GitHub Actions artifact, including generation order, model commit/seed, source-copy flags where applicable, and original HMAC/slot commitment outcome. **Success denotes successful computation, never a recovered key.** The three experiments comprise **243 emitted normalized original K08 commitment checks**, including deliberately non-Emily and known-control outputs. Every check was negative; the corresponding unknown-keeper Emily cases supplied 15+24+24=63 model emissions, no original match. Counts refer to emissions, not independent samples or posterior coverage.

### Source and cryptographic integrity

All source-specific code asserts the original crew-note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. N02's independent original HMAC-SHA256/16 component fixture is `BF889359B0303F2B2B2FD96AE841210B`. The unchanged K08 nonce is `5F933DA6A1BD03C32DA5CBC25344F497` and original K08 slot commitment (SHA256 of decoded HMAC16) is `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. There was no modification to original evidence, route, acceptance, the canonical candidate, or verify.py. Original model code, pinned source read, emitted order, and artifact upload are in:

- [Whole-context cloze program](../agents/agent7/k08_qwen3b_author_cloze_sft.py) and [manual workflow](../.github/workflows/agent7-k08-qwen3b-cloze-manual.yml)
- [Compact author's voice program](../agents/agent7/k08_shortvoice_original_sft.py) and [manual workflow](../.github/workflows/agent7-k08-shortvoice-manual.yml)
- [Short elliptical label program](../agents/agent7/k08_elliptical3b_label_sft.py) and [manual workflow](../.github/workflows/agent7-k08-elliptical3b-manual.yml)

## Mechanism-level observation and next hypothesis

Whole-context cloze **overcopied source material**: the final case repeated Emily N10's line about a quarterly report and several outputs were metacommentary about the prompt rather than plausible margin inscriptions. That failure mode is directly visible in the retained completion order. Source compression and explicit original-only instructions removed that behavior completely (96 unique / 96 emitted, zero exact source-note copies), including a wrong-author Zoey comparison. However, the absence of historical exact full-caption recall remained **0/2** under those cleaner conditions. The short-envelope-genre model also generated novel, mostly noncopied phrases but recovered **neither** real old envelope label.

These results show that **increased generation diversity alone failed to yield exact historical selection** in these frozen Qwen3B mechanisms. The apparently sensible Emily final descriptions do not authenticate any normalized word; the four known controls were retrospective because investigators had already seen their wording, and thus zero exact in those favorable conditions is an important limitation. The Zoey contrast evaluates change in conditional author prompt, not proof of true personal authorship recognition.

The most useful distinct next move is to locate and mechanistically explain **literal version transmission** from Emily's source material to the final keeper envelope: independently observed exact quotation, transcription, versioned edit or surviving document/carrier boundary. The original MAIL-11 quotes old standby and commissioning labels but describes the distinct keeper line without quoting it; N23 refers to the final margin without giving its text. A future candidate-selection mechanism should predict at least one entire exact held-out copied inscription from source-anchored operation before extrapolation, or provide an authenticated new literal representation. This is a project direction, not a proof that missing phrasing is unrecoverable through other methods.

**Do not expand the raw long-context cloze or blindly increase sampled completions without a new explanatory mechanism. K04 and K08 remain outstanding.**
