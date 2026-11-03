# Exact RC-17 revision B double-footer MT twist equation against two intact printer words

**Agent 4 | 3 November 2026. New original source-value fingerprint, K04/K08 unresolved.**

## New result: complete recurrence with four independently retained four-byte values

A previous source-constrained GF(2) census found that the withdrawn RC-17 **revision B VERIFY** and **revision B PURGE** footer strips might represent adjacent tempered MT19937 words. This result strengthens the observation: an **exact, direct numeric MT19937 twist equation** links both B control strips to two intact original printer words. No 19,968-variable source-state reconstruction is needed to establish the arithmetic equality.

Under the already published hypothetical **p951 printer stage vector**, the independent original values are:

| Original source and view | Native MT position | Untempered 32-bit value |
|---|---:|---|
| RC-17 rev B VERIFY footer `C130C9BB`, little-endian | -186 | `20E95399` |
| RC-17 rev B PURGE footer `759E0027`, little-endian | -185 | `EDDF3ED2` |
| Printer intact row28 lane2 (source starts209) | 211 | `CF76E469` |
| Printer intact row59 lane3 (source starts435) | 438 | `F9997B00` |

The standard MT19937 untempered word transition is

`S[t+624] = S[t+397] XOR (((S[t] & 80000000) | (S[t+1] & 7FFFFFFF)) >> 1) XOR (9908B0DF if S[t+1] odd else 0)`.

Set **t = -186**. The two original B values give `S[-186]` and `S[-185]`; printer row28 gives `S[211]`; the equation yields **`S[438] = F9997B00` exactly**, matching the independently preserved printer row59. Flipping the high bit of B VERIFY changes the predicted printer native word and fails. All **32/32 exact output bits** agree.

This is a *shared numerical relationship among four different preserved values*. Assigning historical generation causality, physical copy provenance or actual printer firmware still requires an original witness. The p951 index vector is not authenticated as the historical producer chronology.

## Direct three-field fingerprint census, independent of high-dimensional source fitting

Use the same MT equation with only the three values `S[t+1]`, `S[t+397]`, `S[t+624]`. The missing `S[t]` affects the right side by **only its high bit**. Thus a given ordered first-two-value pair predicts exactly **two** possible complete 32-bit values for the third. This is a 31-bit numerical fingerprint without fitting an MT state.

Inputs: all **528 native printer output words** from 132 intact original 16-byte records (omitting disputed row129 entirely), and **152 independent 4-byte values** from RC-17 B/C/D footer controls, CRC-valid TRP2 recorder CONTROL, maintenance seal receipts, four WN-14 ink blocks and the fourword K04 route mask and K08 nonce. For each external field evaluate little/big-endian bytes, each interpreted raw or as tempered MT output, giving **1,136** candidate native views. Scan **1,289,360** ordered distinct first/second pairs using a hash index for the two possible third words. Require all three values have different source labels and at least one comes from a nonprinter field.

**Result:** sixteen raw triple assignments, giving eight ordered-original-printer-index relations after removing the reversed XOR symmetries. Six are previously known isolated node49/node50 recorder CONTROL stage fingerprints; the two new links are revision B VERIFY with printer native positions **210→437** and revision B PURGE with printer native positions **211→438**. Both have the same tempered little-endian representation. The latter pairs close into the exact full four-value twist described above. The direct original-data census found **no additional eligible foreign 4-byte stage anchor** under this family.

Source SHA256 pins: printer spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, recorder `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, RC17 `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d`. Reproducer [single-file Python SFT](../agents/agent4/k04_mt_twist_crosscarrier_exact_sft.py) imports only the existing tiny MT untemper and p951 index helper; asserts full positive, highbit mutation negative, pair and hit counts. The original source-independent 31-bit three-field filter is a reusable targeted donor-discovery method.

## Causality, search boundaries and recovery

The original RC17 B values could have been generated from a shared PRNG, copied through a common precomputed numeric pool, or coincidentally match the hypothetical recurrence after a broad source search. The four-field exact equation makes the B anchor stronger than two independent posthoc partial-bit correlations. The 1.29 million search attempts and inherited p951 stage selection must be included when assessing chance; no independent *prospective* production lineage has been established.

The additional B source equations add just one rank to the printer+AX source constraints. None has yet constrained **any** of the 128 missing K04 coupon bits. The authenticated original K08 terminal author-final text is likewise absent. Original unmodified REC8 result: K01/K02/K03/K05/K06/K07 individually PASS, K04/K08 missing, combined INCOMPLETE. No equipment, original evidence, commitments, candidate or verifier modified.

**Recommended next attack:** search for non-32bit source fields or encoded recorder/transfer halves that can supply an independently indexed missing future stage near 1179..1181, 1347/1348, 1574/1575; require complete exact recurrence on unrelated intact controls before extrapolating.
