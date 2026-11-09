# K04: selected copied ACK2 four-word independent rotation and rearrangement

**Agent 46, 9 November 2026. Original K04: NO_MATCH under the tested copying model.**

## Concrete recovery mechanism

MAIL-16 describes the printer spool as a reconstruction from retained fragments and warns that acknowledged dispatch does not certify payload-byte integrity. If those fragments were four 32-bit words copied at the wrong bit alignment, each original 32-bit word could be independently circularly shifted before four-word assembly. This could change nearly every byte while leaving each original word's bit multiset intact. **Prior-art correction:** Agent24 already completed the stronger independent 32-bit per-word rotation/reflection test *without changing whole-word order* (100,663,296 original tests, zero accepted). The increment here is **permuting the four whole words after the independent rotations**, enabling cross-word movement. This model still overlaps some earlier byte-permutation and 32-bit dihedral families. It is an exploratory interpretation of a possible retained-fragment fault, not evidence that a bit-alignment failure actually occurred. The original printer does not explicitly attest word rotation or this particular bit-copy failure mode, so this is conditional exploratory recovery.

Source: SHA256-pinned original `resources/evidence/print/spool-reconstruction.log`, checksum `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

Selected source header: `PS-261003-0417`, `ATTEMPT=2`, `STATE=ACK`, `CLASS=RECOVER`, unique r129. Copied selected buffer is `A9A9DC5731A5E2AE879C47215C2559D5`, whose physical integrity remains unverified. The original XOR mask is `8556C8CB6140A7F9A5123AC7571BEE1C`, with unchanged K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

For **each** endian presentation (little and big), independently rotate each of the four original 32-bit words by any count `0..31`; assemble in each of the `4!=24` complete word orders; serialize back in that endian presentation; XOR exactly the original route mask; compare SHA256 of every resulting complete 16-byte component against the unchanged K04 digest. Opposite rotation directions are included because left rotations by 0..31 cover all right rotations.

This covers **2 × 32⁴ × 24 = 50,331,648 complete original target checks** without changing the route, mask, verifier, acceptance, canonical candidate, or source archive. **2 × 32⁴ = 2,097,152 assignments** with identity whole-word order are subsumed by Agent24's existing per-word rotation family; **48,234,496 assignments** use nonidentity whole-word orders and extend that prior coverage. Further duplication with other mechanisms is possible and not deducted.

## Completed original execution

The original supplied export was inspected read-only and its source fingerprint verified. Locally compiled C++17/OpenSSL SFT executed the full assignment space in **26.24 seconds**, returning:

```text
ORIGINAL_SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
COPIED_ACK2 A9A9DC5731A5E2AE879C47215C2559D5
PLANTED_COMPONENT B95CF12FCA94F3170FF4100EDA32FB6B
PLANTED_HIT mode=0 rotations=7,3,19,11 perm=2031
ORIGINAL_CHECKED 50331648 POSITIVE_CONTROL 1 ORIGINAL_HITS 0
```

The planted positive is an independently computed *whole* 16-byte component obtained under little endian, rotations `(7,3,19,11)`, and source-word permutation `(2,0,3,1)`. It was detected **exactly once** by the same K04 XOR/SHA256 loop. This validates enumeration and full target checking; it does not authenticate a historical rotated-copy mechanism.

[Portable source-pinned executable](../agents/agent46/k04_word_rotate_permute_sft.cpp). The committed source uses equivalent enumeration, synthetic control and original-source assertions. This report records the observed original attached-ZIP execution.

## Scope and next model

The K04 commitment rejects this entire finite 32-bit independent cyclic-word fault family of the disputed copied packet. A physical source from a different stage, a truly independently authenticated coupon, an indexed producer capable of predicting complete retained sibling ACK controls, or arbitrary nonrotation corruption is outside the search. The complete word-permutation extension is incremental beyond [Agent24's prior 32-bit dihedral test](h17-k04-independent-32bit-word-dihedral-bit-alignment-20261103.md). This scoped result supplies **zero authenticated K04 selected coupon bits**, no K08 author-final words and no seventh individual acceptance. The six original PASS components and combined REC8/1 INCOMPLETE state remain unchanged.

Further arbitrary copy fault expansions are low-value without a source discriminating the copying stage or selector. The next distinct opportunity is an alternate selected *object* or an independently modeled **whole historical printer job** predictor, rather than a larger transformation neighborhood of this same retained r129 byte string.
