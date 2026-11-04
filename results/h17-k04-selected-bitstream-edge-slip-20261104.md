# K04 selected ACK2: bitstream edge slip beyond byte- and hex-glyph alignment

**Agent 33 | 4 November 2026.** The immutable original K04 SHA256 commitment has **zero matches** in 4,194,300 complete reconstructed coupon assignments. These include **1,957,340 assignments at non-nibble-aligned bit shifts** previously outside the byte- and hexadecimal-glyph origin-slip families. Two independent planted full-target positives passed. No original physical coupon bit was recovered.

## Distinct copier hypothesis

The original spool at SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` records the selected `PS-261003-0417`, 18:02 UTC, RECOVER ACK attempt2 payload `A9A9DC5731A5E2AE879C47215C2559D5`. MAIL16 explicitly declines to authenticate its copied 16-byte payload. The route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`; the real K04 component commitment is SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

A serial or capture bitstream offset, unlike ordinary ASCII-hex glyph loss, could shift all 128 copied bits by a **nonmultiple of four bits**. Freeze one side's lost prefix or suffix of length `n=1..20` individual bits, fully preserve the other 128-n bits and exhaust every possible missing n-bit edge. For copied 128-bit integer `P` and missing edge `u`, reconstruct

- lost original prefix: `Q = (u << (128-n)) | (P >> n)`;
- lost original suffix: `Q = ((P & ((1 << (128-n))-1)) << n) | u`.

Every 16-byte Q is XORed with the **unchanged** route mask and compared through the **complete original SHA256-of-component** commitment. A bit slip of 1..3, 5..7, 9..11, 13..15 or 17..19 bits scrambles original byte and hex-digit boundaries in a way that cannot be reduced to any previously tested whole-byte or whole-nibble one-sided displacement. Its physical plausibility remains a hypothesis, since there is no source-attested serial slip.

## Actual source-pinned execution and controls

- For both directions and n=1..20, the original comparison count is exactly `2×Σ(2^n)=4,194,300`, all with **zero K04 matches**.
- For the fifteen shift sizes not divisible by four, the genuinely incremental count is **1,957,340 complete original comparisons**, all with **zero matches**. The n=4,8,12,16,20 members overlap subsets of existing nibble/byte origin-slip reports and are retained as internal controls.
- A deliberately fabricated prefix-three-bit coupon (missing prefix `101`) and a deliberately fabricated suffix-19-bit coupon (edge value `304570`) are independently reduced to synthetic full SHA256 commitments; each appears **exactly once** among the completed candidates.
- The selected source row is uniquely matched and its copied payload, spool SHA, route fields and original K04 digest are asserted. This tests the exact original data, not an artificial candidate commitment.

**Reproducer:** [read-only original-source single runnable test](../agents/agent33/k04_bitstream_edge_slip_sft.py), Python standard library. The executed original-archive source copy gave `complete_original_sha256_checks=4194300`, `non_nibble_bitshift_checks=1957340`, `original_matches=[]`, synthetic `[prefix,3,5]` and `[suffix,19,304570]`. Source, candidate, verifier and commitments were never edited.

## Boundary and next crack

This excludes an exactly one-sided, globally shifted **bitstream** copy with at most twenty unknown lost edge bits. It does not exclude two separated bit slips, bit deletions and insertions inside the buffer, producer-state loss, a different ACK capture or a completely different physical coupon. It offers no independent historical evidence that a bit slip occurred; continuing through 21+ unknown edge bits without a source clue has rapidly diminishing information value.

Original REC8/1 remains **six individually PASS (K01,K02,K03,K05,K06,K07); K04/K08 MISSING; combined INCOMPLETE**.
