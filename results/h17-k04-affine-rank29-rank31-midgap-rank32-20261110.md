# H-17 K04: 25.23 billion new complete low-rank printer coupon constructions

**Agent 3 | 10 November 2026 | All original K04 commitments NO_MATCH.** These are conditional source-derived **complete 16-byte** coupon candidates. No authentic missing K04 bit or K08 author-final word was recovered. The original six other REC8/1 slots still pass and the combined archive remains incomplete.

## Distinct recovery mechanisms, not repeats of earlier rank-28 or byte-fault scans

Reuse the exact **original-source rank-15,365 MT19937 GF(2) basis** from [Agent49](../agents/agent49/k04_p951_symbolic_basis.py). The selected ESC-N/PS-261003-0417 ACK attempt2 row129 is excluded **before its copied PAYLOAD is parsed**. Each hypothetical four-native-word stage is reduced against the 132 intact printer packets. The resulting affine 128-bit coupon is then MT-tempered, serialized as four little-endian 32-bit outputs, XORed with the route's original 16-byte mask, and compared against the full original K04 SHA256 commitment for **every** remaining independent bit assignment.

This extends [Agent7's exact rank spectrum](h17-k04-native-stage-relocation-rank-gap-20261110.md) and [Agent26's sole rank-28 complete scan](h17-k04-rank28-native-stage-1082-fullhash-20261110.md). All seven rank-29 starts were previously unsearched at full target width. Six rank-31 starts are clustered in the pre-event original printer timeline. Two rank-32 starts **944/945** fill precisely the *two internal* wholeword positions in the 17:35→18:01 buffer boundary that [Agent21's four edge-stage 2^32 scans](h17-k04-adjacent-shift-one-word-exhaustive.md) did not enumerate.

### New midgap whole-packet construction

The original PS-0427 17:35 ACK packet at native 942..945 is:

\`F0DC2DDF78FFE61C33320BCB94178480\`

The original PS-0417 18:01 RECOVER REQUESTED1 packet at native 947..950 is:

\`CD3E4F216ADB2FB180DA2AA90B33F7A4\`

Position 946, between these intact packets, is an unobserved native 32-bit word. The two *complete hypothetical physical coupons* are therefore:

- **Stage 944:** \`33320BCB 94178480 [any 4 bytes] CD3E4F21\`
- **Stage 945:** \`94178480 [any 4 bytes] CD3E4F21 6ADB2FB1\`

Both are internal source-spanning splice windows. The observed 12 bytes in each are independently original-source-frozen; all **2^32** possible intermediate words are exhausted in the correct byte order. Agent21 previously exhausted only stages 943, 946, 948, 954. Thus stages 944/945 are genuinely new complete candidate families. Neither the original 18:02 ACK2 copied payload nor its apparent \`A9A9\` prefix selects an unknown word.

## Original finite results

| Conditional fourword stage rank | Newly checked stage indices | Complete SHA256 K04 candidates | Original hits |
|---|---|---:|---:|
| **29** | −1074, −1000, −965, −905, −671, −492, −486 | **3,758,096,384** | **0** |
| **31** | 925, 931, 938, 939, 940, 941 | **12,884,901,888** | **0** |
| **32** | 944, 945 | **8,589,934,592** | **0** |
| **Total** | 15 source positions | **25,232,932,864** | **0** |

These are **assignments**, not a claim of 25.23 billion globally distinct physical coupons across all stage families.

Original SHA256-pinned printer source:
\`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`

Original route XOR mask:
\`8556C8CB6140A7F9A5123AC7571BEE1C\`

Original K04 SHA256 acceptance commitment:
\`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`

Every rank-29 stage contributes exactly 2^29 combinations, each rank-31 stage 2^31, and each rank-32 stage 2^32. Exact source basis rank and all listed affine dimensions were asserted. The earlier rank-28 stage −1082 original-source base and first direction were also reproduced exactly as an independent geometry check. For both new midgap stages, every generated original-source coupon and every affine direction was checked against the twelve frozen original bytes; no printed source byte varies.

### Whole-object positive and hashing validation

For each newly tested stage, a complete independently selected coupon within its true affine space was planted at Gray-code assignment index **1337**. The exact SHA256 of that complete 16-byte component was calculated using OpenSSL's full SHA256 interface, then recovered **exactly once** from the first 65,536 search assignments by the identical optimized original-commitment compression path. All **15/15** full-coupon synthetic controls passed. The comparator uses the complete original 256-bit digest; it never treats a short prefix as a match.

A masking-stage error was detected during the initial rank-31 pilot: raw coupon bytes rather than coupon XOR mask had entered its input. Those pilot checks were **discarded** and do not appear in the table. The rank-31 and rank-32 original counts above refer exclusively to the fully rerun **correctly masked** components. The rank-29 scan had been correctly masked from the beginning. The portable generator's output was then independently compared stage by stage with the actual full-run source vectors: **all 15 bases and all directions agree exactly**.

Execution against the supplied original ZIP on 10 November 2026 completed three full groups, with zero original matches. The source and target were read-only throughout.

## Reproduction in the shared repository

- [Source-only stage generator](../agents/agent3/k04_affine_source_sft.py) imports Agent49's SHA-pinned spool basis, withholds row129, checks the original route and acceptance constants, calculates the exact affine coupon directions, checks stages 944/945 against their entire preserved source fragments, applies the **original mask**, and emits a stream of all 15 component bases and directions.
- [Optimized C++17/OpenSSL SHA256 complete scanner](../agents/agent3/k04_affine_sha256_sft.cpp) consumes that stream, tests a planted full-coupon positive at every stage, enumerates each 2^rank affine component through exact Gray-code steps, and checks the **complete** original 256-bit target. OpenMP permits local parallelism. Optional finite prefix limits are supported for smoke tests; the default is the complete 25.23-billion scan.
- Source-stream-to-full-run vector comparison: 15/15 stage bases and direction sequences identical. A portable 1,048,576-per-stage smoke test passed all 15 planted positives and checked **15,728,640** original components, zero hits. The full 25.23-billion original test used the computationally equivalent optimized C++ routines with the same source vectors, mask and target; this is a local original-data execution, **not** a separately completed remote GitHub Actions run.

## Causal limit and next decision

No source confirms that an earlier printer native stage supplied the later selected 18:02 ACK2 **physical paper coupon**, and the hypothetical p951 MT19937 stage map has not been authenticated as a printer-firmware implementation. Even a complete finite negative leaves the original selected native stage951 at **128 unconstrained bits** under the source basis, and the torn actual physical coupon remains missing.

The midgap construction rejects every canonical 16-byte paper coupon that could be formed from the two original preserved packets and their one fully arbitrary missing intermediate word, including layouts overlooked by the previous adjacent-shift report. This is a useful closure of that natural copy-boundary family. Further undirected rank-30/32/33 prehistory searches are unlikely to explain the incident-event selection without a new source witness.

**K08 is independently blocked by absent verbatim author-final words.** The original accepted six keys, selected printer record, original ZIP, route mask, commitments, canonical candidate and verifier are unchanged. REC8/1 combined acceptance is still **INCOMPLETE**.
