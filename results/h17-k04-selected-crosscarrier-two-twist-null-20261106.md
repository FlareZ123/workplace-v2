# K04 selected-versus-alternative two-twist cross-carrier test (6 November 2026)

**Agent 1. Outcome: no new K04 component, no authenticated physical coupon bits.** An exploratory source-model discriminator focused on **complete selected K05/K06/K07 material** rather than wider K04 hash/candidate enumeration. The same test includes withdrawn/older/drill controls. This tests a **different two-twist 62-bit joint relation**, complementing Agent 6's individual source-bit alignment and Agent 4's first-order 227-stage donor-pair syndrome.

## Question and independent selected objects

Does any actual selected administrative four-word source record behave as the `D[0:2]` value of a two-twist native-MT19937 identity with three **intact** printer packet donors? A successful complete two-word identity would have probability about `2^-62` at a **fixed preselected site and byte orientation**, and could help distinguish shared original producers. This is a conditional hypothesis, not an assertion that the archived printer actually used the hypothetical generator.

Read immutable original `evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`), RC17 scans, the CRC-valid TRP2 recorder records and transfer CHUNK attempts. Withhold **entire disputed printer ACK2 row129** before decoding. For the printer only, use the explicitly **conditional p951 source assignment** of [Agent 1's two-twist four-sum result](h17-k04-stagefree-secondorder-31bit-4sum-bridges-20261105.md), with 132 intact 4-word packets and their printed little-endian u32 values, untempered.

The relation is `(D ^ C ^ L(A) ^ L(B)) & 0xbfffffff == 0`, where `L(x)=((x&0x7fffffff)>>1) ^ (0x9908b0df if x&1 else 0)` and the native stage offsets are `A=t, B=t+227, C=t+396, D=t+850`. Require **two adjacent** source words each for A/B/C, then predict the two adjacent D words' 62 source bits. Scan the 4-word candidate administrative object under both native little-/big-endian untemperings, and its three possible two-word windows, against all distinct printer prediction sites.

Groups: all three RC17 revisions B,C,D-draft in issued service order; CRC-valid TRP2 node49/event82 highest-sequence four-latch group plus available seq200,300,990 four-word groups; and all four AX-7778/7781/7782/7783 transfer chains, each with highest-attempt checkpoint seq0..7 concatenated to 16B. There are **11 source groups, 22 orientation variants**. In particular the actual accepted groups are RC17 C, node49 seq300..303, and AX-7782; the others are comparison sources. A raw four-word group is a source object, **not the hashed K07 slot bytes**.

## Actual original-source and controlled results

* Exactly **36** two-adjacent-word prediction sites where all A/B/C native source words are present in the calibrated printer model. **Six** have both future D words preserved in an intact original printer packet. **All six pass** the two 31-bit native recurrence checks.
* Planted synthetic CPython MT19937 history (`Random(0xC0FFEE)`) independently passes the 62-bit two-twist relation on **all 36 sites**, confirming the recurrence and staging geometry.
* **Zero** of the 22 original administrative group/orientation configurations matches any predicted D two-word block in all 62 bits. The highest observed match is **44/62**, from RC17 D-draft little endian and AX-7778 big endian (both alternatives). The best accepted-source scores are: **K06 C 41/62**, **K05 seq300 43/62**, **AX-7782 39/62**.
* To calibrate the post-selection maximum, freeze the 36 original predicted blocks and resimulate 1,000 complete 11-group × 2-orientation sets of four independent random native u32 words per group/orientation using `Random(0xA911C7)`. Null maximum range **41..50/62**, median **44/62**. **794/1,000** null sets reach at least the original 44-bit maximum. Thus 44 is not evidence of cross-source alignment.

No K04 target commitment/hash was used to select the source relation, predict donors or compare selected groups. No acceptance, candidate, source or verifier was modified.

## Scope, limitations, and next step

This is an original-data **negative for a fixed two-twist complete 62-bit donor window** under the inherited p951 source assignment and the specific native word serializations. It does **not** exclude other producer histories, noncontiguous source fields, a differently staged/captured selected coupon or unseen original records. Its score maximum agrees with chance; there is no reason to enlarge it by sweeping hundreds of arbitrary stage-offset aliases. 

The most useful distinct next step is a source-dated *selected-versus-rejected output-producing process* or an independent literal/forwarding witness for K08. Previous positive shared-MT alignments favor some nonselected/withdrawn admin source objects, so do not use their matches to infer selected K04 bits without a new causal link.

**Official state unchanged: six PASS, K04/K08 missing, combined INCOMPLETE.**
