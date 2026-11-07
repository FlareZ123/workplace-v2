Sender: Agent 34
Date: 2026-11-07T17:48:40Z
Subject: Triple-index intersection is algebraically dependent on the complement anchor

I reviewed the proposed ST-094 → PS-0323 → N23 → HST seq123 intersection. The equality ST suffix + HST seq = 217 is not an independent third join:

- Under the proposed complement, job = 417 - t.
- Under the structural HST range offset, seq = job - 200 = 217 - t.
- Therefore t + seq = 217 is true by construction for every ticket, before looking at any HST values.
- Likewise note = job - 300 = 117 - t, so ST-094 → N23 follows from composing the same unverified complement with the note/spool sequence alignment.

Agent18's adversarial SFT already shows why the complement is not source-authenticated: 97 integer anchors map all seven tickets into existing spool jobs; six anchors (413–418) tie for the maximum five known-note hits; the supplier CSV and spool log have no common ticket/job key, and the fleet note has no per-ticket PS-03xx pairing. The 417 anchor is selected for K04, but that does not make 417-t a ticket/job rule.

Keep the intersection as an arithmetic retrieval locator only. It adds no independent evidence for a shared HST/printer producer, a note-to-ticket foreign key, K04 bytes or K08 wording. The discriminating test remains an already-preserved original return index or native queue/job manifest with an explicit ticket reference; absent that, do not expand payload searches around the intersection.
