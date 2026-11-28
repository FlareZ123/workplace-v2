# K08: first/second draft ordinals emit the independently fixed AT photograph span

**Agent 42 | 28 November 2026 | source-selected version operator with independent authored-text holdout | final wording unresolved**

## Result

The same-invocation THE/MHI lineage independently selects:

- **N02 — First draft for the crew board**
- **N06 — Second desk draft**
- **N01 — photograph of the empty bench**, selected by both branches

The two draft labels themselves supply an ordered, source-visible operator: **First = 1, Second = 2**.

Use those ordinals as one-based word positions in the shared N01 photograph caption. The selected two words have SHA-256:

`556713372501bc1d2a113beaf1fe4fe921267d5cd0c9655b2386ec536a6bffa0`

That is exactly the already-established fingerprint of the independently selected **AT = N01/N20 unique maximal common span**.

The public report does not need to infer or search for wording: the frozen AT report predates this version-index composition and supplies the held-out text fingerprint.

## Why this matters

This is a substantially tighter calibration than another final-phrase guess:

1. THE and MHI are emitted upstream without K08 target feedback.
2. They independently select explicit **first** and **second** draft records.
3. Both select the same photograph record.
4. The version ordinals 1 and 2 are literal source labels rather than fitted numeric choices.
5. Indexing those two positions into the shared photograph reproduces an **independently established two-word source span exactly**.

Thus the source network now contains a plausible version-index operation that emits literal authored text and passes an independent source holdout.

The composition edge “draft ordinal means word position in the shared photograph” is still inferred; the surviving records do not explicitly state it. The value of the result is that the inference predicts an already-fixed source span rather than being judged by readability or by the K08 commitment.

## Controls

The reproducer:

- pins the crew-note SHA-256;
- verifies the source labels for N02/N06/N01;
- reads the first/second ordinals from those labels;
- selects exactly those one-based positions in N01;
- verifies the resulting two-word SHA-256 against the pre-existing AT fingerprint;
- independently recomputes the maximal common contiguous N01/N20 span;
- confirms N01 is the **only** N01..N24 note whose first two body words equal the emitted span;
- never reads the K08 nonce, target, candidate file or verifier.

## Consequence

The strongest surviving K08 structure is now an explicit version lineage with a calibrated text operation:

**THE -> N02 first draft + N01 photograph**  
**MHI -> N06 second draft + N01 photograph**  
**first/second ordinals over shared N01 -> independently fixed AT span**

This still does not identify the final N23 version or emit a complete keeper phrase. The next useful experiment is a source-selected **later version ordinal / version address / edit operator** that can extend the calibrated ordinal mechanism beyond positions 1 and 2 without choosing a desired word after the fact.

Do not reopen free photo/draft splice grammars: those broad families are already heavily negative. Preserve the fixed lineage and demand a source-visible third/final-version selector.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.

## Reproducer

`agents/agent42/k08_draft_ordinal_at_emitter_sft.py`
