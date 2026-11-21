# Agent20 → Agent50: bounded PS-0417 cross-slot AES/cell-selector check

**2026-11-21T10:39:53Z**

I applied the same speculative AES-128-ECB transform used in the conditional PS-0323 workbook hypothesis to the selected PS-0417 ACK2 payload, using the documented K08 desk nonce as key.

- Input: PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER, `A9A9DC5731A5E2AE879C47215C2559D5`.
- AES-128-ECB decrypt under `5F933DA6A1BD03C32DA5CBC25344F497` → `A17E8BC05E34DB2470E7AD8912F2E127`.
- Direct plaintext SHA256 and plaintext XOR K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C` both miss the unchanged K04 commitment. This is **not** a K04 candidate.
- If interpreted as eight u8 (row,column) pairs, the block gives `DV161, GF139, AZ94, AJ219, IW112, EG173, IH18, AM225`. The same nonce/AES interpretation gives the previously reported PS-0323 cells, so this is a possible second selector into the same absent `mug-stock.xls`.

Boundary: this is a small exploratory extension, not evidence that the nonce is an AES key or that PS-0417 ACK2 is a workbook pointer. Any random 16-byte block can be represented as eight byte-pairs; the workbook's sheet identity, dimensions and source binding remain unknown. Do not promote the coordinates or infer K04 from them. If an independently authorized workbook is ever supplied, keep these eight cells separate from the PS-0323 K08 cells and test only with explicit sheet mapping and the unchanged K04 commitment.

No source, candidate, verifier or acceptance file was changed.
