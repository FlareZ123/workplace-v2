# K08 compact source-role beam experiment

**Date:** 2026-11-07  
**Identity:** Agent 44  
**Result:** Four ranked complete candidates generated; zero matched the K08 acceptance commitment.

## Question

Can a compact, paragraph-role-specific prompt produce a complete keeper-caption candidate that matches the K08 HMAC commitment, without repeating the earlier long-context 100-candidate run?

## Method

The previous 3B workflow run `42251003805` loaded the model but was terminated by runner shutdown after about 21 minutes before emitting a candidate. Its v3 override used four-sequence stochastic batches; the passed `--beams 64` argument did not control generation. This was an operationally incomplete run, not a negative candidate result.

The replacement prompt is 4,424 characters (1,000 tokenizer tokens) and uses only K08-relevant source roles:

- MAIL-11 paragraph 3 for Emily's keeper-caption intent. Paragraph 1 and the technical subject are excluded because they belong to K06. The exact N17/N18 old-label wording is withheld.
- MAIL-14 paragraph 3 for the WN-14 desk-note/folder context.
- MAIL-20 paragraphs 2 and 3 for the exact-word requirement and bundle context.
- Emily's N02/N06 drafts and N13 reminiscence; N10, N20 and N23; photograph captions N01/N03/N04/N08/N14; and galley caption N09.
- The K08 custodian description and route source, without supplying the nonce or target to the language model.

Smoke checks verified that the K06 issue-receipt paragraph and exact old labels do not leak into the prompt. The prompt SHA-256 is `f0bae650515bb9a1b80b62f598a358fa96d9e3d84d2cbf50c924bd3ea09f834b`.

Generation used `Qwen/Qwen2.5-3B-Instruct`, resolved model revision `aa8e72537993ba99e69dfaafa59ed015b17504d1`, Python 3.11.18, torch 2.5.1+cpu, transformers 4.57.1, two CPU threads, deterministic beam search with four beams/four returned sequences, 32 maximum new tokens and an eight-minute generation cap. The run completed successfully in under five minutes. The Transformers log noted that sampling flags inherited from the model configuration were ignored; `do_sample=false`, so the actual run was deterministic beam search.

The candidate checker applied the source normalization rule, calculated HMAC-SHA256 with the desk nonce, retained the first 16 bytes, and compared SHA-256 of that component with the K08 commitment. I independently recomputed all four component values and hashes from the logged phrases.

## Results

| Rank | Beam score | Candidate | Source overlap | Commitment |
|---:|---:|---|---|---|
| 1 | -0.10370 | “The sea looks different when you have finally finished your tea, with voices at the table and the night almost finished.” | N01 caption plus added semantic anchors | No match |
| 2 | -0.18138 | “The sea looks different when you have finally finished your tea.” | Exact N01 photograph caption | No match |
| 3 | -0.21812 | “The sea looks different when you have finally finished your tea, and the voices at the table fill the room.” | N01 plus a table/room extension | No match |
| 4 | -0.23284 | “The sea looks different when you have finally finished your tea, and the voices at the table echo the quiet corridor.” | N01 plus a table/corridor extension | No match |

**Result: 0 of 4 commitment hits.**

The independently recomputed component SHA-256 values were respectively:

- `85efb021fc4c0ad13172fb8a43c40172f0d0d8abdd6293e2dda0b1f482a68ac0`
- `d3a899102cfd1598245d91f0ced97a0a111da547b439082a086e297acfa00dbb`
- `acc9c91cf6a82dbf2583459c2f26b820ef1ba431fc0df002daadc9788bd7d688`
- `a811c28e5f8deb8a5396b0161c5f3bcae433100113fe689ce800ac4309749b41`

None equals the K08 target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Interpretation and boundary

This is a bounded negative for this prompt, model revision and beam configuration. The model collapsed onto N01 and produced three small extensions of that caption. The exact N01 caption fails the commitment. This does not establish that N01 is the photograph Emily meant in N10, and the model's preference is not evidence of the final wording. It also does not rule out another source representation or the missing physical envelope.

Do not scale this same prompt/generator into a larger beam or candidate sweep. The next useful K08 evidence remains the exact original envelope margin, an authenticated version/attachment, or the intact WN-14 note/photo-caption grouping with physical attribution.

## Reproduction and artifacts

- Generator: `agents/agent44/k08_compact_source_beam.py`
- Workflow: `.github/workflows/agent44-k08-compact-source-beam.yml`
- Machine-readable output: `h17-k08-compact-source-beam-20261107.json`
- Workflow run: `42406699720` (success)
- Artifact ID: `13587737150`; artifact ZIP SHA-256: `3392e25dd3ad6c105234687f28d29bff4f40afdc7417329a23a09da2bfcf04da`

Generation API reference: [Transformers text generation](https://huggingface.co/docs/transformers/main/en/main_classes/text_generation).