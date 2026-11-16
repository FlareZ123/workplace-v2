# K04: V.34 answer-mode self-synchronizing scrambler, complete original commitment test

**Agent 49 | 16 November 2026. Original K04 hits: 0 / 33,554,432 complete candidate components.** No K04 bytes recovered; K08 likewise unresolved; REC8/1 still six PASS, two MISSING, combined INCOMPLETE.

## Distinct complete-object constructor

Crew note N22 jokingly describes the label printer as "thinking it is a fax machine." The previously published [V.17/V.29 scrambler experiment](h17-k04-v17-v29-self-synchronizing-scrambler-20261116.md) covers the **calling-side** polynomial `1 + x^-18 + x^-23`. The different **answer-mode** polynomial `1 + x^-5 + x^-23` is specified in [ITU-T Recommendation V.34 (02/98), §7](https://www.itu.int/rec/dologin_pub.asp?id=T-REC-V.34-199802-I%21%21PDF-E&lang=e&type=items). This report tests only this incremental alternative. The actual historical ESC-N hardware/modem protocol is **not identified** by N22, and the model is speculative.

For each of two within-byte bit orders (MSB-first, LSB-first) and each transform direction, enumerate all 2^23 possible transmitted-bit histories. The *descrambler* computes `d[n] = s[n] XOR s[n-5] XOR s[n-23]`; the *scrambler* computes `s[n] = d[n] XOR s[n-5] XOR s[n-23]`. A 23-bit basis over GF(2) and Gray-code traversal enumerate all histories without repeats. Every output is one complete 16-byte coupon; XOR the original K04 route mask and compare the **full SHA256** digest of the resulting 16-byte component against the immutable original target.

Pinned primary source `resources/evidence/print/spool-reconstruction.log` SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Exact selected row is 3 Oct 2026, 18:02 UTC, PS-261003-0417, ATTEMPT2, ACK, RECOVER, copied payload `A9A9DC5731A5E2AE879C47215C2559D5`. Route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. Authentic K04 full target SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. Source paths and exact fields are asserted by the reproducer.

## Completed execution

| Branch | Complete 16-byte candidates | Original SHA256 hits |
| --- | ---: | ---: |
| MSB-first / descramble | 8,388,608 | 0 |
| LSB-first / descramble | 8,388,608 | 0 |
| MSB-first / scramble | 8,388,608 | 0 |
| LSB-first / scramble | 8,388,608 | 0 |
| **Total** | **33,554,432** | **0** |

The same complete-candidate hash search recovered **exactly one** planted 16-byte synthetic component at hidden-history state `0x5A3C12`. Synthetic transmitter↔receiver round trips passed in both bit orders; basis reconstructions agree with independently computed full recurrences at seven states in each branch. Each original branch completed with the exact state count and zero matches. Four branches took 16.504, 16.693, 16.403 and 16.173 seconds respectively in the original local execution, with a distinct 16.906-second full planted-positive test.

**Reproducer:** [Agent49's source-pinned portable Python SFT](../agents/agent49/k04_v34_answer_mode_sft.py), standard library only. Its first argument may be `synthetic`, `msb-descramble`, `lsb-descramble`, `msb-scramble` or `lsb-scramble`; no argument executes the planted control and all four original branches. The repo script uses `resources/` and accepts the unpacked ZIP's `evidence/` form by placing the script inside the unpacked root.

## Strict limitation and next decision

This is a **bounded negative** of a specific previously untested answer-mode scrambler hypothesis. It leaves unspecified bit phases, modem framing, an unknown copier transform, other producer mechanisms, and the original physical ESC-N coupon untested. It supplies no independent proof of the historical printer's encoding. Do not infer any K04 selected bit or K08 final-caption word from the negative result.

The next meaningful K04 advance needs an authenticated event-stage producer/copy model that predicts an original withheld intact packet and actually determines the entire selected 16-byte coupon, or a contemporaneous physical/native event witness. Other speculative fax variants without equipment evidence offer diminishing payoff. Preserve all six accepted slots and the original acceptance commitments; no canonical candidate, source, or verifier was modified.
