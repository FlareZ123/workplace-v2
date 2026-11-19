# K04 retained-spool XOR commitment screen (19 November 2026)

**Reproducer:** agents/agent9/k04_spool_payload_exhaustive_screen.py  
**Result:** zero of 133 retained spool payloads produces the accepted K04 commitment after XOR with the authoritative masked_component.

The script pins acceptance.json, recovery-routing.json, and the spool reconstruction log. It applies the exact K04 operation from the route file to every retained 16-byte payload:

candidate = payload XOR masked_component

The target is the accepted K04 slot SHA-256 commitment. The source-directed job PS-261003-0417 has three RECOVER records: attempt 1 REQUESTED, attempt 2 ACK, attempt 3 REQUESTED. Therefore attempt 2 is the unique last ACK for the exact job, as the route requires. Its payload is A9A9DC5731A5E2AE879C47215C2559D5; XOR with the masked component produces 2CFF149C50E54557228E7DE60B3EB7C9 (SHA-256 11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b), not the accepted K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

| Screen | Count |
|---|---:|
| Retained 16-byte spool payloads | 133 |
| XOR candidates matching K04 | **0** |
| PS-261003-0417 RECOVER ACK rows | 1 (attempt 2) |
| Source-directed candidate matches | **No** |

The script preserves all 133 payload/XOR/hash outputs for audit. This is a source-bounded negative result: the K04 component cannot be recovered from any payload in the retained spool reconstruction under the stated XOR operation. It does not justify trying alternate job IDs, non-RECOVER classes, or other transformations as replacement selection rules. The native media/coupon source remains absent.
