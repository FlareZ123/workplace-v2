# K04: 128-job CLASS/DEST bitstream carrier trial

**Agent 1 | 6 November 2026 | original source-based complete K04 candidate search, no match**

## New possible recovery architecture

The original printer export has **exactly 128** consecutive ordinary five-minute jobs, suffixes `0300..0427`, each with an intact `CLASS` and `DEST` label, before five exceptional `Z`-timestamp events containing the copied selected ESC-N ACK2 coupon. Exactly 128 visible categorical records is the same width as the 16byte target. Rather than assume an MT19937 publisher or try to correct the suspicious 18:02 copy, ask whether a deliberate record-sequence encoding used those labels to carry the original 128bit coupon (or its final route-reduced component). This is a speculative steganographic interpretation of the source's fixed 128-job block, **not an attested historical encoding or physical producer**.

This differs from earlier direct *within-payload* CLASS/DEST two-bit tests (Agents35/43), top-bit MT stage-metadata oracles (Agents2/15), and Agent50's **hashes of the batch payload bytes**. It attempts complete coupon construction from the *categorical record sequence* itself, with no payload bytes required except for authenticating/excluding the selected object.

## Frozen original source

Use unchanged `resources/evidence/print/spool-reconstruction.log`, original SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, and require exactly 133 packet rows. The first 128 are all `ACK attempt1` with consecutively numbered suffixes `0300..0427`. Their `CLASS` distribution is LABEL 52, STORES 41, RECOVER 35; `DEST` store 45, bench 45, desk 38. Only those 128 ordinary records enter carrier synthesis; the copied selected 18:02 ACK2 payload from original row129 is never used in any candidate construction.

The official source mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, and the unchanged K04 slot SHA-256 target is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Candidate 16byte strings are checked both as a directly encoded K04 component (alternative representation test) and as a hypothetical source coupon XOR the mandated route mask (original route interpretation). All reductions compare the **full 256-bit K04 SHA-256**, without prefix filtering.

## Complete tested encoding families

1. **All fixed one-bit maps across the nine pairs**: for each of the `2^9=512` Boolean truth tables on `CLASS × DEST`, take exactly one bit per ordinary job in event order to build a 128bit block. Test every 128 cyclic alignment of this bitstream and four byte/bit orientations. The resulting **262,144 presentations** produce **261,122 distinct 16byte strings**. This exhaustive map includes every label-membership bit, any fixed class/destination Boolean combination, and complements, across the specified cyclic/orientation family.
2. **Multi-bit categorical representations**: all `4P3=24` injective two-bit class codebooks and destination codebooks, with both reverse and native job order, first-job origin or the job0417-derived index117, bitplane extraction, whole 32byte codeword windows, and hash or XOR-fold reductions.
3. **Interleaved joint four-bit pair encodings**: all `24×24` class/destination codebook combinations, alternative nibble order, the two job-order orientations and the two alignment origins; fixed block windows, direct folded blocks and SHA/MD5/BLAKE reductions.
4. **Entire base-three/base-nine digit streams** using all ternary label permutations or 36 paired symbol permutations, with full numeric serialization and content reductions.
5. **Literal metadata transcripts** using class labels, destinations, class/dest joins, or one-letter abbreviations, five fixed separators and both event directions, with the same 16byte reduction views.

For each multi-bit original source string, the bounded reduction vocabulary was first/last sixteen bytes, up to sixteen adjacent 16byte windows near the beginning, XOR-folding complete 16byte chunks where possible, and both digest endpoints plus reverse-digest endpoint from MD5, SHA-1, SHA-256, SHA-512, SHA3-256, and BLAKE2b. These are concrete finite encodings, not exhaustive arbitrary steganographic transformations.

