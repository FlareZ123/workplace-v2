# K04: source-observed MT witness geometry projected to a complete selected coupon

**Agent 19 | 22 November 2026 | original K04 0/40 complete commitments; intact heldout 0/1,920 packet/word fits.** No seventh component recovered. This is a narrow coupon-producing hypothesis, not a known historical writer.

## Question and source anchor

The independent original spool study [Agent9's witness reproduction](h17-k04-agent9-independent-mt-reproduction-20261118.md) found 25 fullword MT19937 recurrence witnesses concentrated in five packet-row offset pairs `(k-r,l-r)`:

`(52,83)`, `(53,83)`, `(53,84)`, `(53,86)`, `(54,84)`.

Can those *observed* row-offset geometries be promoted to a rigid **four-word** recurrence constructor for the missing selected row `l=129`, deriving the entire physical coupon from two **intact** prior packets plus one unobserved predecessor state bit? This is distinct from single-word witness enumeration, the p951 source-state rank certificate, and large source-independent generator sweeps: a complete coupon reaches the untouched original acceptance commitment in one deterministic step per specified historical pair.

The actual five `r,k` pairs are `(46,98)`, `(46,99)`, `(45,98)`, `(43,96)`, `(45,99)`, in the same order as the five source geometry types. Each source row is intact and precedes selected ACK2. The test identifies the exact `PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER` row 129 by metadata and deliberately **skips its PAYLOAD field before decoding bytes**. The script SHA-pins the original spool to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Exact 16-byte constructor

Under one rigid row-alignment conjecture, the selected packet's four native MT state words `L[0..3]` are a 624-step twist successor of a source packet `R[0..3]` and a 397-lag partner `K[0..3]`. To use all four observed words of both intact packets, place the source packet at native stages `n+1..n+4`, the partner at `n+397..n+400`, and the missing output at `n+624..n+627`. The first predecessor word `native[n]` is unobserved, but the recurrence uses **only its high bit**; enumerate its two possibilities.

For `j=0,1,2,3`, set `b=R[j]`, `a=R[j-1]` when `j>0`, and for `j=0` use the enumerated predecessor MSB with other 31 predecessor bits zero (those lower bits do not enter the recurrence). Calculate

`L[j] = K[j] XOR (((a & 0x80000000) | (b & 0x7fffffff)) >> 1) XOR ((b & 1) * 0x9908b0df)`.

Untemper the two intact source packets with the exact MT19937 inverse temper; temper all four resulting `L` words, serialize them into 16 bytes and XOR the original K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C`. For each pair use four globally consistent packet views, little/big endian 32-bit words and normal/reverse 4-word order, times the two predecessor bits. This gives exactly **5 × 4 × 2 = 40 complete 16-byte original K04 candidates** against the unchanged full SHA256 target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The observation is the **packet-row offset class**, not a precise MT native-stage equality: the assumed fixed 396/623 lag and shared word orientation remain unverified. In particular, an observed scalar MT witness at a row offset does not by itself authenticate a full four-word packet successor.

## Historical holdouts and synthetic success

Before constructing the missing-row candidates, the same five offset geometries were projected to **every eligible intact original packet as a withheld destination**, excluding the missing selected row entirely. That produces exactly 1,920 complete predictions across five offset classes, source/destination rows, four word views and two predecessor-bit choices.

| Check | Actual result |
| --- | ---: |
| Historical intact 16-byte packet predictions | 1,920 |
| Historical heldout 32-bit word matches in their corresponding 4-word slots | **0** |
| Historical exact 16-byte packet matches | **0** |
| Complete original selected K04 candidates | 40 |
| Original full SHA256 K04 acceptance hits | **0** |

This sharp failure of intact full-packet holdouts is a relevant source-only warning against elevating the prior 25 *isolated scalar* recurrence witnesses to whole-packet production. It does **not** refute the original 25 scalar witnesses, a variable-lane/variable-gap MT model, or some other actual issuer.

A genuine CPython-seeded 624-word MT19937 state at one twist boundary supplies 4 observed words at positions `1..4` and `397..400`, with the full selected 4-word successor withheld at `624..627`. The exact constructor reproduces **all 128 withheld bits** when the unknown predecessor MSB is selected correctly, for all four packet byte/word views. The wrong predecessor MSB changes the expected packet. This positive validates genuine whole-object prediction, not just hash-loop correctness.

**Reproducer:** [`agents/agent19/k04_witness_two_donor_fullcoupon_sft.py`](../agents/agent19/k04_witness_two_donor_fullcoupon_sft.py), read-only Python 3 standard library, executed locally against the unchanged original preservation export. It asserts source SHA256, K04 route mask, K04 acceptance SHA256, exact selected metadata, and exact test counts. No canonical candidate, evidence, routing, commitments or verifier were modified.

## Recovery decision

For this source-derived five-geometry, two-donor, one-predecessor-bit full-packet MT hypothesis, the selected K04 coupon **does not pass** acceptance. More importantly, the rigid whole-packet producer predicts no complete intact holdout and no corresponding 32-bit word; expanding the same rigid geometry or adding equivalent serializer variants lacks an empirical source signal. To go further, require a source-discriminated packet-stage/consumption rule, a different actual selected-event constructor, or a physical/rendered source. Existing 42 scalar MT relations are genuine observations but do not solve the four-word historical packet.

The six accepted slots K01/K02/K03/K05/K06/K07 remain untouched; K04 and K08 are still MISSING; combined REC8/1 remains INCOMPLETE.