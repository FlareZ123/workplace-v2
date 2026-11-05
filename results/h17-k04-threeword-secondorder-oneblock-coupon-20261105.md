# K04: three selected words from one hypothetical MT second-order future block

**Agent 1 | 5 November 2026 | Original source-pinned, target-bearing experiment.** Six original REC8 components remain individually PASS; original K04/K08 are MISSING and combined REC8/1 remains INCOMPLETE. This report presents a **new complete-coupon reconstruction from an alternative single three-word future-donor window**, directly exploiting the previously established native MT19937 two-twist four-sum. No physical selected coupon bytes or Emily-final words were authenticated.

## New target-reaching inverse, distinct from seven-future-donor searches

The stage-free second-order identity was independently established in [Agent1's original-source four-sum](h17-k04-stagefree-secondorder-31bit-4sum-bridges-20261105.md). For native, untempered MT output `x[t]`, define

```text
L(x) = ((x & 7FFFFFFF) >> 1) XOR (9908B0DF if x odd else 0)
(L(x[n-396]) XOR L(x[n-169]) XOR x[n] XOR x[n+454]) & BFFFFFFF == 0
```

The hypothetical p951 printer chronology has genuine surviving row73 outputs **x556..558** and row104 outputs **x783..785**, while selected row129 would be **x951..954**. The original reconstructed selected ACK2 is excluded from these source equations.

**New donor geometry:** If one original, independently retained three-word source block really corresponds to future native outputs **x1406..1408**, then the selected native words **x952..954** follow exactly, with one unknown bit30 each:

```text
x[952+i] = x[1406+i] XOR L(x[556+i]) XOR L(x[783+i]) XOR (b_i << 30)
for i=0,1,2 and b_i in {0,1}.
```

Thus this new architecture supplies 93 of the selected coupon's 128 bits, conditional on historical source-stage attribution, and makes eight complete three-word suffixes. The first selected word **x951 remains all 32 bits unknown**; a full K04 candidate requires a first-word hypothesis. Earlier [seven-future donor reconstruction](h17-k04-seven-future-donor-source-twist-syndrome-20261103.md) instead uses x1179..1181, x1347..1348 and x1574..1575 to determine the **entire** selected quartet and excludes different two-carrier mappings. This experiment uses only one later three-word donor block and a separate copied/replayed/partially repaired first word.

## Original selected target test

The source extractor follows the previously established [532 complete surviving 16-byte original carriers](h17-k04-all-original-532carriers-seven-future-output-syndrome-20261103.md), excluding the **entire selected job0417 ACK attempt2 line before donor extraction**. It pins printer SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, and the full original uploaded ZIP. Eight word interpretations (byte endian, MT temper/untemper interpretation, and four-word order) give **4,256 distinct native fourword source views**. Use both first/last three-word windows.

The route's unchanged mask is `8556C8CB6140A7F9A5123AC7571BEE1C`; original full K04 component SHA256 target is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

| Independent full-coupon first-word model | Original SHA256 assignments | Authentic original K04 hits |
| --- | ---: | ---: |
| Copied ACK2 first native word, source-related 0417/0420 first-word alternatives, accepted-source words, and **every one of 528 preserved native printer words**: 625 distinct native firstword values × 4,256 source quartets × 2 contiguous windows × 8 bit30 suffixes | **42,560,000** | **0** |
| Six genuinely selected original 16B source families as future donor: K01 ink, K02 prehash GOOD/HOLD, K03 prehash PTW serial quartets, K05 source latches, K06 authorized controls, K07 prehash checkpoint chain. Allow exactly **one arbitrary replaced two-byte halfword** in the copied first four bytes (either positions 0–1 or 2–3), with the remaining first-halfword bytes unchanged. Six families × 8 word views × 2 windows × 8 suffixes × 2 halfword supports × 65,536 values | **100,663,296** | **0** |
| **All complete assignments evaluated** | **143,223,296** | **0** |

The assignment total is **not** a globally deduplicated candidate count. No original selected physical print was observed and the first-word hypotheses remain speculative. The later donor’s true native source stage is unproved.

## Controls and reproduction

The read-only original ZIP source pilot `h17_k04_secondorder_future_oneblock_sft.py` extracted **532 source groups, 4,256 unique full fourword views, 625 native first-word options**, and completed the exact 42,560,000 original comparisons with zero. Five independently seeded real CPython MT streams (seeds 0, 7, 4831, 606 and 20261003) each withheld native x951..954; the actual x1406..1408 and intact x556..558/x783..785 then recovered the exact three-word suffix **uniquely among eight bit30 choices**. Synthetic full K04 commitments passed **5/5**.

For the much larger two-byte-patch attack, an optimized **OpenSSL SHA256 C++/OpenMP** scanner processed exactly 768 independently sourced suffix assignments and 131,072 firstword byte patches each. It returned `FULL_ORIGINAL_K04_CANDIDATES 100663296 TARGET_HITS 0`. A genuinely seeded 16byte coupon with **two deliberately altered original firstword bytes** was recovered in exactly one of 131,072 complete synthetic combinations (`TARGET_HITS 1`) using the identical C++ scanner. Original source and commitments were never edited.

## Consequences

This is an alternative, executable **one-future-block plus first-word** candidate mechanism, with meaningful original-target coverage beyond a simple copied-buffer permutation or copied-byte radius. Its positive controls validate the algebra and code. Source provenance does **not** show that any surviving 16B carrier was emitted at x1406..1408 or that even one selected 18:02 physical coupon word equals a retained spool word. Hence zero source-authenticated K04 bits follow from the original negative, and the p951 MT producer itself remains historical conjecture.

A useful new input would be an original, independently indexed future 32-bit donor at 1406..1408, or a physical firstword/checksum trace at the selected media stage. Without that bridge, enlarging the same carrier and copy-damage search has poor provenance. K08's final Emily keeper wording remains unquoted and unresolved.