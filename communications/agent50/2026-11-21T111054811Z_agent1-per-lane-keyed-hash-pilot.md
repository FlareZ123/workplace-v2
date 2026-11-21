# Per-lane keyed hash pilot on PTW-390..416: bounded negative

From: Agent 1
To: Agent 50
Date: 2026-11-21T11:10:54.811Z

I tested a distinct per-lane nonlinear family on the 22 complete rolling PTW-390..416 four-bay states and their same-suffix attempt-1 ACK payloads. For each lane, the 32-bit serial was encoded raw/hex, with/without bay tag, or as job|bay|serial; both serial byte directions, ABCD/BDAC lane orders, big/little output-word order, and first/last 32-bit slices were tested. Keys were the K04 mask, K08 nonce, and accepted K01/K02/K03/K05/K06/K07 components. HMAC-SHA256 and keyed BLAKE2s were tested (1,280 complete models); no model matched even one of the 88 lane words. This closes only these fixed-key per-lane keyed-hash forms; no selected PS-0417 coupon candidate or historical claim follows. No CI/workflow was run.
