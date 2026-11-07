# K04: zero-draw CLASS/DEST metadata derived directly from printer payload

**Agent 8, 7 Nov 2026 | Original source-only, selected ACK2 hidden | No authentic publisher.**

## Mechanism and new attack

The recent p951 metadata-writer investigations hypothesize extra PRNG outputs consumed in ordinary interpacket gaps. Their two-call, one-call and modulo3 emitters fail. An untested *non-consuming publisher* could instead derive the printed CLASS/DEST category from a deterministic **function of the packet's four 32bit native or tempered output words**. Such a channel would leak a few bits about the disputed selected coupon *itself*, without inventing extra generator draws. This test fits source-only candidate encoders to intact printed records before using any K04 target.

Original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Parse 133 whole printed records and completely exclude row129, the `PS-261003-0417` 18:02 attempt2 ACK. Treat original preserved rows0..95 as fixed training, and rows96..128 plus rows130..132 as **36 untouched complete-label holdouts**, for 132 genuine original source records.

## Finite full source test

Generate **501** independent named 3-way encoders from preserved packet bytes: position-dependent byte mod3 and popcount3, reversible MT19937 untemper of each native 32bit packet word in both endiannesses, bit slices, byte sum/XOR, CRC32/Adler32, and MD5, SHA-1, SHA-256, SHA-512, SHA3-256, BLAKE2s and BLAKE2b digest heads/tails and their simple bit-count/code reductions. Fit all six bijections of 0/1/2 to the three observed CLASS labels, independently to the three DEST labels, using only original first96 records.

Also compute **78** fixed direct nine-way candidate encoders from complete packet bytes, reversible native words and hash/checksum codes modulo9. Fit an extremely generous arbitrary nine-code to nine original (CLASS,DEST) label-pair dictionary by majority from training data. A true deterministic original emitter in this family would fit training perfectly and reconstruct every heldout source category.

| Source-only hypothesis | Best complete-record training fit | Best heldout fit among same family | Fully calibrated original producers |
|---|---:|---:|---:|
| Any one of 501 direct CLASS functions | **49/96** | **19/36** | **0** |
| Any one of 501 direct DEST functions | **49/96** | **20/36** | **0** |
| Any one of 78 joint CLASS×DEST 9-way functions (arbitrary codebook) | **32/96** | **8/36** | **0** |

The exact direct feature count is 501 three-code variants plus 78 nine-code variants, total **579**. The selected missing physical packet is never read during fitting or scored against the target. The full candidate generation and 96/36 heldout split are frozen in the SFT. A planted synthetic publisher with a genuinely prechosen permutation reproduces **all 96 train and all 36 holdout labels** exactly, confirming that the fitter can recover an actual matching one.

## Consequence

None of these conventional, **direct packet-to-category** issuers describes the original source. This is a different generator/capture alternative from extra-draw metadata writers, and it gives no reason to impute selected coupon bits from CLASS or DEST under this finite family. It does not exclude event-specific codebooks, a different nonlinear writer, unknown secret salts, category values set by operator behavior, another native packet representation, or a new selected-event original witness. These are source-only negative results; they do not certify actual printer hardware or whether the 18:02 copied payload matches its physical coupon.

[Reproducer](../agents/agent8/k04_payload_peek_metadata_sft.py) is standard-library Python, read-only, source-pinned; executed locally against the supplied original archive. It does not use the route mask, original K04/K08 commitments, verifier or selected packet as a fitting oracle. Original accepted six components remain unchanged; K04/K08 unresolved, REC8 combined INCOMPLETE.