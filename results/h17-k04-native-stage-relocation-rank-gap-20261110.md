# K04 native printer stage-relocation entropy has an exact 5–27-bit gap

**Agent 7 | 10 November 2026 | Conditional original-source mathematical result, not a recovered coupon**

## Decisive result

Reused the existing [Agent49 native MT19937 p951 printer basis](../agents/agent49/k04_p951_symbolic_basis.py), which excludes the disputed selected ACK2 record and fits the other 132 original physical 16-byte spool payloads to an exact rank-15,365 GF(2) source basis. It is an *unverified historical printer-producer and stage-map hypothesis*, not a recovered selected record.

Evaluated **all 2,138** complete four-word native stage windows starting at −1100 through +1037 (inclusive), determining the number of independent unconstrained native bits in each 128-bit candidate output after conditioning on the original spool source.

| Free native bits | Number of possible starts |
|---|---:|
| 0 | 284 |
| 1 | 118 |
| 2 | 43 |
| 3 | 9 |
| 4 | 4 |
| **5 through 27** | **0** |
| 28 | 1 |
| 29 | 7 |
| 30 | 32 |
| 31 | 157 |
| 32 | 221 |
| 33 through 128 | 1,262 |

The only rank-28 start is **−1082**. The proposed historically selected p951 native stage starts at **951** and has rank **128**. This is a complete *stage-set exclusion* for free bit-counts 5 through 27, not a coupon commitment hit or a restriction on alternative stage chronologies/emitters.

## Recovery consequence

[Agent21's earlier rank-0..4 stage-relocation test](h17-k04-p951-source-constrained-stage-relocation.md) already enumerated all 458 low-rank starts and all **317,952** output permutations/byte-endian variants, with no authentic K04 commitment match. This new stage-spectrum observation proves there is **no hidden next tier of rank-5..27 starts** in that model and enumerated stage domain. Increasing its arbitrary low-free-bit cutoff to 5–27 cannot generate any new candidate; the next previously untested rank 28 requires 2^28 state choices and occurs at distant stage −1082, not the selected p951 stage. A new historically evidenced stage selector or a different producer model remains necessary to generate a complete K04 candidate.

## Reproduction and limits

[Source-backed SFT](../agents/agent7/k04_stage_rank_gap_sft.py) imports the original-source checksum-pinned Agent49 basis, computes full quotient rank for every stage, and asserts prior Agent21's five historical rank bins, total count, rank-28 location and selected rank. A method-equivalent independent local reconstruction of the untempered original spool basis produced this same 2,138-position distribution. The script is **source-only**: it does not read K04 mask/commitment, does not use the copied selected ACK data, and cannot recover an original coupon.

The recovered accepted six components remain unchanged; original K04/K08 missing; combined REC8/1 incomplete.
