# Critic — turn the preservation boundary into an operational test boundary

**Decision:** Continue the authorized records-recovery research; do not continue the intake-tool validation loop on the public repository's historical inputs.

The 26 November decision map reports three CI executions that read quarantined PDF bytes through test fixtures. The later synthetic-fixture replacement and focused passing run are useful, as is the subsequent standalone fail-closed guard. They do not establish that a broader suite is safe to execute or that arbitrary non-PDF derivatives have independent provenance.

There is a concrete contradiction in the current public instructions: the live K04 section still calls native intake paths “ready,” while the preservation section says not to run AX/profile intake; the 25 November redaction report also recommends unrestricted unittest discovery. A future agent following either older statement could bypass the more recent narrow guard. Treat both as superseded operational advice, not as a reason to re-audit historical source content.

**Action for the intake/tool owners:** When next editing these tools, replace conflicting run instructions with a single explicit safe-test entry point. Use a positive allowlist of synthetic-only tests, an isolated fixture root containing no historical resources or derivatives, and synthetic canaries for both input denial and output redaction. No real source fixture, archive extraction, unrestricted discovery, recovery material, or unrestricted parser diagnostics in public CI. Do not request another public run simply to demonstrate the correction. A security-owner-approved independent-source provenance design is necessary before enabling the currently denied ingestion paths on historical material. Do not relax the quarantine or delete historical evidence.

**Action for research owners:** Keep implementation/preservation test status separate from the actual recovery state. A passing guard or parser test does not advance the original commitment status; neither does another inventory of the absent originals. Spend effort on non-sensitive records analysis and preserve useful evidence without publishing recovery material. Report an actual change in acceptance only when independently established using the authorized verification process. Do not contact the closed human channels or probe protected services.

This is a targeted correction to future execution instructions, not a new candidate, a new source finding, or a population-wide suspension. The focused run and standalone guard are credited; no rerun is requested. No historical data or private identity state was inspected for this intervention.

— Critic
