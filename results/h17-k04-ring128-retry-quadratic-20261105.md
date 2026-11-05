# H-17 K04: exact 2-adic modular-ring retry reconstruction

**Agent 2 | 5 November 2026 | Original K04 commitment NO_MATCH.** This tests a new *complete unknown coupon* producer, distinct from the earlier GF(2^128) field-affine retry and the late printer Z/(2^128) two-anchor model. The selected disputed ACK2 copied bytes are excluded before parsing, and all original source files, acceptance, route and verifier are unchanged.

## Causal question and original source

The same printer job `PS-261003-0417` has an original preserved LABEL ACK at 16:45 (A), a RECOVER REQUESTED attempt1 at 18:01 (B), an unverified physical attempt2 ACK at 18:02 (missing X), and a RECOVER REQUESTED attempt3 at 18:03 (C). Another job `PS-261003-0420` supplies a STORES ACK at 17:00 (U) and RECOVER ACK attempt2 at 18:25 (V). The 0417/18:02 copied coupon bytes are withheld from all equations and SHA preparation.

Source spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original K04 route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 acceptance SHA256: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Hypothesis (not historically attested):** a common per-job retry state transition `T(z)=a*z+b mod 2^128` operated on 16-byte printer packets under some consistent byte serialization. Integer-ring carries give a different algebraic producer from GF128 multiplication, and can reconstruct the entire unknown intermediate X if surviving original before/after relationships suffice. No actual printer specification confirms this mechanism.

For each of eight invertible presentations (reversing the four 32-bit words, reversing bytes within each word, and independently reversing bits within each byte), solve the following three possible original-source constraints **exactly**, derive `X=T(B)`, then invert the presentation to produce a full hypothetical 16-byte physical coupon:

1. **Two-pair calibration:** `T(A)=B`, `T(U)=V`. Invert `(A-U)a = B-V (mod 2^128)` using its power-of-two gcd; test `T(T(B))=C` as an independent source holdout.
2. **Same-job bracket:** `T(A)=B`, `T(T(B))=C`. Invert `(B-A)(a^2+a)+(B-C)=0 (mod 2^128)`; test the independently preserved `T(U)=V`.
3. **Cross-job pair plus bracket:** `T(U)=V`, `T(T(B))=C`. Invert `(B-U)a^2+(V-U)a+(V-C)=0 (mod 2^128)`; hold out `T(A)=B`.

The quadratic inversion uses exact bit-by-bit 2-adic Hensel lifting, including even leading coefficients and all finite high-bit lifts. This is complete for the actual source coefficient families. Each fully reconstructed X is XORed with the **unchanged original mask**, and SHA256 of the full resulting K04 component is compared with the **entire untouched 256-bit original slot commitment**.

## Executed original results

| Byte presentation (word, byte, bit reversal) | Two-pair roots | Same-job roots | Cross-job bracket roots |
| --- | ---: | ---: | ---: |
| 000 | 1 | 4 | 2 |
| 001 | 1 | 0 | 0 |
| 010 | 0 | 0 | 0 |
| 011 | 1 | 0 | 0 |
| 100 | 2 | 0 | 0 |
| 101 | 0 | 0 | 1 |
| 110 | 0 | 0 | 0 |
| 111 | 1 | 0 | 4 |
| **Total complete candidate assignments** | **6** | **4** | **7** |
| **Independent whole-packet holdout passes** | **0** | **0** | **0** |
| **Original K04 commitment passes** | **0** | **0** | **0** |

The **17 complete candidate assignments** represent **14 distinct raw physical coupon candidates**, each checked through the original mask and full K04 SHA256. The absence of a common ring-affine transition satisfying even one independently held out whole-packet source event argues against this producer. It is not an arbitrary partial hash-prefix exclusion.

**Positive controls:** a separately planted genuine 128-bit `T(z)=a*z+b` source sequence with genuine before, missing, after and independent pair yields the authentic coefficients and the exact withheld complete 16-byte coupon under **all three** inverse classes. Independently formed SHA256 of that complete planted coupon XOR the unchanged mask is recovered. All original input hashes and source-event selectors pass.

Portable no-dependency [Agent2 standalone Python SFT](../agents/agent2/k04_ring128_retry_hensel_sft.py). The locally executed original-archive equivalent reports `full_candidates [6,4,7], heldout [0,0,0], distinct_full_coupons 14, original_slot_sha256_matches 0`, and all positive controls PASS. The committed version independently implements the same frozen equations and model; no separate remote CI run is claimed here.

## Meaning and next useful direction

This exact modular-ring producer is newly excluded under its specified sources, layouts and retry logic; the earlier GF128 affine experiment did not cover 2-adic carries or the same linear/bracket inverse classes. It remains speculative because LABEL ACK, REQUESTED and RECOVER ACK may belong to distinct producer stages. A genuine physical coupon could be unrelated to both the printer's original REQUESTED bytes and this shared ring transition.

**No authentic original physical K04 bits** were obtained. K08 final words are also still absent. K01/K02/K03/K05/K06/K07 stay individually PASS; K04/K08 unresolved; combined REC8/1 INCOMPLETE. Further progress needs a selected-stage physical source, an independent whole-coupon checksum/copy relationship, or an emitter supported by original records before expanding another arbitrary algebraic family.
