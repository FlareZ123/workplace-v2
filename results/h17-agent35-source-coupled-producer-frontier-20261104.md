# H-17: cross-record producer mechanisms capable of predicting whole missing slots

**Agent35 | 4 November 2026 | source-pinned complete candidate experiments; no REC8 recovery.**

## Current target and evidentiary boundary

The original archive's six independently verified components remain **K01/K02/K03/K05/K06/K07 PASS**. Original **K04 physical coupon remains unavailable** and **K08 Emily final desk-margin exact words remain unquoted**; combined original REC8/1 is **INCOMPLETE**. These experiments preserve the original 46-file export, K04 mask, K08 nonce, original commitments, original verifier and canonical candidate. All producer tests deliberately exclude the suspect copied 0417/18:02 ACK2 payload as a fitting source. All original results are conditional on source-unattested producer assumptions.

Unlike undirected guessed candidates, the first seven investigations solve a **complete 128-bit missing packet** using historical 128-bit control blocks, exact algebra and a second evidence-layer check when available.

## New mechanisms and executed results

| Candidate construction | Original known-data calibration | Complete selected K04 packets checked | Historical full-block holdout outcome | Result |
|---|---|---:|---|---|
| **Common cross-archive GHASH-field selected-source issuer** `P(x)=A*x⊕B` | Two of five independent authentic selected 16-byte source blocks (K01, K02 prehash, K05, K06, K07 prehash), original record-label encodings | **680** | All 680 fitted source models fail all three independent remaining selected blocks | **0 K04 commitments** |
| **Same-job affine GHASH-field retry bridge** `T(x)=h*x⊕p`; source-observed pair, unobserved ACK2, later original request | 0417 A/B/C and independent 0420 U/V, exact Artin–Schreier quadratic inverse for missing whole block | **24** | 8 pair-trained models and 4 bracket-trained models fail independent full 16-byte source holds; 12 bracket roots satisfy only fitted constraints | **0 K04 commitments** |
| **Archive-keyed AES single-block header issuer** | 25 source-derived AES128/256 keys (six accepted slots, raw selected prehash, route mask, desk nonce, released office PDF AES file key and derived keys); 65 event-header plaintext encodings | **1,625** | **0/214,500** exact nondisputed original printer packet predictions; every 1,625 key/label family fails source | **0 K04 commitments** |
| **Late RECOVER ACK GHASH-field issuer** | 0448/18:24 and 0420/18:25 actual late RECOVER ACK packets, 12 event-label forms, six encodings and eight serializers | **560** | No model reproduces any of the **35** earlier genuine RECOVER ACK complete control packets; strongest accidental overlap 3 bytes | **0 K04 commitments** |
| **Late RECOVER ACK integer-ring affine issuer** `P(x)=a*x+b mod 2^128` | Same two late ACKs, exact modular congruence roots including carry and even input differences | **496**, across 306 viable of 576 source-layout hypotheses | No model reproduces any of the **35** earlier RECOVER ACK complete packets; strongest accidental overlap 2 bytes | **0 K04 commitments** |
| **Same `RECOVER/bench` destination-and-class issuer** (both GF128 field and Z/2^128 ring) | Two preserved genuine matching `RECOVER` `bench` ACKs, job0416/16:40 and job0420/18:25; selected job0417/18:02 excluded | **552 field + 356 ring = 908** | No complete packet predictions match any of **10** earlier heldout same-class/same-destination ACKs; max incidental overlap 2 bytes | **0 K04 commitments** |
| **Nonlinear GF128 quadratic same-CLASS/DEST publisher** | Three latest genuine `ACK/RECOVER/bench` blocks (jobs0407,0416,0420), 12 label forms, six encodings and eight serializers | **552** | Zero complete predictions of **nine** independently heldout same-role packets; strongest incidental overlap 3 bytes | **0 K04 commitments** |

All counts denote *complete-candidate assignments*, not guaranteed distinct coupons or statistically independent tests. Models were specified without fitting to original K04 SHA256 digest. The exact original K04 reduction in every case is `coupon ⊕ 8556C8CB6140A7F9A5123AC7571BEE1C` followed by complete SHA256 equality against the untouched recorded slot. Original printer source SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

**Synthetic positives** show each inverse can construct a full withheld packet from a genuine planted producer of its own family; this does not attest that any such producer generated the 2026 archive. Critically, two late ACK controls alone force-fit an affine issuer by construction. The 35 older-record holdouts help reject a *globally common* source writer but do not falsify an unobserved separate late-only printer epoch.

### K08 independent author-phrase construction

A distinct three-clause, scene-conditioned final-caption grammar follows Emily's original intended motifs: outside sea/window (28 clauses), inside people/table/mugs/lamp (46 clauses), end-of-night/morning (26 clauses), all six orders and independently selected eight-way connectors. The exact original K08 nonce/HMAC16/full SHA256 acceptance pipeline rejects **all 12,859,392 complete normalized phrase assignments**. The original Emily N02 draft HMAC16 control is reproduced exactly, and a synthetic in-family full phrase is found once. This excludes only the explicitly frozen authored-scene grammar; it cannot infer any literal word in the final signed margin.

## Reproducibility and evidence

- [Common source GHASH-field two-anchor test](../agents/agent35/k04_gf128_label_emitter_sft.py)
- [Quadratic exact middle-ACK reconstruction](../agents/agent35/k04_gf128_retry_quadratic_sft.py) and its [detailed report](h17-k04-gf128-affine-retry-quadratic-reconstruction-20261104.md)
- [Known-key AES issuer source controls](../agents/agent35/k04_aes_crossarchive_packet_sft.py)
- [Late two-ACK GF-field source issuer](../agents/agent35/k04_late_printer_twoanchor_sft.py)
- [Late two-ACK integer-ring exact affine inverse](../agents/agent35/k04_late_ring_affine_sft.py)
- [Same destination-and-class bench RECOVER ACK calibrated issuers](../agents/agent35/k04_bench_recov_cohort_sft.py)
- [Nonlinear three-source same-role GF128 quadratic issuer](../agents/agent35/k04_bench_quadratic_source_sft.py)
- [K08 spatial three-clause exact-phrase search](../agents/agent35/k08_inside_outside_scene_sft.cpp)

See [Agent35 persistent memory](../agents/agent35/memory.md) for source mapping, completed original counts and synthetic results. The AES test uses Python's external `cryptography` package; K08 C++17 test links OpenSSL libcrypto; remaining tests use Python standard library. All ran against the original user-supplied 46-file ZIP-extracted resources, without writing to those evidence files.

## Source-directed conclusion

The unverified copied ACK is an invalid calibration target and the late two-ACK pair by itself supplies no authenticated link to the missing physical receipt. More arbitrary byte permutations, hash constructors or field rings without an independently attested emitter relation would mostly enumerate novel numerical coupons with low evidentiary value. Similarly, Emily's N20 motifs constrain scene content but do not reveal exact final diction; a larger grammar cannot certify final words.

**High-information next step:** an independently linked *original selected attempt2 physical emission or checksum* (historical print host/escrow paper/receipt) and *exact terminal author-final margin representation* (already-preserved original envelope/underleaf/native photograph caption history). Existing source requests and acquisition caveats are recorded in [custodian intake](h17-required-additional-evidence.md). Public marketing assets, protected accounts, live facility equipment and guessed portal credentials do not provide such a source. Until a new source supplies a literal selected-stage observation or a producer/edit rule that first predicts another unseen whole control, no further K04 or K08 value can responsibly be marked PASS.
