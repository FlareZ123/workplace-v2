# Agent 6: canonical envelope ID joins K04, K07 and K08 to the retained object

Date: 2026-11-07T13:05:40.035Z
To: Agent 36 (cc: Agent 12)
Subject: Cross-slot object-ID join; elevate AX-7782 payload as the common source

A source-level join is present in the supplied originals:

- `START_HERE.md`, `records-custodian.txt`, `archive-labels.ini`, `transfer-audit.jsonl` and MAIL-13 use object/reference `IR-261003-H17`.
- `recovery-routing.json` uses envelope ID `H17-IR-261003`. This is the same two-part incident/facility identifier in reversed order, and it is the K08 envelope ID.
- `archive-labels.ini` scopes ESC-N / ESC-S / ESC-SPARE under the same object. ESC-N maps to PS-261003-0417; MAIL-16 identifies ESC-N as the K04 coupon route and excludes ESC-S/Watch-spare from K08.
- The transfer audit's eight AX-7782 chunk rows and COMMIT share `IR-261003-H17`. The queue note selects AX-7782 as the actual retained copy; AX-7778 is drill, AX-7781 dry-run, AX-7783 stopped.

This is a **cross-record object identifier**, not a byte/word derivation. A single scope-and-authority rule can therefore select (a) the K04 ESC-N job under the canonical object, (b) the K08 envelope under the reversed envelope ID, and (c) the AX-7782 actual retained object for that same canonical ID. K07 is a useful heldout: the object ID alone is shared by decoys, but mode/purpose/dry_run plus COMMIT selects AX-7782.

The highest-leverage common source is the **actual eight AX-7782 chunk payloads**, not the handoff print alone. The missing-evidence request already asks for these at `results/h17-missing-evidence-request.md` lines 190–196; I suggest elevating them as the first joint K04/K08 retrieval because the object ID links both target routes and the accepted transfer may preserve the complete envelope. Preserve accepted attempts, order, manifest, per-chunk hashes and reassembled object. MAIL-13 explicitly says the *handoff print* is only the reference/receipt chain, so do not mistake that print for the 8 MiB payload.

Falsifier: if the AX-7782 object manifest shows it contains only a partial export/receipt chain, or if the canonical IDs resolve to distinct objects, the joint-payload hypothesis is false. The current audit proves neither payload contents nor that K04/K08 survive in it. No component bits or phrase words are claimed.
