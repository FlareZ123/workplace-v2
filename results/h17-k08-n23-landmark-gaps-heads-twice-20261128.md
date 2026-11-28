# K08: N23 landmark gaps select First/Second/photo/photo, then N04's “heads twice” reaches N01

**Agent 42 | 28 November 2026 | source-only terminal-carrier structural control | exact final wording still missing**

## Result

The already-selected final-version witness N23 says, in one line, that the **wording** was in Emily's **margin**, that the **envelope** remembers the **words** finally put on **it**.

Take those five text/carrier landmarks in their source order. Each occurs exactly once in N23. Their one-based normalized word positions are:

`wording=2, margin=5, envelope=12, words=16, it=21`

Apply the already-emitted `COUNT` / `BETWEEN` vocabulary literally by counting normalized words strictly between adjacent landmarks:

`2, 6, 3, 4`

Those four note IDs are:

- **N02 — First draft for the crew board**
- **N06 — Second desk draft**
- **N03 — Kitchen photograph**
- **N04 — Under the old shift photograph**

This is a compact source-local reconstruction of exactly the two editorial draft roles followed by two photograph-caption roles named by MAIL-11 as Emily's wording sources.

## N04 supplies the next operation in plain language

The fourth selected record, N04, begins:

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

The strongest limitation is the first step: choosing the semantic landmarks `wording / margin / envelope / words / it` is an interpretation of N23's grammar and coreference, not an explicit machine field. The downstream arithmetic is fixed once those landmarks are declared.

A complete positional denominator helps calibrate that choice. Among all five-position subsets of N23's 21 normalized words, exactly **two** have the same adjacent-gap vector `2/6/3/4`:

1. positions `1/4/11/15/20` = `the / my / the / the / on`;
2. positions `2/5/12/16/21` = `wording / margin / envelope / words / it`.

The latter is the only one consisting of the final-text/carrier references; the former is entirely function words.

As a separate source-side control, the photograph-labelled records are N01/N03/N04/N08/N14. **N01 alone** contains a tea/cup token, matching N10's explicit statement that Emily kept returning to “the photograph after the last cup.” This does not prove N01 is historically the exact image N10 meant, but it independently agrees with the two-HEAD selection.

## Consequence

This materially sharpens the terminal-carrier branch: N23 itself contains a bounded BETWEEN-count structure that recovers the same First-draft / Second-draft / photograph classes reached by other source programs, and its fourth output literally supplies a “heads twice” instruction that selects N01 through N14.

It still does **not** emit every word of Emily's final inscription. N01's complete caption is known and does not itself pass K08; this result must therefore be treated as a source-selected antecedent/photo identity mechanism, not as recovered final wording.

A productive next step must consume this now-selected N01 antecedent with a complete source-visible authoring/version operation. Do not turn the N23 landmarks into a larger free landmark grid, vary the gap convention after seeing the target, or claim N01's literal caption as K08.

## Reproducer

`agents/agent42/k08_n23_landmark_gaps_heads_twice_sft.py`

The SFT pins the original crew-note SHA, verifies unique landmark occurrences and positions, enumerates every five-position N23 subset for the exact gap-vector denominator, reproduces both HEAD passes, checks the photograph role set and the N01 tea/cup control, and never reads K08 target material.

K01/K02/K03/K05/K06/K07 remain accepted. K04 and K08 remain missing.
