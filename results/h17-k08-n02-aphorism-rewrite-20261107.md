# K08: testing Emily's first-draft aphorism as a keeper-caption version operator

**Agent14 | 7 November 2026 | 2,594,064 complete source-tethered constructions, 0 original K08 commitment matches.**

## Concrete question

Emily's attested **N02 first draft** reads “A good watch leaves the room ready for the next pair of hands.” Its sentence structure expresses an ethical handoff, resembling MAIL-11's specific description of the keeper phrase as people making room for one another after a long watch. Emily N20 later requires the sea, the end of the night, and voices at the table. These observations motivate a **conditional** N02-to-keeper version operator: retain the `subject + verb + place + beneficiary` grammatical chassis of N02, substitute scene/beneficiary words, and optionally prepend or append a water/night/table adjunct.

This differs in construction from an imperative invitation, a three-clause scene description, N13 deletion/insertion, an eight-note one-word carrier, or the 1.49-million MAIL-11 interior replacement test. It makes no claim that N02 is historically the direct ancestor of the final caption. N06 and N23 do not establish such a version relationship.

## Source and exact construction

Source SHA256 pins:

- Crew notes: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.
- Emily's MAIL-11, including its third-paragraph K08 wording constraints despite its RC-17 subject: `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`.

Freeze 17 subjects, 11 verbs, 16 place objects, 17 beneficiary predicates, and 26 optional adjuncts (including empty), all in the [source-pinned standalone Python test](../agents/agent14/k08_n02_aphorism_rewrite_sft.py). For a nonempty adjunct test it at both the start and end; for empty, test the bare N02-like sentence once. This makes `17 × 11 × 16 × 17 × (1 + 2 × 25) = 2,594,064` **complete candidate assignments**, not a claim of globally unique normalized captions.

For every full candidate, use the unmodified K08 normalization (lowercase ASCII token spans joined by spaces), `HMAC-SHA256` keyed by raw decoded `5F933DA6A1BD03C32DA5CBC25344F497`, its first 16 bytes, then full SHA256 against original K08 commitment `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Executed result and controls

A local read-only run against the original extracted ZIP evidence and acceptance produced:

```json
{"model":"N02-aphorism-subject-verb-object-beneficiary+adjunct","assignments":2594064,"original_matches":0,"original_historic_n02_control":1,"planted_wholecaption_control":1}
```

- A genuine original author control from N02 is exactly in the grammar once, and its first16 HMAC reproduces known `BF889359B0303F2B2B2FD96AE841210B`.
- A full in-model synthetic phrase `a long watch leaves a place at the table open for another voice while the sea is outside` is also generated once and recovered through the same HMAC16/full SHA256 chain under a separate planted commitment.
- **Zero exact original K08 matches.** No K08 word of the final caption has been authenticated. K04 physical coupon remains unknown. The accepted six components and combined incomplete outcome are unchanged.

## Research decision

This model is weakly motivated by the author's attested ethical handoff and later final thematic brief, without a recorded final-version operator or an authentic selected-final text for blind calibration. Therefore its negative **only** excludes this finite N02-syntax population. Enlarging its synonym vocabulary without source-selected wording would repeat the existing low-yield grammar cycle. New author-final source evidence or a true source-constrained revision selector is preferable.
