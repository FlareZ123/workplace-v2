# K04 PTW predecessor-window cross-stream screen

**Date:** 2026-11-07 UTC  
**Status:** Negative; no K04 candidate recovered.  
**Reproducer:** [`agents/agent5/k04_ptw_predecessor_window_sft.py`](../agents/agent5/k04_ptw_predecessor_window_sft.py)

## Question

The surviving records contain 27 singleton seal receipts, PTW-390 through PTW-416, and one same-suffix printer packet for each PS-0390 through PS-0416. Each PTW record has one signed, CLOSED, AS_LEFT revision-1 serial of four bytes. Each corresponding PS record has one 16-byte payload.

This raises a narrow cross-stream hypothesis: a PS job's 16-byte component might be assembled from the four immediately preceding PTW serials. For the selected PS-0417 job, that window is PTW-413 through PTW-416. The relationship is a hypothesis; the same numeric suffixes do not establish a shared producer.

## Method

The test pins the exact source files:

- `seal-receipts.jsonl`: `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`
- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

For each complete control job PS-0394 through PS-0416, the test checks whether the observed payload equals a predicted payload under the K04 mask:

1. **Raw predecessor component:** concatenate the four prior PTW serial bytes in ascending permit order, then XOR the 16-byte result with the recorded K04 mask. Four bounded order/byte-orientation variants are also checked.
2. **Hashed predecessor components:** SHA-256 the four prior printed serial strings joined by `|`, take the first 16 bytes, and separately SHA-256 the raw 16-byte concatenation and take the first 16 bytes. Each result is tested as the K04 component under the same mask.
3. **Pre-job four-bay snapshot:** for PS-0396..0416, select the highest-numbered singleton PTW serial for each bay before the corresponding job, assemble raw A/B/C/D and B/D/A/C blocks, then XOR with the K04 mask. Also apply the exact K03 reducer to the B/D/A/C snapshot: SHA-256 of the four printed serial strings joined by `|`, first 16 bytes, then the K04 mask.

The selector is tested with a planted component/payload positive control. The selected printer row is asserted from the source fields as PS-0417 attempt 2, ACK, RECOVER, destination bench.

## Prior-art boundary

Agent8's 7 Nov 07:34 memory already records the **target-only** latest-singleton-per-bay block (B=0412, D=0416, A=0415, C=0414) and its failure against K04. This report does not claim that target candidate as new. The additional work here is the **21-control pre-job snapshot calibration** across PS-0396..0416, including the source K03 reducer applied to the B/D/A/C snapshot; all variants yield zero matches.

## Results

- All source pins and structural assertions passed.
- 27 singleton PTW receipts and 27 one-row same-suffix PS packets were present.
- The 23 complete predecessor-window controls produced **zero** matches for the raw component under the four tested orientations.
- The same 23 controls produced **zero** matches for the delimited SHA-256 component and **zero** for SHA-256 of the raw 16-byte window.
- The raw pre-job latest-per-bay snapshot produced **zero** matches across 21 complete PS-0396..0416 controls in both A/B/C/D and B/D/A/C orders. Applying the exact K03 B/D/A/C pipe-joined SHA-256[:16] reducer to that snapshot also produced **zero** matches across the same 21 controls.
- The planted positive control passed.
- Selected PS-0417 ACK2 payload: `A9A9DC5731A5E2AE879C47215C2559D5`.

For the target window PTW-413..416:

| Candidate component | Candidate bytes | SHA-256 of component | Predicted PS-0417 payload |
|---|---|---|---|
| Raw serial window | `A60B42C5645EB28CF8DD126A0C814A5E` | `c3c69ae2f9656cddbcd56301ab15e9d05450d432398783578c3ca249e22611a8` | `235D8A0E051E15755DCF28AD5B9AA442` |
| Delimited SHA-256[:16] | `AB60E5234EB8AB75452A319840DA5CF8` | `f1213ebcb1ebb6382166ad3dc61aae54e0cf0a067ef44f42c3bcc1d794065b1b` | `2E362DE82FF80C8CE0380B5F17C1B2E4` |
| Raw-byte SHA-256[:16] | `C3C69AE2F9656CDDBCD56301AB15E9D0` | `fd91b05c3084cef071574f7cb485cc31cff3f60177b533cfbb570ce174597034` | `469052299825CB2419C759C6FC0E07CC` |

Neither candidate payload equals the selected ACK2 payload, and neither component digest equals the official K04 commitment:

`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The **pre-job latest-per-bay snapshot** was tested on 21 complete controls, PS-0396..0416. The latest singleton PTW serial for each bay before the corresponding job was assembled in A/B/C/D and B/D/A/C order, then XORed with the K04 mask; both orders produced zero matches. For PS-0417, the A/B/C/D component is `F8DD126A5AD7D397645EB28C0C814A5E` (SHA-256 `eef469494783b5278d225329f5c584e220af5387c281601de74c98288378d31e`); B/D/A/C is `5AD7D3970C814A5EF8DD126A645EB28C` (SHA-256 `fb324325f058f623ad608d328ede136568ba94d65863b65df763932679df72fe`). Their masked payload predictions are `7D8BDAA13B97746EC14C884B5B9AA442` and `DF811B5C6DC1EDA75DCF28AD33455C90`, respectively; neither equals selected ACK2. The K03-reducer snapshot uses B/D/A/C serials `SG-5AD7D397`, `SG-0C814A5E`, `SG-F8DD126A`, `SG-645EB28C`. Its component is `05A0729DC148654D6A05C4618AB56ACC` (SHA-256 `62ea4e91298e26c1b26b09ee8290ecdad1de4ee4cb32b36e646262882ede0445`); its masked payload prediction is `80F6BA56A008C2B4CF17FEA6DDAE84D0`, also not selected ACK2. The reproducer prints the exact permit IDs for both orders.

## Conclusion and limits

The simple four-predecessor PTW-to-PS window, its delimited and raw-byte SHA-256 variants, and the raw and K03-hashed pre-job bay-state snapshots do not recover K04. The target-only latest-singleton-per-bay block is prior art from Agent8; this run adds a 21-control calibration for that block. This closes only these explicit cross-stream constructions. It does not authenticate a PTW-to-PS producer relationship, exclude a different source-defined transform, or replace the missing original ESC-N coupon and native PS-0417 spool object. **No K04 bits are recovered.**

Do not widen this into arbitrary hashes, permutations, or ticket arithmetic. The next useful evidence remains an authenticated native copy/queue record or the original physical coupon.
