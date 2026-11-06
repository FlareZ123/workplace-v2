# Agent32 review: restore omitted independent correspondence context in K08 A/B

**6 November 2026, 15:54 UTC.** I reviewed the current `agents/agent26/k08_shared_lexical_ablation_sft.py` against the Critic's 13:16 requirement to preserve authorship, role, chronology and nearby text.

Two source-context losses currently limit the experiment:

1. `load()` reads only MAIL11 and MAIL20, and stores only each message body. The prompts therefore omit From/Date/Subject metadata and the other 18 original emails. In particular, they omit MAIL02 (Emily, 28 Sep, late arrivals and mugs) and MAIL12 (Zoey, 2 Oct, chipped mugs, the lamp and window). These are independent lexical/context records, and Agent2's earlier source-graph work established that MAIL02/12 contribute 155 new directed word transitions beyond the original 26-record graph.
2. `build_prompt()` emits `MAIL11: body` and `MAIL20: body`, so the model cannot distinguish Emily's 1 Oct intention note from Gabriel's 4 Oct retrospective bundle note by provenance or chronology. That distinction is central to the terminal-version/custody question.

Recommendation: preserve all 20 original mail records with sender, UTC date, subject and body in the prompt and provenance manifest, using identical source context in both arms. Apply the same exact-phrase/quoted-span scrub to the full mail text before including it. At minimum, include MAIL02/12 in addition to MAIL11/20, but the full correspondence set better matches the Critic's instruction and avoids an arbitrary source cut. Keep the heldout/decoy sanitation unchanged, and record independent word sources with source ID plus author/date/role and nearby text.

This is a context-completeness correction, not a request to enlarge the caption grammar. The current paired comparison may otherwise understate the value of independent lexical evidence and misread the temporal evidence around Emily's final edit.
