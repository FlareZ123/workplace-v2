# K08: N23 landmark gaps select First/Second/photo/photo, then N04's “heads twice” reaches N01

**Agent 42 | 28 November 2026 | source-only terminal-carrier structural control | exact final wording still missing**

## Result

The already-selected final-version witness N23 says, in one line, that the **wording** was in Emily's **margin**, that the **envelope** remembers the **words** she **finally** put on it.

There are now two bounded landmark paths inside that same line.

### Primary explicit-finality path

Take the five explicit final-text/carrier terms:

`wording / margin / envelope / words / finally`

Each occurs exactly once. Their one-based normalized positions are:

`2 / 5 / 12 / 16 / 18`

Count normalized words strictly **BETWEEN** adjacent landmarks:

`2 / 6 / 3 / 1`

Those note IDs are:

- **N02 — First draft for the crew board**
- **N06 — Second desk draft**
- **N03 — Kitchen photograph**
- **N01 — photograph of the empty bench**

So N23 itself directly recovers the two labelled draft stages followed by two photograph records, ending on N01, without a pronoun/coreference step.

### Secondary sentence-final coreference path

Replace the explicit finality marker with the sentence-final coreference `it`:

`wording / margin / envelope / words / it`

Positions `2 / 5 / 12 / 16 / 21` give BETWEEN counts:

`2 / 6 / 3 / 4`

or N02/N06/N03/**N04**, where N04 is **Under the old shift photograph**.

This second path is more interpretive because it uses the pronoun's envelope coreference, but it supplies an independent continuation that converges back to N01.

## The secondary N04 path supplies the next operation in plain language

The fourth record on the sentence-final-coreference path, N04, begins:

`Count the heads twice ...`

Use the already-established A1Z26 HEAD low-bit convention on the four selected record-heading heads:

`First / Second / Kitchen / Under`

Their initial parities pack first-bit-as-LSB to **14**, selecting:

**N14 — Sunrise photograph**

Apply HEAD a second time to N14's heading words `Sunrise / photograph`. Their initial parities pack to **1**, selecting:

**N01 — photograph of the empty bench**

Thus the source-local continuation is:

**N23 landmarks -> BETWEEN counts N02/N06/N03/N04 -> HEAD -> N14 -> HEAD -> N01**

No K08 nonce, acceptance target, candidate phrase or verifier is read.

## Controls and selection freedom

The strongest limitation is still landmark semantics: these are natural-language fields, not explicit machine columns. The **primary** path reduces that freedom by ending on the literal finality word `finally` rather than a pronoun. Once the landmarks are declared, every BETWEEN count is fixed.

For the primary gap vector `2/6/3/1`, exactly **five** five-position subsets of N23 share the same spacing; the declared set is the one consisting of the final-text/carrier terms `wording / margin / envelope / words / finally`.

For the secondary `2/6/3/4` vector, exactly **two** five-position subsets exist:

1. `the / my / the / the / on`;
2. `wording / margin / envelope / words / it`.

The content-word/coreference set is therefore sharply separated from the only same-spacing alternative, which is entirely function words.

As a separate source-side control, the photograph-labelled records are N01/N03/N04/N08/N14. **N01 alone** contains a tea/cup token, matching N10's explicit statement that Emily kept returning to “the photograph after the last cup.” This does not prove N01 is historically the exact image N10 meant, but it independently agrees with the two-HEAD selection.

## Consequence

This materially sharpens the terminal-carrier branch: N23 itself contains a bounded BETWEEN-count structure whose **explicit-finality path directly selects N01**, while a separate sentence-final-coreference path reaches N04 and then selects the same N01 through the literal “heads twice” instruction and N14. The two within-N23 paths converge on the same photograph antecedent.

It still does **not** emit every word of Emily's final inscription. N01's complete caption is known and does not itself pass K08; this result must therefore be treated as a source-selected antecedent/photo identity mechanism, not as recovered final wording.

A productive next step must consume this now-selected N01 antecedent with a complete source-visible authoring/version operation. Do not turn the N23 landmarks into a larger free landmark grid, vary the gap convention after seeing the target, or claim N01's literal caption as K08.

## Reproducer

`agents/agent42/k08_n23_landmark_gaps_heads_twice_sft.py`

The SFT pins the original crew-note SHA, verifies unique landmark occurrences and positions, enumerates every five-position N23 subset for the exact gap-vector denominator, reproduces both HEAD passes, checks the photograph role set and the N01 tea/cup control, and never reads K08 target material.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.
