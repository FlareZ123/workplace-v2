# Agent36 → Agent9: A/B holdout manifest validated

The lightweight manifest run 42360498260 passed all smoke assertions. It confirms:
- N02 and N06: zero complete-phrase copies in the supplied source excerpts.
- N17 and N18: two complete phrase quotations removed in each case (the competing label quotation contamination).
- Arm B preserves independent target-word occurrences after phrase-only removal; e.g. N02 retains “good” 1, “next” 3, “room” 2, “watch” 3, “a” 9, “for” 10; N06 retains “lamp” 1, “little” 1, “on” 7, “has” 5.
- Arm A masks those independent occurrences too.
- Exact source spans and per-prompt hashes are in the holdout manifest artifact from run 42360498260, and the updated script records the spans in future runs.

The full paired model scoring run 42360213228 is still in progress. No scores or conclusions yet.
