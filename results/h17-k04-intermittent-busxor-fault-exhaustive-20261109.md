# K04 intermittent uniform XOR copier fault, exhaustive 16-byte screen

**Agent 17 | 9 November 2026 | Source-pinned original K04: no match.** Six REC8 slots remain accepted. K04/K08 and combined key unresolved.

## Model

The selected ESC-N 0417 18:02 RECOVER/ACK2 copied 16-byte packet is A9A9DC5731A5E2AE879C47215C2559D5. The original route mask is 8556C8CB6140A7F9A5123AC7571BEE1C, and the copied component is 2CFF149C50E54557228E7DE60B3EB7C9. That copied component does not pass original K04 SHA256 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

Hypothesis: a copier/export bus intermittently applies one unknown **fixed nonzero 8-bit XOR error** to any nonempty subset of the sixteen source bytes. Each affected byte receives the SAME delta, whereas each unaffected byte is unchanged. Reduce the reconstructed complete coupon through the unchanged original K04 XOR mask and test its entire original SHA256 commitment.

This fault family allows from one through sixteen corrupted bytes, including more than seven bit errors. It is structurally different from the earlier low-Hamming-weight bitflip shells, globally uniform copier transforms and independent-byte donor mosaics. Its physical existence is speculative because the source lacks a verified original selected paper coupon.

## Source and complete execution

Original archive source pins: spool SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083; recovery route SHA256 f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5; acceptance SHA256 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f. All are checked by the standalone test.

For each of 255 nonzero byte-error values, every nonempty sixteen-position mask is visited by Gray-code enumeration. The 16-byte output is fully constructed on every step. The SHA256 source commitment is used only to check complete original candidates; no target-driven fitting or edited acceptance is involved.

| Scope | Observed value |
| --- | ---: |
| Byte-error values | 255 |
| Position masks per error | 65,535 |
| **Distinct complete K04 candidates** | **16,711,425** |
| Original K04 exact SHA256 matches | **0** |
| Planted full-candidate positive (delta 0x93, mask 0x4A35) | **1, PASS** |

The planted positive builds a separate synthetic commitment from an independent fixed error/mask assignment and must be recovered exactly once; it was. The [source-pinned standard-library SFT](../agents/agent17/k04_intermittent_busxor_fault_sft.py) has been committed; a local execution with the unmodified attached 46-member ZIP reproduces the same full counts.

## Interpretation

This exact intermittent one-error-symbol class is excluded. Multiple independent bus-error values, another production stage, a missing authentic paper coupon or incorrect source mask remain outside it. No new K04 byte or K08 author-final word has been authenticated. Expanding to arbitrary per-byte errors without a real capture-stage witness would be an unstructured 128-bit preimage search.

Canonical candidate, source, routing, acceptance and verifier were left unchanged. **K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; REC8/1 combined INCOMPLETE.**
