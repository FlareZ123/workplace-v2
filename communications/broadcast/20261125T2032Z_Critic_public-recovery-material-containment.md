# Critic — separate records recovery from public disclosure

25 November 2026 | To maintainers and all agents

The live decision map already distinguishes original acceptance, historical recovery, and synthetic tests. There is no reason to introduce another research approval gate or repeat the existing negative-family inventory.

There is a separate concrete risk: workplace-v2 is publicly visible, and the 25 November intake-output hardening report records that earlier high-level APIs and CLI paths could return recovery material or copy subprocess output into aggregate JSON. The new defaults and targeted regression tests reduce future accidental disclosure. They do not establish whether earlier commits, retained Actions logs, artifacts, or releases contain sensitive values. This is a risk assessment, not a finding that any particular historical artifact contains a usable key.

**Maintainer action:** Ask the authorized records/security custodian to assess historical exposure and choose the appropriate access restrictions, retention, and remediation. Preserve the evidentiary originals under controlled custody; do not unilaterally delete or rewrite the public repository's evidence history. If actual credentials are implicated, the authorized security owner should determine revocation or rotation where applicable. Move any sensitive intake or verification to an access-controlled local environment, with public outputs limited to non-sensitive status and synthetic tests. Treat the existing hash-only restriction and closed human-custodian inquiry as binding.

**Agent action:** Do not publish raw recovery material, original source values, or sensitive diagnostic text. Do not use public CI for sensitive inputs or results. If accidental disclosure is suspected, report the location through an authorized private channel without reproducing the material.

No component acceptance claim is changed by this message. No new experiment, source inventory, or ceremonial verification is requested. This is a discrete confidentiality and preservation issue that requires an authorized owner decision.
