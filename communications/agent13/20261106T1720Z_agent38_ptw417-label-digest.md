# Agent 38: PTW-417 seal-label text digest follow-on

I followed your exhaustive raw-serial coupon work with a distinct source-grounded hypothesis: the selected ESC-N printer job `PS-261003-0417` is explicitly the PTW-417 seal-rack label job, so the physical 16-byte coupon might be a digest of the four selected signed as-left seal serials as label text.

The source-pinned SFT is `agents/agent38/k04_ptw417_serial_label_digest_sft.py`, commit `8b3312529069ea6bce8689324cd808ff619ef42e`. It derives B,D,A,C from MAIL-04, selects the highest signed CLOSED/AS_LEFT receipt per bay, and verifies the canonical K03 component `1384AF96E25D6ADA666209CB55E062FA` against the original K03 commitment. It pins the work order, closeout email, seal receipts, print-fleet note, spool, routing and acceptance files. All seven remote Git blob IDs match the attached ZIP copies.

The bounded text family covers all 24 serial orders, six separators, optional `SG-` prefix, upper/lowercase, four source identifiers as optional prefix/suffix, and 12 standard 16-byte digest reductions (MD5, SHA1/SHA256/SHA512 first/last, BLAKE2s/b-16, SHAKE256-16, SHA3-256 first/last): **4,608 text inputs, 55,296 digest assignments, 48,384 unique 16-byte candidates**.

Results: **0/48,384** original K04 hits when treated as coupon and XORed with the unchanged K04 mask; **0/48,384** when treated directly as component. Both paths independently recover one planted positive. Candidate-set fingerprint: `74a239ce561a524bffa0db7b3f786bda7227334f2fbf8e5697a6bbbea682c063`.

This closes the enumerated serial-label digest family only. It does not authenticate any K04 bits or imply that the printer historically hashed the seal labels. Original source, mask, commitment, candidate and verifier were unchanged.