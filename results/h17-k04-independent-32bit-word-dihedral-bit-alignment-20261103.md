# K04: independent 32-bit word rotations and reflections of the disputed coupon copy

**Agent24, 3 November 2026. Target-facing complete-coupon test: 100,663,296 full SHA256 checks, zero original K04 matches.** This excludes a distinct finite 32-bit word bit-alignment fault class. It does not authenticate the source's copied ACK or supply a new selected coupon bit.

## Why this is a separate copier hypothesis

The original printer record is `evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`). The source-selected ESC-N, job `PS-261003-0417`, attempt-2 RECOVER ACK payload is `A9A9DC5731A5E2AE879C47215C2559D5`. The original `recovery-routing.json` supplies mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and the unverified XOR candidate is `2CFF149C50E54557228E7DE60B3EB7C9`. Original K04 SHA256 slot commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Earlier v2 Agent5 tested arbitrary permutations of the four **bytes** inside each of four 32-bit payload words, with word-order reorderings; Agent9 tested independent per-**byte** rotations/reversals and byte-nibble faults. Agent25 tested **global rectangular bit-raster** scans. The present model allows independent *arbitrary 0..31 bit rotations of each native 32-bit word*, with optional whole-word 32-bit bit reversal (the 64 symmetries of a 32-bit cyclic bit ring). This can move bits across byte boundaries inside each 32-bit word and is distinct from all of those fixed reassembly rules. It is an exploratory interpretation of the source's retained-fragment/fax-printer caution, not an attested diagnosis of an actual fault.

## Exact construction and execution

The source 16-byte buffer, the route mask, and their XOR have four 32-bit lanes each. For each lane independently, apply one of 64 transformations: `ROL32(word,n)` for `n=0..31`, or `ROL32(BITREVERSE32(word),n)` for `n=0..31`. Reassemble the original lane order in either little- or big-endian 32-bit word view. This produces six model families, each exactly `64^4 = 16,777,216` complete candidates:

| Transformed stage | LE full checks | BE full checks | K04 accepted |
|---|---:|---:|---:|
| PAYLOAD, XOR unchanged mask | 16,777,216 | 16,777,216 | 0 |
| MASK, XOR unchanged copied payload | 16,777,216 | 16,777,216 | 0 |
| COMPONENT, direct rotation/reflection of original XOR | 16,777,216 | 16,777,216 | 0 |
| **Total** | **50,331,648** | **50,331,648** | **0** |

All four words for each of the three source stages and two word views have 64 distinct transformed 32-bit values, so every one of the six families has 16,777,216 **unique** candidates internally. Across families, duplicates are possible; the 100,663,296 figure counts complete tested assignments.

The [single-file C++17/OpenSSL SFT](../agents/agent24/k04_32bit_dihedral_lanes_sft.cpp) is the same model executed locally. In each of the six families, an artificial complete coupon with the fixed nontrivial lane operations `[35,7,43,19]` was independently committed by SHA256 and recovered **exactly once** when exhaustively enumerating all 64^4 assignments. The program also checks the exact source-derived XOR baseline before its sweep and compares every constructed 16-byte candidate against the complete untouched 32-byte original slot SHA256. All six original results reported `original_hits=0` and `synthetic_positive=1`. Local SFT SHA256 `7ceecb20484f0c913ad90c4118aee78419c1c7bb48685d7f19ea29aec47d10e5`.

## Scope and next direction

This negative closes arbitrary independent 32-bit word rotations/reflections of the **recorded** buffer, the mask, or their XOR. It does not extend to erased bits, unknown inserted values, cross-word shifts, a different historical source object, incorrect route provenance, or a genuinely different generator. It is not evidence of a hardware design involving 32-bit cyclic lanes. The selected copied ACK remains uncorroborated by an independent media checksum, and the exact printed coupon remains missing. There is no new K08 author-final wording. Original six individual slot PASS and combined REC8 INCOMPLETE remain unchanged.

A more productive follow-on would need an independent control identifying which stage/word alignment actually occurred, or an original selected-stage donor. Unbounded wider bit scrambles without source selection will merely enlarge this finite search.
