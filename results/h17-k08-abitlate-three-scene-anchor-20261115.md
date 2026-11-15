# H-17 K08: A BIT LATE acrostic-anchored three-scene caption

**Agent 31, 15 November 2026.** Complete original K08 phrase assignments: **3,686,400**; original unchanged K08 matches: **zero**. This is one bounded authoring model, not a K08 reconstruction.

## Distinct causal hypothesis

The first words of N02, N06, N11, N13, N17, N18, N20 and N23 have initials `ATEALBIT`, an anagram of **A BIT LATE**. The prior [initialism screen](h17-k08-note-initialism-phrase-screen-20261114.md) tested it as an exact phrase and as constrained eight-word token selections. This test asks a different complete-phrase question: might **a bit late** have been an editorial anchor inside a longer late-watch caption incorporating Emily's explicitly requested **sea → end of night → voices at the table** order (N20)?

Predeclare the following three source-only span families from the original crew notes, preserving each span's verbatim token order: N01 contiguous 2–6 word spans containing `sea` (10); N13 contiguous 4–8 word spans containing `end of the night` (12); N20 contiguous 4–8 word spans containing `voices at the table` (15). Insert the exact newly hypothesized normalized anchor `a bit late` at one of the **four** boundaries of that three-strand sequence. At the **three** joins choose one of eight fixed source-literal connectors: empty, and, but, when, with, after, as, until. The strands remain in N20's order, without arbitrary word substitution or reordering. The resulting finite model has `10×12×15×4×8³ = 3,686,400` complete assignments; some phrase strings can coincide.

This is an exploratory, unverified editorial hypothesis, not an attested original margin. No independent final-caption holdout exists in the supplied export.

## Executed result

Read the original extracted `h17-archive-dump.zip` unmodified, with exact pinned SHA-256 values for original crew notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, recovery route `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, and acceptance commitments `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

For every complete normalized candidate, compute `SHA256(HMAC_SHA256(original_desk_nonce, UTF8(phrase))[:16])`; compare the full unchanged K08 commitment. The historical N02 draft reproduces its independent HMAC16 value `BF889359B0303F2B2B2FD96AE841210B`. An independently defined in-family planted complete caption was recovered exactly **once**. The **original** K08 commitment had **zero** matches across all 3,686,400 assignments.

Portable standard-library reproducer: [`agents/agent31/k08_abitlate_scene_join_sft.py`](../agents/agent31/k08_abitlate_scene_join_sft.py). It pins original source bytes, extracts selected numbered notes, constructs the fixed full captions, performs both controls, and reports counts and matches.

## Meaning and next decision

The entire stated *A BIT LATE + N01/N13/N20 + three fixed connectors* construction is negative. It does not exclude a longer independent final-caption phrase, another authoring rule, or a different interpretation of the note acrostic. Given previous ATEALBIT eight-word negatives and generic caption searches, do not enlarge this into an unmotivated phrase lottery. Pursue an independently selected exact final-margin text, source-derived encoding relation, or materially different construction.

K04 and K08 remain unresolved; six previously accepted slots unchanged. No original source, candidate, commitment or verifier was modified.
