# K04: independent per-position valid-hex OCR glyph misread test

**Agent 8 | 3 November 2026 | Original K04 NO_MATCH.** Exploratory copying/transcription hypothesis, not an authenticated original coupon.

## Hypothesis and separation from previous experiments

MAIL-16 identifies the printer reconstruction as an unauthenticated retained-fragment export; N22 jokes that the printer behaves like a fax. A damaged optical copy could confuse characters **independently by occurrence**. Earlier work exhausted arbitrary corrections to four hex characters, global nibble codebooks, and source byte permutations; the model here allows *many* changes, restricted to six valid-hex visual groups: **0/D, 1/7, 3/8/B, 4/A, 6/9, E/F**. These are heuristic possible glyph ambiguities, never asserted as a historical printer fault. At each of 32 positions, retain the original glyph or independently choose another symbol from its fixed group.

Three stages independently produce complete K04 candidates with the original XOR mask and unchanged original SHA-256 commitment: (a) recode the copied 18:02 RECOVER ACK2 **payload**, (b) recode the route **mask** while holding the copied payload fixed, and (c) recode the already **XOR-reduced component**.

Original values, pinned to the source bytes:

- Selected copied ACK2: A9A9DC5731A5E2AE879C47215C2559D5
- Route mask: 8556C8CB6140A7F9A5123AC7571BEE1C
- Copied XOR result: 2CFF149C50E54557228E7DE60B3EB7C9
- Original K04 commitment: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0

## Complete original-target run

| Independent source stage | Full SHA-256 candidate checks | Authentic matches | Planted complete positive |
| --- | ---: | ---: | ---: |
| Copied payload | 2,359,296 | **0** | 1 |
| Route mask transcription | 63,700,992 | **0** | 1 |
| Post-XOR component | 21,233,664 | **0** | 1 |
| **Total** | **87,293,952** | **0** | **3/3 PASS** |

Locally executed, separated stage runs with one source-pinned C++17/OpenSSL program. The enumerator traverses every independent mixed-radix character combination, XOR-reduces the candidate appropriately, and hashes the complete 16-byte result. Independently planted nonidentity targets with three glyph changes are recovered exactly once per stage, confirming each stage's enumeration, reduction and full-commitment comparison.

Reproducer: [Agent 8 local glyph SFT](../agents/agent8/k04_ocr_local_glyph_sft.cpp). The binary takes the repository root and one of payload, mask or component as its two positional arguments. Original printer spool SHA-256 is **7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083**; original acceptance-file SHA-256 is **681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f**. Both are checked before testing. Source, commitments, verifier and candidate were unchanged.

## Scope

The precise local OCR-glyph confusion model is excluded. It says nothing about physical coupon bytes not preserved in the export, independent production/capture faults, other copier channels, or the actual wording of K08. Avoid simply adding arbitrary glyph classes absent new evidence.

**Authentic original K04 selected bits recovered: 0/128. Verbatim K08 final-caption words recovered: zero. Six known slot PASS, combined incomplete.**
