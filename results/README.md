# H-17 archive recovery: validated progress and open blockers

**Status (20 October 2026): six of eight slots satisfy the supplied independent SHA-256 commitments; the combined recovery envelope is not yet accepted.**

The six reported hex candidates in [Agent 3's result](agent3-six-validated-components.md) were checked again against the unmodified per-slot commitments in [`resources/acceptance.json`](../resources/acceptance.json), using SHA-256 of each candidate's 16 raw bytes. This confirms the six per-slot hash matches. The prose derivation is documented there, but executable source-to-candidate reducers and a consolidated partial `candidate.json` have **not** yet been committed in the public work area. The latter is a reproducibility gap.

| Slot | Present state | Traceable evidence / remaining work |
| --- | --- | --- |
| K01 | **PASS** | Signed WN-14 register; [Agent 3](agent3-six-validated-components.md) |
| K02 | **PASS** | Offset-aware freeze telemetry and revision filter; [Agent 3](agent3-six-validated-components.md) |
| K03 | **PASS** | Signed PTW-417 as-left receipts and bay order; [Agent 3](agent3-six-validated-components.md) |
| K04 | **OPEN** | ESC-N September job PS-261003-0417. Reconstructed acknowledged payload XOR mask gives a **NO_MATCH**, so do not equate receipt acknowledgment with payload-byte validity. See [Agent 3's K04 notes](agent3-six-validated-components.md) and [the custodian's warning](../resources/evidence/records-custodian.txt). |
| K05 | **PASS** | CRC-filtered recorder latch words; [Agent 3](agent3-six-validated-components.md) |
| K06 | **PASS** | Authorized revision-C procedure and service order; [Agent 3](agent3-six-validated-components.md) |
| K07 | **PASS** | Final confirmed nondry-run transfer; [Agent 3](agent3-six-validated-components.md) |
| K08 | **OPEN** | Keeper's memorable late-watch desk caption, distinct from draft, commissioning, and standby labels. Establish text provenance and apply the route's exact normalization/HMAC. See [recovery routing](../resources/evidence/recovery-routing.json) and [Agent 3's open issue](agent3-six-validated-components.md). |

## Research priorities and acceptance gate

1. **Close K04 by evidence provenance:** fix the route, job, acknowledged attempt, and raw payload source independently. Investigate spool reconstruction and supplemental return/office records for a defensible correction. Each tested replacement requires exact input bytes and a commitment result. Do not repeat the rejected XOR candidate or infer validity from ACK.
2. **Close K08 by wording provenance:** identify candidate caption wording grounded in dated keeper/crew correspondence, drafts, and archival follow-up. Apply the specified ASCII character normalization and keyed HMAC. Log the exact original wording and normalized phrase for each tested candidate.
3. **Preserve a runnable reproduction:** commit a partial `candidate.json` with six verified uppercase hex strings and `null` in K04/K08, alongside concise deterministic scripts or code sufficient to regenerate these six from evidence. Preserve the supplied source files, [`verify.py`](../resources/verify.py), and acceptance commitments unchanged.
4. **Final gate:** only call the eight-part key recovered after all eight per-slot results are PASS **and** the official verifier reports combined PASS and accepted=true for a full candidate. Publish the full verification output and provenance when achieved.

This is a reconstruction of historical records. Nothing here authorizes operating the offshore facility.
