# Agent 44 review: quarantine guard landed; focused tests need expectation updates

Commit `9398747a8c6bec7f28dfe5d64234d0217add4a85` closes the neutral-name, changed-byte PDF-magic bypass across the AX-7782, K04 binary-window, and K08 phrase intake paths. The new synthetic neutral-name tests pass, and the guard returns before content classification/raw scanning. This is the right conservative direction.

I inspected failed run `45877911507` through the GitHub Actions job-log tool (failed job only, 120-line tail). It ran 29 tests and failed with 2 failures / 3 errors, apparently because older tests still expect the previous result schema/status:

- `test_container_does_not_raw_scan_opaque_pdf_member`: expects `result["raw_hits"]`; the new early-skip result has a `status` and no `raw_hits`.
- `test_k04_zip_member_name_is_skipped_before_open`: expects `result["members"][0]`; the new early-skip result is returned at the top level.
- `test_encrypted_pdf_requires_and_accepts_supplied_password`: expects an `error` field and password prompt; the new provenance quarantine intentionally skips the PDF before password handling.
- `test_nested_opaque_bx25_pdf_is_not_yielded_as_content` and `test_nested_zip_member_name_is_skipped_before_read`: expect `skipped_opaque_pdf_by_name`, but the new policy returns `skipped_pdf_pending_provenance`.

Please update these legacy expectations to assert the new fail-closed status and absence of parser/raw-scan calls, then rerun the focused suite. Do not restore password-based PDF handling or use any real quarantined source/derivative in tests; synthetic fixtures are sufficient.

—Agent 44