| Original-data result | Exact count |
| --- | ---: |
| One-bit category-map presentations | 262,144 |
| Distinct one-bit candidate strings | 261,122 |
| Further distinct candidates from all multi-bit/literal encodings | 334,210 |
| **Total unique sixteen-byte candidate strings** | **595,332** |
| Full SHA-256 comparisons, direct plus route-masked | **1,190,664** |
| **Exact original K04 commitment matches** | **0** |

The [read-only original-source SFT](../agents/agent1/k04_spool_metadata_bitmap_sft.py) asserts these counts and performs a genuine full-candidate enumeration for a planted synthetic masked K04 value; it checks that exactly the planted 16byte candidate is recovered. The original selected K04 copied data and K08 original source are not needed to build any candidate. [Independent manual CI run 42284502719](https://github.com/FlareZ123/workplace-v2/actions/runs/42284502719) **passed** on the exact committed script revision, including the complete genuine K04 negative and planted positive.

## Interpretation and next attack

The simple and quite broad hypothesis **“128 categorical printer events were deliberately made into a fixed codebook bitstream”** produces no authentic K04 under the specified full Boolean-map/packing/reduction vocabulary. An arbitrary position-varying codebook, an unknown secret salt, or data in the original payloads rather than labels is untested and should never be called excluded by this result. The uncommitted historical provenance of the labels also means a coincident K04 digest hit would still require physical verification. Further random category-packings are low-priority absent an encoder clue; another genuinely different evidence dependency is preferable.

K04 remains without an independently authenticated coupon bit; K08 final authored wording remains unquoted; the original six other slots still PASS and the combined REC8 verifier remains INCOMPLETE. The original spool, acceptance file, route, existing candidate and verifier are unchanged.

## Extended rank-carrier test: categorical ordering rather than literal bitcodes

The one-bit/packed-symbol results above were followed by a separate, exact **combinatorial ordering** hypothesis. If the original 128 job sequence were deliberately arranged to carry an escrow coupon, its information could reside in the *permutation* of CLASS/DEST categories, instead of their literal bit codes. For each original class, destination and joint class/destination sequence, the SFT computes (a) an exact lexicographic multiset rank respecting repeated category counts and (b) a stable-sort Lehmer rank of all 128 original job indices. This second approach distinguishes original job identities even when categories repeat. Encodings vary class/destination labels, joint-pair orientation, forward/reverse job order and four anchored rotations (0, 1, job 0417 offset117, and 127). Each whole integer rank is reduced through bounded byte, text, six-digest and folding presentations, then checked against the complete original K04 commitment, directly and with the immutable source mask.

| Extended test result | Count |
| --- | ---: |
| CLASS rank parameter choices | 48 |
| DEST rank parameter choices | 48 |
| Joint CLASS/DEST rank parameter choices | 576 |
| Distinct multiset-rank 16byte values | 44,150 |
| Distinct additional stable-sort permutation-rank values | 40,022 |
| **New complete 16byte values beyond previous bitcode candidate set** | **84,172** |
| **All distinct complete source-category values, combined** | **679,504** |
| **All complete K04 SHA256 checks, direct + source-mask XOR** | **1,359,008** |
| **Original K04 commitment matches** | **0** |

The corrected and expanded [SFT](../agents/agent1/k04_spool_metadata_bitmap_sft.py) asserts every total above, including the uniqueness of the synthetically planted full-coupon candidate in the **entire** enumerated pool. The precise expanded revision `addb9b4bc563669f491264ee2d69300a0c39cad8` independently [completed manual CI PASS](https://github.com/FlareZ123/workplace-v2/actions/runs/42285233860) on 6 November at 20:05 UTC, with original direct hits zero, masked hits zero, planted control PASS.

This eliminates the **tested** fixed categorical rank and ordering carriers as well as fixed literal codebook encodings. It does not rule out an arbitrary unknown ordering algorithm, original physical coupon data, or another selected-stage producer. No authenticated K04 bit or final K08 text resulted. Earlier totals in this document are a proper subset of the definitive combined count reported here.
