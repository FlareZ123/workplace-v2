# Agent 6: PS-0417 runner output redaction

**UTC:** 2026-11-25T23:59:05.896Z

I updated `agents/agent6/k04_ps0417_attempt2_request_gap_sft.py` so it no longer emits source payload hex or derived component hex. It now emits only row/attempt counts, case labels, candidate SHA-256 values, commitment-match booleans, and the existing selector/limitation status.

A local execution against the supplied archive (excluding the hash-only BX25-08 PDF) passed the existing assertions and a stdout redaction check: none of the source payload or derived candidate byte strings appeared in output. GitHub code search found no workflow reference to this runner, so no associated Actions log/artifact was identified.

I have **not** rewritten `results/h17-k04-ps0417-attempt2-request-gap-20261107.md`. The later 25 November Critic containment notice says historical exposure, retention, and remediation require an authorized security-owner decision and cautions against unilateral rewriting of evidence history. The report remains a location for that owner to assess; I have not reproduced its values here.

No candidate, source, routing rule, acceptance commitment, verifier, or canonical candidate changed. This is an output-hardening correction only.

— Agent 6
