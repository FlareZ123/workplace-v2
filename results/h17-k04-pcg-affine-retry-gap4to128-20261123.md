# K04 selected-job two-flank inverse: variable-spacing 64-bit affine PCG writers

**Agent 50 | 23 November 2026 | Exact complete-coupon reconstruction test, negative under the named producer.** Original six accepted slots remain K01/K02/K03/K05/K06/K07. Neither selected physical K04 coupon nor author-final K08 phrase is recovered.

## Source-specific question

The original spool retains **RECOVER REQUESTED attempt 1** at 18:01 UTC, disputed selected **RECOVER ACK attempt 2** at 18:02, and **RECOVER REQUESTED attempt 3** at 18:03 for the same PS-261003-0417 job on ESC-N. Could the two intact request payloads bracket the missing two-output ACK2 coupon under a per-job invertible 64-bit PCG-style output permutation and one affine emitter state? This would construct a complete physical coupon without trusting the copied ACK2 bytes.

The prior [invertible PCG ordinary-packet study](../agents/agent29/k04_pcg_reversible_heldout_sft.py) inverted within-packet output pairs and tested a fixed PCG multiplier or a globally calibrated affine transition. This test instead uses the two specific selected-job request flanks, permits an arbitrary state multiplier and increment, and allows a variable native output gap. It does not infer continuity from the ordinary-job population. A REQUESTED spool entry is not an authenticated physical coupon.

## Exact inverse and finite search

Original 133-record spool SHA256: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Extract 16-byte REQUESTED payloads at indices **128** and **130**. Identify index **129** from job/attempt/state metadata and **never decode its copied PAYLOAD** when fitting the producer.

Each request supplies two 64-bit outputs. Test both byte orders and both native word orders. Invert either of two bijective PCG output permutations, **RXS-M-XS** or **XSL-RR-RR**. Each layout yields candidate native states (s0,s1) and (sN,sN+1).

Under one unknown 64-bit affine law s[i+1] = a*s[i] + c modulo 2^64, assume ACK2 uses the consecutive output states s2,s3. Permit every **N=4..128** for the start of REQUESTED3, allowing extra hidden draws after ACK2. Subtract state equations to eliminate c:

s[N+1] - s[N] = a^N * (s[1] - s[0])  (mod 2^64).

Write t=v2(s1-s0). First require the observed right difference to have the corresponding 2-adic divisibility. Otherwise divide by 2^t, invert the odd denominator modulo 2^(64-t), and enumerate **all** roots of the resulting a^N congruence using exact one-bit modular lifting. Include even multipliers and every high-bit completion. Infer c=s1-a*s0, advance the candidate state N steps, and demand the entire independent REQUESTED3 starting state. Any surviving history gives exactly two missing output words; serialize them, XOR the original K04 route mask, and check the original SHA256 commitment. Neither copied ACK2 bytes nor the target digest enter state inference.

## Original results

| Output permutation | Byte order | Native word order | Modulus power roots | Exact whole-history issuers | Complete coupon candidates |
| --- | --- | --- | ---: | ---: | ---: |
| RXS-M-XS | little | forward/reverse separately | 62 each | 0 each | 0 |
| RXS-M-XS | big | forward/reverse separately | 0 each | 0 each | 0 |
| XSL-RR-RR | little | forward/reverse separately | 62 each | 0 each | 0 |
| XSL-RR-RR | big | forward/reverse separately | 0 each | 0 each | 0 |

**0 complete K04 candidates and 0 original commitment matches** across all **2 × 2 × 2 × 125 = 1,000** specified source-spaced model configurations. All 62 necessary roots in each little-endian layout fail full REQUESTED3 state equality. The target hash did not eliminate any otherwise surviving issuer.

**Synthetic positives:** for both output permutations, assert direct/inverse equality on four selected 64-bit states. Plant genuine 64-bit affine streams under two distinct odd multipliers at each of N=4,5,7,17,32,64,128; hide middle outputs; require exact modular lifting to recover a genuine multiplier and regenerate the later request state. All positive controls passed.

## Scope and decision

This source-conditioned exclusion covers precisely a two-output-per-request, single-state **64-bit affine writer** under those invertible PCG permutations, constant multiplier/increment, selected ACK2 placed immediately after REQUESTED1, and N up to 128. It does **not** exclude per-attempt reseeding, unrelated writer permutations, filler before the selected ACK2, non-affine state laws, greater spacing, or corrupted REQUESTED copies. There is no source attestation that the two REQUESTED payloads are genuine generator output.

No authenticated K04 coupon bit or K08 exact final-caption word is obtained. Original acceptance, source, verifier, route mask and six accepted candidate values remain untouched. Future work needs a new physically anchored copy/producer relation rather than another arbitrary affine variant.

**Reproducer:** [source-pinned single-file SFT](../agents/agent50/k04_pcg_affine_retry_sft.py), executed locally against the original supplied archive with whole-history positive controls.
