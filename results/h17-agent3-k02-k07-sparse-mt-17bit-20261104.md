# K04 sparse K02/K07 shared-MT producer: 17-bit complete-coupon quotient and original target rejection

**Agent 3 | 4 November 2026 | source-conditioned reconstruction, no recovery.**

## Source and hypothesis

The original printer spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected ESC-N job PS-261003-0417/18:02 RECOVER attempt2 copied ACK is **excluded** from all source fitting. The original K04 route mask is `8556C8CB6140A7F9A5123AC7571BEE1C`; the unchanged original slot SHA256 is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

This genuinely different donor pairing tests whether the source-selected K02 prehash telemetry `E1A5E474BAD7E853A2E8C71D3317D507` and eight selected K07 AX-7782 attempt2 checkpoint halfwords `8947CEDCB9CC73BAB7E87BE63302C5C9` belong to the same hypothetical MT19937 native output sequence as the printer. The selected physical coupon could then be reconstructed without trusting its disputed copied ACK. Source K07 transfer SHA256 is `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`.

The printer source model is the exact Agent49 symbolic p951 state, rank 15,365 from 132 intact rows (selected row129 withheld), target native outputs 951..954. The K02 donor quartet is hypothetically at stage1178 or1405, under 16 whole-word layouts. K07's eight original two-byte checkpoint fields are hypothesized to be high or low 16 bits of MT tempered words, with four halfword endian/direction presentations. The original archive **does not attest this shared emitter or stage schedule**; chronology is a reconstruction hypothesis.

## Rank-first then original-value discrimination

An original-target-blind rank screen searched K07 first stages 941..2500 and strides 1,2,4,8,16,32,40,48,64,97,170,227,397,624 (40,200 eligible geometry tests per K02 donor). Without K02 the lowest K04 quotient was 64 bits. After conditioning on K02, each donor had 86 geometry candidates reducing the 33-bit quotient to 16 or 17. The original K02/K07 values were then applied to these low-rank geometries, rather than exploiting the disputed selected printer bytes or the K04 target digest.

Across 22,016 source-layout/geometry cases, 21,504 were source-inconsistent. The **512 source-compatible assignments** all use K07 first stage **951**, stride **397**, a 17-bit target quotient, one of two K02 stages and the source K07 halfword presentations. All 16-bit rank geometries contradict the actual donor source values. Source-compatible assignments collapse to **256 distinct target affine cosets**, each with 2^17 complete output values.

The complete target enumerator applies the original component reduction `SHA256(physical_coupon XOR route_mask)` to every 16byte candidate, using actual source equation RHS and free-bit target basis. It tested **256 × 131,072 = 33,554,432 complete candidates**, in four disjoint 64-coset shards, **zero K04 original commitment matches**. Each shard included a planted complete SHA256 positive and passed; no original source, mask, commitments, canonical candidate or verifier changed.

## What this establishes and next step

The K02/K07 historical selection pair can mathematically reduce all 128 missing coupon bits to 17 conditional dimensions in a source-compatible hypothetical emitter. The finite original-source model is **excluded by the original K04 commitment**. No physical attempt2 coupon byte was authenticated. No conclusion follows for different K07 stride, different emitter chronology or real hardware. The nearest predecessor [Agent14's K02/K05 227-word bridge](h17-k04-k02-k05-stride227-four-latch-3bit-source-exclusion-20261104.md) tests a different source-selected quartet, stage geometry and output width, with its own separate negative. Additional K05 conditions on the **same** now-rejected K02/K07 cosets cannot rescue this model.

Use original untouched printer and transfer sources and the existing [Agent49 symbolic basis](../agents/agent49/k04_p951_symbolic_basis.py) to reproduce: extend native stage range to 5200; fit 132 original printer packets except row129; append real K02 native/tempered wholeword equations; append K07 selected halfword high/low tempered equations at stages `951+397*i` for i=0..7; reduce each target bit to a 128-bit constant and 17 GF2 effect vectors; enumerate 2^17 Gray-code coset combinations; hash complete masked coupons. The source consistency and reduced quotient must be checked before target hashing. Full local source files were retained during this run at `/mnt/data/h17work/k04_k07_mt_rank2.py`, `/mnt/data/h17work/k04_k02_k07_source_low.py`, `/mnt/data/h17work/k04_k02_k07_complete.py`; those paths are session-local, not repository artifacts.

**Official result: K01/K02/K03/K05/K06/K07 PASS; K04/K08 missing; combined INCOMPLETE.**
