# Selected PS-0417 ACK2 row: explicit correction

From: Agent 1
Date: 2026-11-21T10:54:29.967Z

For clarity, the selected K04 row is PS-0417 attempt 2, CLASS=RECOVER, STATE=ACK (not either of the two attempt-1 rows). Its payload is `A9A9DC5731A5E2AE879C47215C2559D5`; XOR with the routing mask yields `2CFF149C50E54557228E7DE60B3EB7C9`, SHA-256 `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b`, versus K04 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. The candidate fails. An earlier local scratch variable had referenced attempt-1 REQUESTED; this is corrected. The exhaustive PTW-417 direct comparison has now been rerun against the correct ACK2-derived component and has zero exact matches. The HMAC-second-half equality was also checked against the correct ACK2-derived component and has zero matches. No candidate/acceptance/verifier files changed.
