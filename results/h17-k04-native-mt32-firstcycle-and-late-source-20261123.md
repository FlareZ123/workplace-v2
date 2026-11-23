# H-17 K04 native scalar MT32 producer reconstruction (23 November 2026)

**Agent 13. Source-only computational recovery tests.** The unmodified original REC8/1 still has **six PASS; K04 and K08 MISSING; combined INCOMPLETE**. No historical coupon or author-final phrase recovered. The source hypothesis is explicitly conditional: no original record attests native C++ `std::mt19937` as the selected printer's producer.

## Operationally relevant difference

Prior studies checked conditional MT source-stage geometries or small seed/clock windows. The new tests exhaust the **entire unsigned 32-bit scalar seed space** and search authentic printer payloads independently of the disputed PS-261003-0417 ATTEMPT=2 ACK copy. A native seed/phase matching a complete independently preserved packet, or two uncorrupted complete 32-bit words within a damaged packet, would yield a concrete full generator state for predicting possible complete K04 coupon bytes. No source seed or coupon emerged in the completed tests below.

Original `resources/evidence/print/spool-reconstruction.log`: SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The original 18:02 copied selected ACK2 bytes, and the slot mask/commitment, are **excluded from every seed fit**. The original printer source itself states payload integrity has not been independently validated.

### Completed: intact first historical printer packet

The original `PS-261003-0300` full packet is `FBBBC54356483F5864BB3F06794518A5`. The model generates scalar-seeded native MT19937, first **624 generator output starts**, allowing **24 word permutations** and **independent LE/BE orientation per word**. A planted native source seed 12345, phase 307 (also a phase-623 cross-cycle control) correctly reproduces the four permuted/mixed-endian words; its one-byte tamper rejects.

All **4,294,967,296** disjoint scalar seeds were executed in **16 × 2^28** shards: **5,007 one-word collisions; 0 complete historical 16-byte packet matches**. Reproducer: [native first-cycle source SFT](../agents/agent13/k04_mt32_fullseed_cycle_sft.cpp). No K04 SHA target was used.

### Completed: tolerate two damaged entire source words

The same first source packet was retested allowing **two of four complete source 32-bit words to survive** after arbitrary native-word permutation and per-word LE/BE orientation. A native seeded whole packet with exactly two corrupted word groups was recovered; three corrupted groups were rejected. This is a genuine full seed+phase source reconstruction model and does not use the selected ACK copy.

All **4,294,967,296** scalar seeds were executed: **5,014 original source single-word anchors, 0 qualified two-word matches**. The first eight 2^28 shards used an earlier probe loop, covering packet starts **0..620**; the final eight shards used the fixed probe extending into native outputs 624..626 and covered starts **0..623**. Consequently the original negative is complete for **all seeds at starts 0..620** and for **the upper 2^31 seeds at starts 621..623**. No exclusion is asserted for the missing first-half three-phase boundary. Source: [two-of-four original SFT](../agents/agent13/k04_mt32_two_of_four_salvage_sft.cpp). Local original logs are preserved in Agent13's research continuation.

### Direct same-job and second-cycle reconstruction

The historical same-job pre-ACK `PS-261003-0417 ATTEMPT=1 REQUESTED` has source bytes `CD3E4F216ADB2FB180DA2AA90B33F7A4`. Testing this exact sixteen-byte source against all scalar seeds in the **first 2^30 seeds at first-cycle stages 0..623** produced **zero complete packet matches**. Unlike the first historical printer packet, this input belongs to the disputed job; still, a REQUESTED record is not proof of committed printed media. [Same-job exact SFT](../agents/agent13/k04_mt32_fullseed_cycle_sft.cpp).

To reach a stage relevant to the previously modeled **p951 chronology**, an additional source-only model computes the **second complete native MT19937 twist**, then scans starts **900..980** inclusive. Both original PS-0417 ATTEMPT=1 REQUESTED and ATTEMPT=3 REQUESTED packet copies are eligible, under all fourword permutations and independent per-word endian views. The model accepts **two preserved complete 32-bit source words** from either flank; no selected ACK2 or K04 target leaks into fitting. Genuine seeded stage-951 and two-corrupted-word controls pass; three corrupted words reject. The stage range is a conditional research hypothesis, not a source-authenticated fact.

Reproducers: [single flank second-cycle](../agents/agent13/k04_mt32_request1_latephase_twoof4_sft.cpp), [dual-flank AVX512](../agents/agent13/k04_mt32_dual_request_latephase_twoof4_sft.cpp), [AVX2 fallback](../agents/agent13/k04_mt32_dual_request_latephase_twoof4_avx2_sft.cpp). Full domain independent CI matrix: [Actions run 45114911618](https://github.com/FlareZ123/workplace-v2/actions/runs/45114911618), created with CPU-feature fallback because initial run 45114730001 failed on hosts without AVX512. The CI full-domain result is pending at the time of this initial report; do not count a queued, failed or incomplete matrix as a completed exclusion.

## Status boundary

All claims above concern **specified native scalar MT19937 production and selected source serializers**. They do not establish authentic bits of the damaged selected K04 coupon, do not derive the unquoted K08 author-final margin wording, and cannot turn a synthetic source control into a historical REC8/1 PASS. The meaningful next successful observation would be an original source-seed match that reconstructs **an entire** selected printer coupon and matches the **unchanged original** K04 commitment; otherwise the absent independently authenticated physical coupon and exact final caption remain the objective.
