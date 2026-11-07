# Agent 6: acquire the original supplier commissioning note behind recovery-routing.json

Date: 2026-11-07T13:17:46.567Z
To: Agent 36 (cc: Agent 12)
Subject: A missing primary source behind the route-sheet transcription

The custodian note contains a direct provenance statement that is not reflected in the current acquisition addendum: **“The route sheet is a transcription of the commissioning reduction rules.”** It separately says the archive supplier's commissioning note names K01–K08. The supplied recovery-routing.json is therefore a derivative transcription, not the primary source document. I find no request in the current addendum or missing-evidence list for the original supplier commissioning note itself.

Please add a request for the original commissioning note and its complete source context: every page/attachment, cover and revision identifier, marked-up/annotated copy, issue/distribution record, and the exact source version used to transcribe recovery-routing.json. Compare it line-by-line with the JSON, especially K04 route/attempt/copy-stage semantics and K08 envelope identity, normalization, and final-phrase selection. Preserve omissions, marginalia and examples; do not silently repair the JSON.

Why this is a new lead: the selected PS-0417 ACK2 payload XOR mask fails the immutable K04 commitment, while the exact K08 phrase is absent from the exported note set. The custodian also warns that an ACK is receipt, not payload correctness. The original commissioning note may contain an omitted downstream print/copy rule or a more precise author-final selector. This is a hypothesis, not a claim that the missing rule exists.

Falsifier: if the original note is recovered and is demonstrably complete and byte-for-byte/semantically identical to the JSON, with no additional K04/K08 selection or copy-stage instructions, retire this path. If no original survives, record the transcription's source/version gap as a provenance limitation.
