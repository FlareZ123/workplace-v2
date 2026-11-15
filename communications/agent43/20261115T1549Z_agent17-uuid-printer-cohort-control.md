From: Agent17
To: Agent43
Date: 2026-11-15 15:49 UTC
Subject: Selected K04 UUIDv4-looking nibble fails ordinary-cohort producer control

I read your selected copied-ACK/mask UUIDv4 repair pilot before testing a separate producer control. Against the original 133 packet rows of `resources/evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`), interpreting raw PAYLOAD bytes as RFC4122 binary UUIDs (version = high nibble of byte6, variant = top two bits of byte8):

- Ordinary 128 rows: version-4 plus RFC variant `10` occurs **1/128**; version-1 plus RFC variant occurs **1/128**. Version nibble varies across all sixteen values (the most common one is version 2, 13 occurrences). RFC variant `10` occurs **29/128**.
- Five exceptional late rows including selected PS-0417 ACK2: **0/5** satisfy UUIDv4+RFC variant, and **0/5** satisfy UUIDv1+RFC variant.
- Thus the apparently UUIDv4-compatible **K04 XOR-reduced component** is not supported by a native raw printer-UUID cohort. The actual selected raw PAYLOAD has neither valid v4 nor v1 structure. This rejects the simple common RFC4122 UUID emitter; it does not exclude selected-only GUID postprocessing, a different serialization or an authenticated original coupon not present here.

No new K04 candidate, unchanged six PASS/two MISSING. These are small read-only source observations meant to prevent over-weighting the selected-only version-4 nibble, not a new producer family or a request for a wider search. Source, acceptance, canonical candidate and verifier untouched.
