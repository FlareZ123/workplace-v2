# K08: genuine withheld whole-caption recovery by source-conditioned 64-beam decoding

**Agent 8, 6 November 2026. Five original-archive CI jobs completed; no seventh REC8/1 PASS.** Unlike synthetic planted-positive controls or ranking an authentic known caption among 11 known decoys, this experiment requires a source-conditioned generator to emit the **exact historical whole sentence without seeing that sentence**, then tests a frozen final-version case against the original K08 commitment.

## Source and missingness mechanism

Original `resources/evidence/crew/noticeboard-and-desk-notes.txt` is SHA256-pinned to `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Genuine heldout controls N02 (first Emily crew-board draft), N06 (second Emily desk draft), N17 (older standby-envelope label), and N18 (older commissioning-envelope label) each remove **that entire source note**. Cases N17/N18 also replace their exact quoted inscriptions from MAIL11. The prompt asserts that each withheld normalized phrase is entirely absent.

Independent occurrences of shared words remain in other authentic source notes and MAIL11, MAIL12, MAIL20. This implements the 6 November Critic's corrected **missingness-matched lexical evidence** arm, which differs from Agent9's global target-word-type erasure. Case0 leaves all notes present but asks for the entirely unquoted final Emily keeper margin.

Original K08 reduction is held fixed: lowercase ASCII-alphanumeric/whitespace normalization; nonce `5F933DA6A1BD03C32DA5CBC25344F497`; `HMAC_SHA256(nonce, normalized_UTF8)[:16]`; then full SHA256 equality to original target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`. Independent original N02 HMAC16 fixture `BF889359B0303F2B2B2FD96AE841210B` matches before inference. `Qwen/Qwen2.5-0.5B-Instruct` with transformers 4.57.1 and PyTorch CPU float32 emits exactly 64 deterministic beam sequences per case (`max_new_tokens=48`), later filtered to complete 3..32-word normalized strings and deduplicated. All prompts and decoding parameters are fixed in source code, including roles.

## Completed original run

[Manual GitHub Actions run 42227234614](https://github.com/FlareZ123/workplace-v2/actions/runs/42227234614), five successful historical cases, 6 November 13:39–13:46 UTC. Original source and official commitments read-only. Reproducer [`agents/agent8/k08_missingness_matched_beam_sft.py`](../agents/agent8/k08_missingness_matched_beam_sft.py), [manual workflow](../.github/workflows/agent8-k08-missingness-beam-manual.yml).

| Entire withheld historical target | 64 emitted beams | Unique normalized complete captions | Exact genuine whole-caption rank | Original K08 hits |
| --- | ---: | ---: | --- | ---: |
| N02 first draft | 64 | 53 | **absent** | 0 |
| N06 second draft | 64 | 47 | **absent** | 0 |
| N17 standby inscription | 64 | 46 | **absent** | 0 |
| N18 commissioning inscription | 64 | 49 | **absent** | 0 |
| N23 keeper-final unquoted inscription | 64 | 48 | unknown | **0** |
| **Total** | **320** | **253 within-case distinct** | **0/4 known** | **0** |

Counts of unique captions are within each case; the 253 sum has **not** been checked for cross-case uniqueness. No hit is asserted from a successfully completed CI job alone. The original K08 commitment was actually compared for every emitted eligible complete caption.

The source-model failure is diagnostic: even when exact target lines and their quoted copies were genuinely absent, many highly ranked beams copied other complete surviving records (e.g., the full N13 sentence appears at rank 1 in the N02 task; N23's original prose is copied under other cases). The model often emits commentary *about* the lost inscription, rather than a candidate for the missing historical line. This is an observed retrieval/quotation shortcut, likely caused by leaving entire prose spans in the instruction. Larger beams of this unchanged prompt would mostly yield more source-copy artifacts.

## Consequence and next different attack

This trial provides **0/4 authentic exact-caption recovery at hit@64**, a stricter result than the previous known-decoy ranking, and supplies **48 distinct complete final K08 target attempts** whose true slot outcomes are negative. It does not exclude different language models, historically real terminal witnesses, or reconstruction from a different representation.

A worthwhile next experiment must change the **source channel or production mechanism**. In particular, strip exact preserved source sentences from prompts while keeping independently grounded individual motifs and source roles; require prospectively withheld whole-caption recovery before scaling, or search a representation that actually contains an independently preserved final quote. Exact grammar-cardinality expansion under this same copied-source prompt is disfavored.

The original six K01/K02/K03/K05/K06/K07 individual components remain accepted; K04 physical coupon and K08 final caption still unresolved; combined acceptance remains INCOMPLETE, `accepted=false`. No source, original verifier, commitment, or canonical candidate was modified.
