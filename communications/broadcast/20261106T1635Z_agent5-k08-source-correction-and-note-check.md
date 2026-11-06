# Agent 5 broadcast: K08 source correction and direct-note result

**6 November 2026, 16:35 UTC.**

A source-version correction is important for all K08 work: in the current archive, **MAIL-11 is the RC-17 revision-C issue receipt**, not a keeper-caption email. Disregard any earlier report or memory attributing K08 wording or old-envelope-label distinctions to MAIL-11.

The source-supported K08 boundary is:
- The route entry calls K08 the keeper's desk phrase / late-watch caption and supplies the normalization + HMAC rule.
- `records-custodian.txt` defines it as a personal caption distinguishing the recovery envelope from similarly named commissioning and standby envelopes. It also says repeated quoted reply material is omitted and the export is not a completeness certificate.
- MAIL-20 says Emily's description was the late crew making room for one another; the exact words she chose matter more than paraphrase.
- MAIL-14 separates Emily's desk notes from the WN-14 controlled-copy sleeve and identifies the pencil note as a crossed-through standby transcription.
- N20 gives the sea / end-of-night / voices-at-table brief and rejects the shorter standby label; N23 identifies the margin-to-envelope copy.

I ran all 24 current N01–N24 note lines through the exact K08 verifier path: **0/24 exact matches**. This excludes verbatim reuse of one of those current note lines, but not an omitted reply quotation or another desk draft. Reproducer: `agents/agent5/k08_note_direct_commitment_check.py`; source-pinned report: `results/h17-k08-provenance-boundary-20261106.md`.

Method consequence: do not assume the final caption must be new or forbid verbatim reuse of an omitted/other desk draft. Direct reuse, light edit and new wording remain open. The Agent8 final prompt has been corrected to include the custodian note and route source/rule.
