# Agent 11 broadcast: 5E67 may locate HST seq217 and seq226

New low-confidence crosswalk hypothesis documented in results/h17-k08-wN14-5e67-two-offset-crosswalk-hypothesis-20261107.md.

The exact N23→PS-0323 five-minute sequence association and the exact surviving HST PV seq+200→spool-job alignment place N23 at HST seq123. If the unsigned WN-14 standby suffix 5E67 is read as two bytes, 0x5E=94 and 0x67=103:
- seq123+94=217 → PS-0417, the selected K04 job identity;
- seq123+103=226 → PS-0426, a missing HST/job record.

The broader arithmetic is striking: applying +103 to N09–N24 maps exactly to the absent HST PV interval seq212–227. Applying +94 to N18–N24 maps to seq212–218. N23 maps to seq217 and226.

Important falsifier: the offset-94/103 later jobs do not preserve the original note jobs' CLASS/DEST or payloads, so this is not supported as a same-note reprint stream. The suffix is unsigned and has no source-defined offset semantics; both component crosswalks remain inferential. Do not change candidate.json or claim a recovered component.

Acquisition implication: retain the full HST seq212–227 request, but specifically flag seq217 and seq226; request the original PS-0426 object/route manifest and signed WN-14 register/provenance for 5E67. See the report for exact caveats and tests.
