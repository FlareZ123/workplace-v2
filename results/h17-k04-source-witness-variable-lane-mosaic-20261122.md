# K04: complete original-coupon recovery by source-observed variable-lane MT witnesses

**Agent 19 | 22 November 2026 | 960 complete K04 source-derived candidates; 0 original acceptance matches.** Original six recovered slots unchanged; K04 and K08 missing; combined recovery INCOMPLETE.

## Target-reaching mechanism

The preceding rigid **four-word-per-witness** experiment imposed a single MT19937 recurrence across an entire unknown packet. This new producer relaxes that assumption in a *source-selected, finite* way: different selected target lanes can be constructed from **different observed original historical fullword recurrence templates**. It is an explicit complete-coupon test, not merely a partial-word correlation.

Parse the authentic 133-row `spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Identify the selected `PS-261003-0417, 18:02Z, ATTEMPT=2, ACK, CLASS=RECOVER` as raw row129 and omit its payload field *before decoding*. Interpret the remaining 132 intact packets as four little-endian tempered MT19937 outputs per packet. The actual source supports **25 chronological fullword recurrence equalities**, each described by `(r,p,k,i,l,q)`, with `r<k<l`, lane `p=1..3` and `i,q=0..3`:

`native[l][q] = native[k][i] XOR twist(native[r][p-1], native[r][p])`

Keep each historical equality's **literal, target-independent signature** `(k-r,l-r,p,i,q)`. The 25 equalities yield 23 distinct signatures and five raw physical-row offset pairs: `(52,83)`, `(53,83)`, `(53,84)`, `(53,87)`, `(54,84)`. The `(53,87)` offset fixes the initially published `(53,86)` filtered-index mistake in the separate rigid whole-packet study. No source records establish the real global stream epoch, serialisation or which (if any) independent templates were used for the selected physical print.

For the selected missing row `l=129`, transplant each observed signature by setting `r=129-(l_old-r_old)` and `k=r+(k_old-r_old)` and calculate its complete 32-bit predicted value at native target lane `q` using the two intact source packets. This yields **4**, **5**, **6**, and **8** distinct possible native words for target lanes 0..3. Since every lane has at least one candidate, form their Cartesian product, temper the words, serialize four words in little-endian byte order, XOR the unchanged original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, and SHA256-check each **complete 16-byte masked component** against untouched original K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Original target result: exactly 4 × 5 × 6 × 8 = 960 whole-coupon assignments; 0 K04 SHA256 matches.** The full candidate space includes source-mosaic mixtures of different antecedent row pairs, so the complete-model test is strictly wider than the five rigid whole-packet constructors in the prior report. A deterministic four-lane planted missing packet and its full synthetic masked SHA256 commitment are reconstructed by the identical lane-template candidate constructor; a deliberately altered planted byte fails.

The distinct tempered original-source candidate words (in raw packet lane order) are:

| Selected native lane | Tempered 32-bit candidates |
| --- | --- |
| 0 | `D1E6BAC8`, `DB06D430`, `F66CCB56`, `633A0042` |
| 1 | `3FD06497`, `702F9E57`, `A47F932C`, `8B87CE68`, `F66CCB56` |
| 2 | `D1E6BAC8`, `2151621B`, `CF17A36F`, `65C10F1C`, `8B87CE68`, `11DBC9AD` |
| 3 | `D1E6BAC8`, `C4F5A40E`, `CF17A36F`, `DB06D430`, `985D46E5`, `711378B1`, `4D732B46`, `11DBC9AD` |

## Intact-source blind predictive control

For each original intact row `h`, remove all discovered witnesses with any endpoint equal to `h` **before learning transferable templates**, then apply the remaining original templates to `h` using only earlier intact packets. This yields:

| Original heldout metric | Result |
| --- | ---: |
| Intact rows eligible for at least one lane prediction | 49 |
| Rows with all four target lanes having one or more candidates | 49 |
| Entire four-word exact packet matches | **0 / 49** |
| Actual native words present among their lane's predicted sets | **4 / 196** |

**The four word hits are closely dependent, rather than four independently discovered structural corroborations.** They are the two repeated historical signatures `(54,84,1,1,2)` and `(54,84,2,2,3)` shared by the source packet-row triplets `(8,62,92)` and `(12,66,96)`. Holding out row92 still permits the exact same signature from row96, and vice versa. Both rows' lanes 2 and 3 are recovered by those twin signatures, explaining all four hits. No other lane is blindly recovered. A reasonable correction is to describe the 25 witnesses as containing patterned duplicated scalar relations, with weak predictive transfer outside those twins. This supplies no authenticated target bytes.

## Decision and reproducibility

**The source-observed, independent-lane fullword MT producer cannot produce the accepted K04 under the defined actual-row, little-endian, selected-coupon model.** All 960 complete original candidates fail; no generator seed, authenticated selected row, or physical coupon is inferred. Independent per-target-lane template assignment is an exploratory packet production rule, not one stated by the original printer records; no claim about the historical actual writer follows. More complex lane patterns or unstated source-stage shifts remain open without a new source-defined selector. Do not repeat this exact 960-member set or inflate the four dependent heldout words into an accepted coupon.

Read-only, standard-library, self-contained source-pinned SFT: [`agents/agent19/k04_mt_witness_lane_mosaic_sft.py`](../agents/agent19/k04_mt_witness_lane_mosaic_sft.py). The program independently re-discovers all 25 historical fullword witnesses, verifies the five raw-row geometries and source hashes, constructs and SHA256-tests all 960 complete K04 components, performs all 49 source-blind holdouts, checks all four dependent word matches and runs the synthetic full-coupon positive. `candidate.json`, routing, evidence, verifier and acceptance are unchanged.