# K04: paired printer-return ticket generator source holdout

**Agent 10 | 4 November 2026.** Two independent original archive records tie north/south printer assets to separate five-ticket return sets. A new hypothesized **per-cassette deterministic printer-payload producer** was tested against the **source-visible ESC-S / PS-261003-0448 RECOVER ACK1** as an independent control before making a prediction for the disputed selected ESC-N / PS-261003-0417 ACK2. Across **2,106 original north/south paired source encodings**, **52,650 digest constructions** and **2,156,544 Python PRNG coupon positions**, there were **zero complete south-packet reproductions**, so zero source-qualified K04 coupons. Synthetic digest and seeded PRNG controls succeeded. The tested mechanism is rejected; **K04 and K08 remain missing**, six established slots accepted, combined result incomplete.

## Distinct source relationship and discriminating design

The originally supplied office return register `evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` supplies a literal physical-asset relationship:

| Route | Historical job | Return set | Five actual repair tickets | Preserved printer object |
| --- | --- | --- | --- | --- |
| ESC-N | `PS-261003-0417` | `L-29/N` | `ST-094, ST-081, ST-106, ST-099, ST-112` | Selected disputed 18:02 RECOVER ACK2 |
| ESC-S | `PS-261003-0448` | `L-29/S` | `ST-130, ST-151, ST-121, ST-135, ST-142` | Preserved 18:24 RECOVER ACK1 `234BE186E97EE05830909790E336109E` |

The return register also gives each job's cabinet, account and filing reference. Unlike tests that simply seed arbitrary pseudorandom generators from the selected target bytes, this experiment uses a **separately recorded same-day printer-return sibling with a complete preserved source payload** to reject any proposed ticket-keyed generator before exposing the selected target to its commitment. Whether the surviving south copy is physically intact is not established, so the result remains conditional; the design is nevertheless a distinct genuine-source holdout, not a comparison to a synthetic target.

The hypothesis is that a cassette's five service ticket codes, optionally with its original job / lane / account / return set / filing reference / attempt / destination / timestamp, deterministically seed or hash to a sixteen-byte printed coupon. This is speculative. The original register documents **asset provenance, not a printer-seed algorithm**, and the surviving records do not say any ticket was a cryptographic key. If such a rule reproduced the south ACK1, the same fixed rule applied to the north record could construct a complete proposed north physical coupon to reduce with the official XOR mask and check its unchanged K04 commitment.

## Exact source-gated candidate families

Original source SHA256 pins:

- Return register: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`.
- Printer buffer reconstruction: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

For each of N and S, render five ticket numbers as three-digit text, ordinary decimal text or full `ST-###` codes using seven explicit separators; or pack the five ticket numbers as B, 16-bit LE/BE, or 32-bit LE/BE integers. Add no extra field or prepend/append exactly one matching site-specific source field, among job, route, set, account, filing reference, timestamp, attempt and destination, with one of five explicit separators. Deduplicate identical **paired** byte streams. The paired cardinality is **2,106**.

For each pair compute 25 deterministic 16-byte digest choices: first/middle/last16 of MD5, SHA1, SHA256, SHA512, SHA3-256, BLAKE2s and BLAKE2b, plus first16 of HMAC-SHA256 and HMAC-SHA512 with either the original desk nonce or independently accepted K01. Also initialize CPython's standard `random.Random` on the entire original binary string, its Latin-1 text view, or big/little-endian integer interpretation; compare sixteen output bytes at 256 consecutive `randbytes(16)` positions. This latter **4×256** source-conditioned search per pair intentionally does not assume that ticket-seeded serialization starts at phase zero.

Freeze the family before seeing the south packet result. For every south output matching the exact original sixteen-byte control, derive the paired north output with the same algorithm, representation, and output position; XOR the unchanged north route mask and check the original K04 full SHA256 commitment. No south full-packet match arose, so **no target test from this family** was justified or performed.

## Executed results and boundaries

| Original-source test | Exact complete south-packet checks | ESC-S matches |
| --- | ---: | ---: |
| 25 digest/HMAC constructions per paired representation | 52,650 | **0** |
| 4 CPython seed representations × 256 positions per pair | 2,156,544 | **0** |
| **Total tested source producer assignments** | **2,209,194** | **0** |

The SFT independently plants a same-structure south MD5 digest and a CPython bytes-seeded source packet at output phase 123. Both are found within their original complete search paths, with positive test counts respectively 6 and 4. Duplicated synthetic hits arise from alternative equivalent representations, and are not historical findings.

[Executable portable SHA-pinned SFT](../agents/agent10/k04_cassette_ticket_source_holdout_sft.py) runs with standard-library Python using an extracted archive root argument or the repository's `resources/` default. The original source, acceptance, verifier and canonical candidate remain untouched.

The negative is about the **specified ticket-keyed digest/CPython stream architectures under exactly the enumerated representations and first 256 output coupons**. It does not exclude other generator families, separately seeded streams, hidden salts, additional ticket concatenations, a different physical writer, any other copy-stage failure, or the original selected 128-bit coupon. One preserved south copied packet is only a **source-level comparison**, not an authenticated north paper-media reconstruction. No authentic selected K04 bit or K08 final word was recovered.

**Research consequence:** the paired ESC-N/ESC-S asset provenance provides an unusually concrete **same-class source control**. Future proposed cassette-linked producers should reproduce the south original payload or predict another intact heldout printer object before spending a selected-target hash search. An unobserved ticket-to-generator law cannot be inferred merely by searching additional cryptographic digest catalogues.
