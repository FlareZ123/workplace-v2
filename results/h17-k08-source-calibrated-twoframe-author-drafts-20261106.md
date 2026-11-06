# K08: two explicitly known Emily-draft syntax frames, target negative

**Agent 5, 6 November 2026 UTC.** Original surviving source with exact full K08 HMAC16 then SHA256 commitment. **499,744 genuinely distinct complete normalized captions checked, zero original K08 matches.** Two independently source-attested historical draft sentences are each reproduced **exactly once**, and a separate planted full-caption acceptance check passes.

## Why this changed the previous experiment

Agent 5's earlier same-day figurative caretaker template explored 691,200 new distinct outputs but did not actually include either known original author's entire syntactic draft among the search candidates, making the claimed style resemblance weak. Rather than expand more arbitrary synonyms, this experiment corrects that explanatory limitation with two syntactic **author-derived patterns**, calibrated against the source-quoted original words:

- Original N02 first crew-board draft: `A good watch leaves the room ready for the next pair of hands.` Normalized `a good watch leaves the room ready for the next pair of hands`.
- Original N06 second desk draft: `The little lamp stays on until the corridor has gone quiet.` Normalized `the little lamp stays on until the corridor has gone quiet`.

The experiment permits both patterns and instantiates source/theme-compatible subjects, predicates and complements while preserving those templates. It avoids assuming undated N13's scene-recollection opening survived into the final keeper margin, and it does not confuse either known first/second draft with the final words referenced in N23.

## Exact finite test

**Frame A**: `{subject} {verb} {object} {state} {beneficiary}` with 12 subjects, 12 verbs, 14 objects, 13 states and 18 beneficiaries: **471,744 complete captions**. This includes the exact first draft N02 once.

**Frame B**: `{subject} {verb} {state} until {terminal}` with 14 subjects, 10 verbs, 10 states and 20 terminal clauses: **28,000 complete captions**. This includes the exact second draft N06 once.

The 499,744 resulting normalized strings are all distinct. The original note file SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` is asserted. N02's exact independently established HMAC16 `BF889359B0303F2B2B2FD96AE841210B` is reproduced, and source literal N02/N06 are asserted present. Every emitted candidate receives the original route-defined ASCII lowercase/alnum/whitespace normalization, HMAC-SHA256 first16 keyed by actual nonce `5F933DA6A1BD03C32DA5CBC25344F497`, and complete SHA256 against the unchanged K08 target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

The source-equivalent local original-ZIP execution returned:

```json
{"A":471744,"B":28000,"authentic":0,"historical_draft_N02":1,"historical_draft_N06":1,"planted":1,"unique":499744}
```

Read-only reproducible portable [Agent5 Python SFT](../agents/agent5/k08_twoframe_calibrated_drafts_sft.py) includes the exact fixed candidate list, independent real-draft controls, and a planted complete sentence `the sea waits by the window until the night is over`, recovered exactly once under a separate synthetic target.

## Limits and next action

Matching two known old drafts establishes syntax **coverage**, not a blind predictive author-final editor. The source explicitly says that the final keeper-envelope words were a different choice, and no original selected words are quoted. This excludes the exact two-frame complete-candidate grammar only; it does not provide any original terminal word, and enlarging those same two templates without an author-final version witness is unlikely to be informative. The original six other slots remain PASS, K04 and K08 unresolved, combined REC8/1 incomplete.
