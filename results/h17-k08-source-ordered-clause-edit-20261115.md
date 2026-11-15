# K08 source-ordered grammatical deletion and clause splice (15 November 2026)

**Agent 8. Original K08 commitment hits: 0 of 192,000 complete assignments.** This is a scoped exploratory source-editing rule, not recovery of the final envelope wording.

## Exact independent construction

N20 (Emily) specifies the scene order **sea → end of night → voices at the table**. Her N13 caption is a longer, conjunctive scene, and MAIL-11 describes an edited, rememberable final line. Test one concrete *deletion-plus-splice* mechanism that differs from minimum-SCS interleaving and from pointwise word substitution:

1. N01 provides every contiguous 2–6-word span containing the literal word **sea**: 10 options.
2. Retain N13's complete first six words, **at the end of the night**. Truncate its following mug/window noun phrase at exactly four syntactic cut points; independently retain one of five specified suffixes of its lamp clause. Preserve original relative word order and the source conjunction only if both surviving scenes are present: **20 complete central-clause options**.
3. N20 supplies every 4–8-word contiguous span containing the exact phrase **voices at the table**: 15 options.
4. In N20's specified motif order, join the three pieces at two boundaries, each with one predeclared connector from empty, and, as, when, after, with, while, until. Preserve every selected source word exactly and normalize the complete phrase according to the original route.

This gives exactly `10 × 20 × 15 × 8 × 8 = 192,000` complete assignments, of which 182,520 are distinct normalized phrases. This excludes only this finite clause-deletion-and-join model; no source proves Emily used such a rule.

## Original evidence and executed checks

Run `python agents/agent8/k08_clause_edit_source_sft.py` in the repository root. Portable Python standard library only. The script verifies all source SHA-256 values before deriving its trial strings:
- Crew notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Recovery route: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- Acceptance: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

The script asserts that Emily's N02 known caption produces the independently established HMAC16 `BF889359B0303F2B2B2FD96AE841210B`. An independently predeclared *in-family* planted phrase is recovered exactly once against an isolated synthetic digest. Every original trial uses the unchanged `SHA256(HMAC_SHA256(desk_nonce,normalized_UTF8_phrase)[:16])` K08 commitment. Original hits: **zero**.

## Next model decision

The original source edit may instead have involved newly authored vocabulary or a different document/copy stage. This negative rules out neither. Do not extend the same clause-cut/connector grid arbitrarily. The official candidate, route, original source, commitments and verifier are unchanged. Six previously accepted components remain intact, K04 and K08 unresolved, combined REC8/1 INCOMPLETE.
