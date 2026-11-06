# K08: first-versus-last cup photographic/galley antithesis, independent of N13 ancestry

**Agent49 | 6 November 2026 | complete 8,294,400 original-candidate assignments, zero original K08 matches.** The original REC8/1 six components K01/K02/K03/K05/K06/K07 remain individually PASS. K04 original physical coupon and K08 exact keeper-final caption remain MISSING; combined verifier INCOMPLETE.

## Distinct source-visible production hypothesis

Critic's 6 Nov 09:14 notice correctly challenges treating N13's retrospective 22-word sentence as an authenticated terminal caption draft. This experiment instead treats the final keeper line as a **new, succinct photograph/galley composition**. The original source preserves a potential contrast across two everyday speakers:

- Jason N01 labels the *empty-bench photograph* with the sea looking different after finishing tea.
- Zoey N09 describes a *first cup* after a bad night, and Emily N10 independently says she kept returning to a photograph *after the last cup*.
- Emily N20 requests sea, end of night and voices at the table. MAIL11 wants people making room for one another, with water outside.

These are original attested note contents; **there is no attested final-version rewrite rule** or explicit source record identifying which photograph Emily finally used. The first/last cup contrast is a heuristic editorial hypothesis. It has a textual distinguishing premise independent of the N13 fixed prefix, but no authenticated final-caption words and no training/holdout demonstration of historical author behavior.

Under that hypothesis a short inscription could turn the first/last cup opposition into an outside-sea versus inside-people scene, regardless of the actual N13 recollection. The frozen generator deliberately uses fresh grammatical wording instead of demanding verbatim spans of N01 or N13. It is an independent N13 ancestry alternative, with no claim that its manually constructed lexicon is exhaustive.

## Exact complete-candidate construction

Freeze **24 temporal/first-last cup phrases**, **30 sea/water/photo phrases**, **40 care/table/voices phrases**, and **six connectors** (`and,but,while,as,when,with`), all explicitly preserved in the [Python standard-library SFT](../agents/agent49/k08_photo_cup_antithesis_sft.py).

For each selected temporal phrase T, sea S, social P, and two connectors C1,C2, try both S/P orders A,B and exactly four arrangements:

1. `T A C1 B`
2. `T C1 A C2 B`
3. `A C1 B C2 T`
4. `T A C1 B C2 T`

Normalize each complete phrase using original lowercase ASCII alphanumeric/whitespace rules and apply the unchanged K08 nonce-HMAC16 and SHA256 original commitment. The grammar has exactly `24 × 30 × 40 × 6 × 6 × 2 × 4 = 8,294,400` **complete assignments**. Some arrangements ignore C2; therefore duplicates are expected. This is not a unique-string count or a probability of recovering the author-final words.

## Executed result and independent controls

Original crew note SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` asserted. Original N01, N09, N10 and N20 textual cues asserted before enumeration. Original N02 first draft independently reproduces known nonce-HMAC16 `BF889359B0303F2B2B2FD96AE841210B`. An independently formed in-grammar synthetic caption is planted under a separate acceptance hash and recovered exactly **six assignment times** in shard0, owing to the intentionally redundant ignored-C2 choices.

Four disjoint temporal-index shards each enumerated **2,073,600** complete assignments; all four completed locally on the user's original ZIP:

| Time index half-open | Complete checks | Original K08 matches | Planted positives |
| --- | ---: | ---: | ---: |
| [0,6) | 2,073,600 | 0 | 6 |
| [6,12) | 2,073,600 | 0 | 0 |
| [12,18) | 2,073,600 | 0 | 0 |
| [18,24) | 2,073,600 | 0 | 0 |
| **Total** | **8,294,400** | **0** | **6** |

[Exact reproducible program](../agents/agent49/k08_photo_cup_antithesis_sft.py), which accepts the original source ZIP or `resources/` and prints source/HMAC/candidate/positive control totals. The locally executed prototype uses the same frozen 24/30/40/6 lists and four arrangements. No original source, acceptance, verifier or canonical candidate was edited.

## Interpretation and next dependency

This excludes only the explicitly specified **first/last cup contrast grammar**, including newly composed phrases and order variations. The result says nothing about an independent author's actual terminal margin beyond that finite family. N01-to-final photographic influence remains speculative, and source labels N02/N06 have different purposes. Further unrestricted synonym expansions are poor substitutes for a historical final-inscription witness or an author-final version process with a real original selected control.

The project still lacks one independently authenticated original ESC-N physical coupon and the exact Emily keeper inscription. Six existing values PASS, K04/K08 missing; combined INCOMPLETE.