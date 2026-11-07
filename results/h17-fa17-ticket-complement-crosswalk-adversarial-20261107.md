# FA-17 417-minus-ticket complement crosswalk: adversarial assessment

**Owner:** Agent 18  
**Date:** 2026-11-07  
**Status:** bounded source audit; no K04/K08 component recovered  
**Reproduction:** python agents/agent18/fa17_ticket_complement_crosswalk_sft.py

## Question

Agent 12 proposed the candidate mapping job_suffix = 417 - ticket_suffix for the seven posted FA-17 supplier tickets. Composing that with the already-reported structural note/spool alignment Nn -> PS-0300-n gives note_index = 117 - ticket_suffix. The proposal maps five L-29/N binder tickets to PS-0305/0311/0318/0323/0336 (hypothetical notes N05/N11/N18/N23/N36) and two L-28/A2 holdouts to PS-0319/0330 (N19/N30).

The useful question is whether the apparent matches independently authenticate ticket-to-job identity, or whether they follow automatically from the chosen anchor and the contiguous spool range.

## Source-pinned observations

The SFT checks the exact GitHub resource blobs by SHA-256 before parsing:

- supplier-reconciliation-L29.csv: 73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e
- print-fleet-retirement-note.txt: 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf
- spool-reconstruction.log: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- noticeboard-and-desk-notes.txt: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb

The L-29/N binder order is source-stated as ST-094, ST-081, ST-106, ST-099, ST-112. The posted L-28/A2 FA-17 holdouts are ST-098 and ST-087. At the source-selected K04 job anchor 0417, the arithmetic gives:

| Ticket | Proposed job | Proposed note | Note exported? | Spool class/destination |
|---|---:|---:|---|---|
| ST-094 | PS-0323 | N23 | yes | RECOVER / store |
| ST-081 | PS-0336 | N36 | no | LABEL / bench |
| ST-106 | PS-0311 | N11 | yes | STORES / desk |
| ST-099 | PS-0318 | N18 | yes | RECOVER / store |
| ST-112 | PS-0305 | N05 | yes | LABEL / store |
| ST-098 | PS-0319 | N19 | yes | RECOVER / desk |
| ST-087 | PS-0330 | N30 | no | STORES / desk |

All seven proposed jobs exist. That fact is not discriminating: the preserved spool IDs contain the uninterrupted interval PS-0300 through PS-0427. For these ticket suffixes, **97 different integer anchors, 412 through 508 inclusive, map all seven tickets into existing spool IDs**. The anchor 0417 is source-selected for K04, but no source field states that a supplier ticket maps to 417 - t.

At anchor 0417, five of seven derived note indices fall within the exported N01–N24 set. That count is not unique: **six anchors, 413 through 418, each produce five note-index hits**. The two values N30 and N36 are extrapolations beyond the actual note export. They are not evidence that notes N30 or N36 existed, were authored, or carried K08 wording.

## What the source does and does not join

- The supplier CSV contains ticket IDs, account, folio, posting and descriptions; it contains no PS job identifier.
- The spool log contains job IDs, attempts, states, classes, payloads and destinations; it contains no ST ticket identifier.
- The print-fleet note links PS-0417 to ESC-N / L-29/N / FA-17 and separately lists the five L-29/N binder tabs. It does not pair any individual tab with a PS-03xx job.
- The note/spool crosswalk is already bounded to the 24 supplied notes N01–N24 and jobs PS-0301–PS-0324. It establishes a structural 24-row sequence, not a foreign key that can be extended automatically to N30/N36.
- The mapped classes/destinations are heterogeneous. They do not provide an independent role match for the proposed ticket/job pairs. In particular, ST-112 would map to LABEL/store under the complement proposal, while the separate +304 hypothesis maps it to PS-0416 RECOVER/bench, the immediately preceding same-role job to PS-0417. That competing discriminator is itself still an inference and does not authenticate either join.

## Assessment

417 - t is a coherent **candidate retrieval index**, and the ST-094 -> PS-0323 -> N23 coincidence is worth retaining because N23 is the note that points to Emily's final-envelope margin. It is not an authenticated supplier-index relation. The 7/7 job-existence count is explained by the contiguous spool interval; the 5/7 known-note count is not unique; and N30/N36 must remain hypothetical labels only.

Do not use the complement to infer note contents, select a K08 phrase, or reconstruct K04. The original R:/Stores/returns/SEP26/index.htm, native ticket/folio records, or a native queue/job manifest containing an explicit ticket reference would be the required discriminator. The existing acquisition request already names the retired index; this result does not justify reopening the closed custodian channel or sending a duplicate request.

## Next useful test

If an already-preserved original index or native manifest becomes available, freeze the proposed mapping before inspecting job content and test at least one held-out ticket/job pair, preferably ST-081 -> PS-0336, plus one A2 holdout ST-087 -> PS-0330. Require an explicit source-side key or a distinctive metadata/content prediction. If no such cross-reference exists, retire the complement as an arithmetic locator and keep the N01–N24 crosswalk bounded.

**Confidence:** high in the arithmetic and source-field audit; low in the proposed ticket-to-job relation; no conclusion about missing K04/K08 values.
