# H-17 K04: original-source binary-seed producer frontier, three new complete-candidate routes

**Agent 24 | 4 November 2026, 18:18 UTC.** These are three original-source attacks on the *provenance of a hypothetical CPython binary seed*, under Agent15's p951 printer-source fingerprint. **None recovers an original selected K04 physical coupon bit or a K08 author-final word.** The original unchanged acceptance state remains K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined INCOMPLETE.

## Target-bearing concept and prerequisite

Agent15's [source-derived CPython `Random(bytes)` fingerprint](h17-k04-p951-python-sha512-binary-seed-fingerprint-20261104.md) constrains a missing 2.35–2.43 KB binary seed `B` from the 132 intact original printer ACK packets, excluding the disputed selected attempt2 row129. Were an actual **entire `B`** recovered and source-producer provenance established, one could predict a full hypothetically selected native packet and test its K04 masked component against the original acceptance commitment.

The original selected ACK2 copied payload, K04 route-mask XOR reduction, and target commitments are **not consulted in any of these new source reconstruction experiments**. The source constraints, including `key[22]=FD6A4CF7`, `key[23]=06EDCDAD`, `key[601]=49342EC0`, and `key[602]∈{64589C88,E4589C88}`, are explicitly **conditional mathematical consequences of an unverified first-cycle CPython stage hypothesis**. They are not authenticated original bytes of the missing printer coupon or independently identified true `B`.

## Three distinct binary-input production mechanisms

| New hypothetical inner mechanism | Original source-only complete candidates examined | Independent original holdout result | Reproducer |
| --- | ---: | --- | --- |
| **64-bit whole-word seed outputs:** SplitMix64, xorshift64*, and raw full-state PCG LCG64, packed into 32-bit pairs. Both whole-pair alignment phases, two output byte orders, two halfword orders, and `key[602]` alternatives. | **36** fully determined 64-bit initial output/state and layout configurations | **0/36** match even the independent `B` word12; in each family all three source-heldout words fail. | [64-bit pair-parity Python SFT](../agents/agent24/k04_seed_64bit_pair_parity_sft.py) |
| **Native 32-bit-output PCG-XSH-RR 64/32:** a long `B` made from consecutive outputs of a 64-bit PCG state and standard single-stream increment. For each of two source word0 possibilities and two byte orders, invert all 32 rotations and enumerate all `2^27` undetermined state bits. | **17,179,869,184**, mathematically exhaustive over four complete 64-bit state spaces | First independent distant word12 yields 3,0,3,0 states; **all six fail** independent original word1. True seeded PCG planted state recovered uniquely. | [Original C/OpenMP complete inverse SFT](../agents/agent24/k04_nested_pcg32_seed_inverse_sft.c), [dedicated detail](h17-k04-nested-pcg32-seed-1718b-source-exclusion-20261104.md) |
| **Hash/KDF expansion of preserved source-identities or original member bodies:** SHAKE128, SHAKE256; SHA256/SHA512 four-byte big-endian append-counter chains from counter0 or1; HKDF-SHA256 with four fixed route/nonce/domain choices. `B` has each of 72 lengths corresponding to n606..623 plus four possible first partial key words. | **682,560** full `B` constructions: **948** distinct actual source inputs × **10** producer architectures × **72** lengths | **0/682,560** satisfy even the original exact 32-bit `key[22]=FD6A4CF7`, hence none can satisfy the adjacent 64-bit `key[23]||key[22]` witness or the 86-word full fingerprint. | [Read-only original-source KDF SFT](../agents/agent24/k04_archival_label_kdf_binary_seed_sft.py) |

### Hash-based input corpus and source provenance

The hash-expansion experiment uses **425 source-derived identity labels** and their original/uppercase/lowercase forms (1,323 candidate-label-and-file input entries before binary dedup), including the original ESC-N job, route, incident ID, property account, five north L-29/N service tickets, preserved dates, route mask and nonce, the **surviving file bodies** in `resources/evidence/`, and the original printer spool **with the selected 18:02 ACK2 row expressly removed**. Deduplicating identical input bytes gives **948** candidate `B` sources. It does not use any preimage of the K04 commitment, nor treat the contested ACK2 copied bytes as valid physical payload.

For each expansion, the output's source-required `key[22]` must occur at byte offset `len(B)-28:len(B)-24`; `key[23]` at `len(B)-32:len(B)-28`; and higher `key[590],key[601],key[602]` positions depend on the start of the seed. The exact K22 preliminary gate is **zero across 682,560** full candidate constructions, so no SHA512 or original K04 commitment probes are warranted. Positive controls instantiate complete binary seeds from **all ten actual hash/KDF producers**, at n606, n616, n623 and both partial-boundary lengths, and deliberately flip a byte of the K22 gate to demonstrate rejection. The run against unchanged original source returned:

```text
ORIGINAL n606..623 x 4 possible leading-partial seed lengths: complete
UNIQUE_SOURCE_LABELS=425 INPUT_VARIANTS=1323 UNIQUE_SOURCE_INPUT_BYTES=948
ARCHITECTURES_PER_INPUT=10 SEED_LENGTHS=72 CANDIDATE_B_INSTANCES=682,560
K22_FIXED_MATCHES=0 JOINT_K22_K23_FIXED_MATCHES=0 FIVE_WORD_COMPLETE_MATCHES=0
```

Original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, route sheet SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`, notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` were validated. Locally executed full KDF prototype: `/mnt/data/h17local/k04_seed_kdf_source_sft.py`, SHA256 `4c52fe5a6272a97fe6f1d80eb93eb844d36e9b5c9d16e90a494eca745d698643`. The committed SFT is the repo-portable implementation of the same finite source constructors, with no selected target data in its tests.

## Why this matters and what remains open

This is a **new mechanism boundary** for turning source archival identities/data and low-state native generators into a long full printer seed. It is distinct from direct copied-ACK corruption searches, an integer Mersenne Twister seed-grid, per-ticket AES coupon emitters, and the existing early-2026 printer packet PCG32 inverse: the present tests condition on a *long intermediate source-derived binary seed `B`*, and make **source-only predictions before any selected object hash**.

No original source identifies CPython, a 951-output stage gap, any of these inner generators, a hash KDF, or the physical printer/copying stage's relationship to the copied ACK. A positive source-seed witness would still require selected-stage authentication and the unmodified official verifier. A negative under these model families does not add one physical coupon bit or constrain alternative original generators.

The best next crack is an **independent authentic whole selected original**: a 2026 physical ESC-N ACK2 coupon image/print-host source or an independently authenticated final Emily caption transcription. If a historically evidenced `B` producer appears, use Agent15's six-part SHA512 and 86-source-word test, regenerate the complete native selected coupon and only then check K04. Avoid another arbitrary catalogue of unrelated generators without an original selector or independently heldout consequence.
