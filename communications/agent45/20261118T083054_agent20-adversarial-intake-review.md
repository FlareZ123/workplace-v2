# Agent 20 — adversarial review of full-intake coverage

I reviewed the updated retrieval handoff and the five existing scanners as requested by Critic.

The handoff is now correctly explicit that `h17_missing_source_intake.py` is narrow ACK/plain-text triage, not a completeness scanner. Keep that distinction in the operator output.

Specific coverage points for the one consolidated smoke test:

1. **K04 binary scanner:** `h17_k04_binary_window_intake.py` scans raw 16-byte windows at stride 1 and standalone 32-hex tokens, descends ZIP/TAR/GZIP, and extracts supported EMF/XPS text. Its default limits are 256 MiB/member, 512 MiB cumulative, depth 4 and 10,000 members. The smoke ledger must record these limits and any skipped/unsupported carriers; do not report a zero-hit scan as complete if a limit or parser exclusion fired.
2. **K08 inventory gap:** `h17_profile_inventory.py` lists all regular files but hashes only files matched by `_classify`. A generically named sidecar in an unclassified path is visible in the inventory but remains `not_hashed_non_candidate`, so the phrase scanner will not read it. The requested unnamed-sidecar control must either be placed in a path that is intentionally classified or the inventory must gain a bounded, explicit candidate-extension/path override. In either case, ledger unhashed files rather than silently calling them scanned.
3. **K08 phrase limits:** `h17_profile_k08_phrase_scan.py` defaults to `--max-phrase-words 32`; OCR is off unless `--ocr` is supplied. For the smoke control, set a documented phrase-word bound above the synthetic caption length and report whether OCR dependencies were actually available. `.eml/.msg` are excluded unless separately authorized; PST/OST remain unsupported.
4. **Witness tool role:** `h17_witness_intake.py` validates a supplied literal transcription against an unchanged original and verifier; it is not a discovery scanner. Keep discovery, transcription, source-byte hashing and acceptance verification as separate ledger stages.

The K04 synthetic control should be a 16-byte target-bearing block in a differently named native/container member, not the current text ACK. The K08 synthetic control should be a whole caption in an arbitrary-name sidecar/structured document, with the exact normalized HMAC16→SHA-256 commitment and source hash/path reported. Include the contradictory-ACK case from the new fail-closed tests plus one explicit unsupported/limit case. Preserve all original targets and commitments.

I did not modify these scanner owners' files. This is a coverage review only; the external source remains unavailable in this invocation.
