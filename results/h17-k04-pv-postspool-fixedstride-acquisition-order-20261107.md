# K04: acquisition-time ordered HST PV fixed-stride screen against source-conditioned postspool MT

**Agent 1 | 7 November 2026 | original fixed-stride family rejected, no original coupon recovered.**

## Recovery question and exact boundary

The [recent chronological HST screen](h17-k04-pv-postspool-acquisition-chronology-20261107.md) established that 112 historian PV records are acquired *after* the last surviving printer packet and cannot be treated as consecutive in **seq** order. Here we test an additional, **complete-sequence** producer hypothesis: after the last printer native word at p951-model stage 966, one common CPython MT19937 stream emits each three-decimal historian PV as `round(12 + 76*random.random(), 3)`, with a fixed number of native-word calls between successive PV samples. The model need only match the PV values; other per-row fields are omitted, so failure is a necessary-condition exclusion of this fixed-stride class.

The p951 mapping and the float formula are **hypotheses**, not attested original issuer documentation. A correct producer would enable source-calibrated predictions of the withheld K04 whole coupon, whereas matching arbitrary isolated PV prefixes cannot do so.

### Source-only calibration and target isolation

The reproducer pins the complete original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and HST extract SHA256 `3787dbd6bab3930ea5293c25a995175161a1c0d7683daad29f498026e057639f`. It reconstructs the same p951 symbolic 624-word native MT recurrence and fits every bit from **132 genuine intact 16-byte printer packets**, reaching exactly **15,365** independent source bit equations. **Row129 / selected 18:02 PS-261003-0417 ACK2 is withheld in full**, and no copied selected bytes, K04 mask, K04 commitment, candidate or K08 text participates in the screen.

For each prospective postspool stage, the source basis predicts zero or more of the first 15 high bits of a CPython two-word `random.random()` floating-point number. The actual 0.001-rounding bin can span two adjacent 15-bit prefixes; the tester generously includes immediately neighboring prefixes as additional permitted values. This can admit false matches but prevents rejecting a true producer because of float rounding at the bin boundary.

The 112 PV rows (seq100..211) are sorted by **acquisition timestamp**. The dataset contains **75 unique seconds**: 50 singletons, 14 pairs, 10 triples and one group of four. For each source stage schedule, the implementation **maximizes the possible number of PV matches over all permutations within every tied second**. A stage is considered independently informative only if the intact printer source already fixes **at least 10 of its 15 float-prefix bits**.

### Predeclared schedule family and original results

All `first_stage = 967..3000`, `native_word_stride = 2..16`, with the final PV stage within 4780, were scanned exhaustively, yielding **30,510** schedule assignments and **zero** fully supported alignments with at least 20 informative PV readings.

| Original-source result | Count |
| --- | ---: |
| Complete fixed-stride schedules evaluated | **30,510** |
| Schedules with at least 4 informative training and 15 informative held-out PV stages | **10,272** |
| Greatest informative PV matches in that credible-coverage subset | **2** |
| Corresponding example (first stage 1606, stride 6) | 2/12 training; 0/22 held-out |
| Schedules with all source-informative readings matched and ≥20 informative positions | **0** |

A model that explains only uninformative stages is not a fit: **3,006 of 3,814 postspool stages have zero known high-prefix bits** under the incomplete original printer MT state. This source-known-bit gate prevents a 100%-matching score from being manufactured by assigning records to unconstrained stages.

### Genuine generator and whole-packet controls

The standalone [source-pinned SFT](../agents/agent1/k04_postspool_pv_chrono_sft.py) confirms all **132/132 intact printer packets** byte-for-byte from the fitted source basis.

Independently, a genuine `random.Random(0x5C3E7)` generates a complete synthetic spool with the same 133 job-stage geometry, then 112 rounded PV readings at **true first stage 1011, stride 7**. It withholds synthetic selected row129, rebuilds the source-only basis and **reverses the order of values within every actual timestamp-tie group** to exercise the ambiguous-order logic. The scorer still matches all **48/48 source-informative** observations (18/18 training, 30/30 held-out). Twenty-six independent native MT recurrence controls pass as well. Thus the source chronology screen is capable of recovering a deliberately planted true schedule.

## Outcome and next decision

The original 112 historian readings are inconsistent with **every tested constant postspool native-word stride 2..16 at first stages 967..3000** for this exact p951/CPython/`12+76u` model whenever the source predicts at least 20 informative values. This goes beyond an isolated stage prefix coincidence and respects timestamp ties. It does **not** eliminate a variable per-record call schedule, extra hidden calls, an independently reseeded historian, another float transformation, another RNG, or another printer chronology.

The earlier Agent 1 [same-job direct word-quantizer screen](../agents/agent1/k04_hst4_pv_printer_direct112_sft.py) excluded 30 direct same-record encodings. The present test is an independent *postspool shared-state* screen with source-conditional predictive bits, not an extension of direct quantizer offsets. The prior [Agent 50 postspool study](h17-k04-pv-postspool-acquisition-chronology-20261107.md) enumerated individual feasible PV stages and a longest ordered chain. This test additionally runs a full fixed-stride whole-sequence fitting criterion with independent source-bit coverage, all tied-second assignments and a planted 112-record positive.

The authentic 18:02 physical coupon remains **0 independently recovered selected bits**, and Emily's final keeper caption remains without attested exact words. Official six individual PASS, K04/K08 MISSING, combined **REC8/1 INCOMPLETE**. Original files, acceptance commitments, verifier and canonical candidate are unmodified.

**Next productive switch:** require an independently source-defined *variable* call/issuer schedule or a preserved native/physical output that can independently tie a complete future/held-out object to its producer. Merely widening fixed strides or reordering historian seq values would repeat a falsified condition.
