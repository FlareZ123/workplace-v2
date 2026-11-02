# K04 two-internal-bit reassembly: 264,257,536 complete repairs rejected

**Agent 24 | 2 November 2026 | Conditional selected-event copy-stage hypothesis.**

## Question

Could the copied 18:02 UTC ESC-N `PS-261003-0417` attempt-2 ACK have lost two bit positions and gained two different bits at arbitrary positions, retaining the other 126 bits in order? This differs from the previously exhausted **byte** deletion/insertion model (v2 Agent7, `results/h17-k04-two-position-copier-reassembly-exclusion.md`), and from v1 Agent9's **whole-buffer edge** shifts (`results/check_h17_bit_slips.py`). The discarded source bits may lie anywhere in the 128-bit payload, and replacement bits are inserted at independently chosen destination positions; no bytes need remain aligned.

The original copied selected payload is `A9A9DC5731A5E2AE879C47215C2559D5`. The source-documented XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`. The original K04 SHA-256 commitment, preserved unmodified, is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`; printer source SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. An ACK attests job dispatch, not payload integrity.

## Exact mechanism and computation

Treat the payload as a 128-bit big-endian byte string, with bit positions numbered from its least-significant bit. Enumerate all 8,128 unordered source bit-position pairs `0 <= i < j < 128`. Remove the high position `j` first, then low position `i`. Enumerate all 8,128 unordered destination bit-position pairs `0 <= a < b < 128`; insert zero placeholders at `a` and `b`, then fill their two independent values (four assignments). For each resulting complete 128-bit candidate, XOR the original mask and check SHA-256 against the original K04 commitment.

Exact count: `8128 * 8128 * 4 = 264257536` complete assignments. Duplicate complete strings, if any, are counted as separate assignments. The source-ordered other 126 bits are untouched; the chosen model does not add arbitrary substitutions or substitutions to the mask.

Native C++17/OpenMP/OpenSSL SFT: [`agents/agent24/k04_two_bit_reassembly_sft.cpp`](../agents/agent24/k04_two_bit_reassembly_sft.cpp); SHA-256 of tested local source `a2b208291327c2d497c6979761548007182d6366c615014307fb4dd80471cccb`. Synthetic bit-deletion/insertion and exact SHA-256 mask positive controls passed. Four disjoint source-low-bit-index intervals were executed:

| Source first-deletion indices | Assignments | Result |
|---|---:|---|
| `[0,16)` | 62,162,944 | NO_MATCH |
| `[16,40)` | 77,638,656 | NO_MATCH |
| `[40,72)` | 74,387,456 | NO_MATCH |
| `[72,127)` | 50,068,480 | NO_MATCH |
| **Total** | **264,257,536** | **NO_MATCH** |

An additional independent standard-library Python single-bit deletion+insertion proof-of-concept tested all `128*128*2 = 32768` assignments with a synthetic roundtrip positive control; zero original commitment matches. This is a subset-type companion test, separate from the two-bit report.

## Interpretation

This rejects one complete-candidate **internal bit slip/reassembly** fault model, rather than the general case of printer copy damage. The original records do not attest this bit-slip failure mode; its motivation is only the possibility of shifted fragment extraction and the difference between arbitrary bit and previously exhausted byte operations. Larger slips, multiple unbounded source substitutions, different stages or producer architectures, and any independent selected physical coupon remain outside this test. **No authentic selected K04 bit has been recovered, K08 remains missing, and inherited six slots remain the only verified PASS components.** Do not interpret this as proof about physical printer operation.

The selected-event metadata-driven digest/HMAC family tested in the same invocation also returned zero K04 matches across 18,322,080 component constructions, but is retained in Agent24's memory as a weaker, historically unattested candidate-generation pilot rather than promoted to a separate headline.

## 2 November independent bit-127 boundary fix

The initial C++ insertion helper could form a shift by 128 when the second inserted bit position was 127. The [corrected canonical SFT](../agents/agent24/k04_two_bit_reassembly_sft_fixed.cpp) explicitly returns zero for this vacated shifted high part at that position. To independently close that edge, a native read-only scan restricted to `b=127` reran all 4,129,024 possible source deletions / first insertion coordinates / inserted-bit patterns. Synthetic positive PASS; original K04 commitment matches **zero**. The original non-edge scans cover all `b<127`. Together these exclude the stated two-bit repair class without relying on undefined C++ shift behavior. The prior source and verifier files remain unchanged.
