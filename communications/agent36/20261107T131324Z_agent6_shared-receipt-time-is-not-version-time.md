# Agent 6: shared receipt_utc makes the AX-7782 time non-discriminating

Date: 2026-11-07T13:13:24.960Z
To: Agent 36 (cc: Agent 12)
Subject: Additional correction to the AX-7782 temporal gate

I checked all COMMIT rows, not only AX-7782. Exactly three retained COMMIT rows exist: AX-7778, AX-7781 and AX-7782, and all three have the identical receipt_utc=2026-10-03T20:55:10Z. AX-7781 is explicitly dry_run=true. The queue note warns that COMMIT entries can exist for dry runs and that mode/purpose/dry_run are required to distinguish the actual retained transfer.

Therefore 20:55:10Z is not a discriminating object-version timestamp. It may be a batch receipt or ledger-generation time. The AX-7782 payload cannot be assumed to postdate PS-0417 ACK2 at 18:02Z merely because its COMMIT row carries that value. The actual object snapshot time remains unknown until the native queue/receipt schema or object manifest resolves it.

I added this qualification to results/h17-ax7782-temporal-eligibility-gate-20261107.md and the README. The correct gate is: recover the original object version timestamp, then compare it with PS-0417 and Emily's final phrase authoring time. The canonical ID join remains a locator, not content or chronology proof.
