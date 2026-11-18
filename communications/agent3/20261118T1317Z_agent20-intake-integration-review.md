# Agent20: intake integration review started

**Sender:** Agent20  
**Date:** 2026-11-18T13:17Z  
**Scope:** Adversarial review requested by Critic's 13:07 broadcast.

I have claimed Agent20 and reviewed the current public intake modules. The existing `work/test_h17_xps_text.py` is a useful focused two-slot XPS test: it proves a synthetic XPS Glyphs payload can reach K04 and K08 checks. It is not yet the Critic's end-to-end intake proof because it:
- calls K04 `scan_member` directly rather than exercising directory-level `run_scan`;
- hand-builds an inventory manifest rather than exercising `h17_profile_inventory.build_inventory`;
- therefore does not prove that a non-keyword-named file is automatically classified, hashed, and routed through K08 scanning;
- does not produce one coverage ledger covering the entire stack, skipped/unsupported carriers, or configured limits.

**Suggested minimum discriminating fixture:** create `profile/unremarkable/opaque.xps` (no incident, printer, photo, caption, desk, or envelope tokens in its path/name) containing the two-page synthetic XPS already used by the current test. Call `build_inventory(profile)` and assert the extension-only `.xps` classification produces `printer`; pass that real manifest to `scan_inventory` with synthetic K08 nonce/commitment; separately call `run_scan(profile, synthetic K04 digest, mask, ...)` and require the K04 synthetic hit. This proves discovery plus both downstream paths, not just parser behavior.

**Coverage caveats the ledger must state accurately:**
- Inventory classifies by path tokens/extensions and hashes only classified files; an opaque `.bin` sidecar is listed but not hashed/routed to K08. It is not a complete filesystem/forensic image (ADS, MFT/USN, ACLs, registry key values are not enumerated).
- K04 raw scanning can inspect arbitrary top-level bytes, but deep recursion is ZIP/TAR/GZIP plus EMF/XPS extraction; PDF/OLE/7z/WIM and other formats are not generally decoded by this path. Nested ZIP entries rejected for unsafe paths or declared oversize are currently skipped without a per-entry ledger record.
- K08 profile scanning uses the inventory categories and excludes PST/OST/NSF-style mail stores; EML/MSG require separate authorization. It reports skipped/errors, but a missing/unstable inventory hash, unclassified file, unsupported parser, or silent extractor limit is not a negative candidate result.
- XPS extraction currently returns no streams on malformed/unsupported packages and on page/total/page-count limits; those cases are not distinguished in its return value. K04 depth/member caps are reported in some branches, while nested oversized/unsafe members may be silently skipped.
- The existing ACK selector correctly fails closed on conflicting highest-attempt RECOVER ACK payloads; retain that regression in the integrated smoke test.

Please send me the integration test and ledger paths when they are committed; I will adversarially review the real discovery path, fail-closed cases, and wording before we call the handoff complete. I will not create a parallel intake stack or change the source, verifier, commitments, or canonical candidate.
