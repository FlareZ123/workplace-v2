# Agent 46: K08 whole-text copy hypothesis tested

**17 November 2026, 20:15 UTC**

Following Critic's 19:57 request, I tested one bounded model materially different from the phrase-grammar families: **the final envelope caption is a verbatim complete sentence copied from an earlier crew text or card/caption retained in another role**. This is a candidate-selection/copy model, not a word-generation sweep.

I used the exact K08 normalization and HMAC-SHA256/first-16-byte/SHA256 commitment pipeline in `work/h17_check_phrase.py` against the unchanged local acceptance target. The following source-grounded complete texts all returned **NO_MATCH**:

| Candidate source | Complete text | K08 component |
|---|---|---|
| MAIL-02, Emily's late-arrival provision | “There should be enough soup for the late arrivals on Thursday.” | `50D1489FC4B4CAA5FE98C1021EE884AB` |
| MAIL-02, bowl allocation request | “Could we keep six clean bowls aside?” | `3F9EEBEF8F34152AFAAD04804B251151` |
| MAIL-02, late-arrival mug sentence | “They arrived after the dishwasher finished last time and ended up eating out of mugs.” | `6AAC892E99250805542E429126AB2BDB` |
| N09, Zoey's galley-board caption | “Nobody should have to make their first cup alone after a bad night.” | `FCCD17F08A1C558E344613EDD0BE0B19` |
| N12, Simon's workshop-card line | “The best repair is sometimes remembering who comes on after you.” | `FE024F718A937BB79AAA699DBA6EB784` |

The role boundaries matter: N09 is explicitly a **galley-board caption**, whereas MAIL-12 says Zoey's small card was **not** put on the board; N12 is a **workshop card**, not an authenticated transcription of the shelf card. Neither establishes an adoption edge to Emily's envelope. MAIL-02 is an earlier hospitality email, but there is no evidence of verbatim copying from it. These are falsified verbatim-copy candidates, not evidence that the physical card's text is known.

**Conclusion:** no complete retained text tested here is the K08 final inscription. Do not expand this into a generic edit grid. The decisive missing witnesses remain the actual shelf card, Emily's WN-14 desk-note underleaf/final margin, the relevant original photo-caption source, or the AX-7782/IR-261003-H17 object with its Bundle06 manifest/trim log. Six slots remain PASS; K04 and K08 remain MISSING.

— **Agent 46**
