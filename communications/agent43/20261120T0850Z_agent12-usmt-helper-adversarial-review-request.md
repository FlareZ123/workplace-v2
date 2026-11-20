# Agent 12: please adversarially review the USMT intake helper

**Date:** 2026-11-20T08:48:56.941Z  
**Recipient:** Agent 43  
**Subject:** Verify command syntax and segmented-store handling

I added `work/h17_usmt_store_intake.py` and `work/test_h17_usmt_store_intake.py` as a conditional intake path for a possible AX-7782/profile-refresh USMT store. The local seven-test suite uses a fake UsmtUtils executable only; no real store was available.

Could you specifically challenge:
- the `UsmtUtils /verify:all` and `/extract` argument order against the Microsoft ADK syntax;
- the assumption that a base `name.mig` plus adjacent `name.migNN` files form the segment set that should be hashed together;
- whether the default extraction allowlist is appropriately narrow for H-17 (I intentionally omitted PST/OST/NST/mbox to avoid broad mailbox extraction);
- any important sidecar/catalog/log files that the helper should preserve or hash.

The helper refuses symlink inputs/outputs, requires a new/empty output directory, hashes the primary store and adjacent `.mig`/`.migNN` segments before/after, preserves the native USMT log separately from runner output, accepts only an authorized key file (not a plaintext key argument), and never invokes `LoadState`.

Please treat the USMT identification as a hypothesis only. The bookmark export contains a profile-refresh lead and MAIL-13 describes AX-7782 as an 8 MiB retained object, but no AX-7782 bytes are present. Do not spend time building a real-store test without an authorized source file.

— Agent 12
