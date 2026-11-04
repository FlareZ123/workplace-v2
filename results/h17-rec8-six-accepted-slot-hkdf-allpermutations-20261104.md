# REC8: a six-accepted-component joint-source KDF attack on missing components

**Agent 12 | 4 November 2026. Outcome: no original K04 or K08 commitment match.** The six independently accepted components were tested as a **joint entropy source** for a possible archive-internal deterministic derivation of K04 or K08. This is a newly tested exploratory alternative to recovering a disputed physical printer coupon or the unknown author's exact caption. It is not a historically attested firmware procedure; the H-17 route sheet instead describes separate physical and textual reductions.

## Why this is a genuinely different architecture

The earlier conventional Reed–Solomon / second-order finite-field study asks whether six known slots are symbols of an eight-slot codeword. Agent47's K08 bypass tested arithmetic and digest transforms on **pairs** of source carriers. Agent18's printer-HMAC study tested the six known slots individually as HMAC **keys** over per-job metadata.

Here all **six actual accepted REC8 components simultaneously form the input key material** (96 raw bytes, before any optional ASCII rendering) of a joint extractor. A positive result would reconstruct a complete missing component independently of the disputed selected ACK and absent Emily final phrase. SHA256, SHA512, direct HMAC keyed by a known slot, and RFC5869-style HMAC-SHA256 extract/expand are tested with deterministic source-domain context. The trial is motivated by an escrow envelope possibly using a secondary KDF; no original evidence specifies one.

## Exact source and frozen complete-candidate family

Use only the original six individually PASS slot values K01,K02,K03,K05,K06,K07 from `resources/candidate.json` and validate each against the unaltered `resources/acceptance.json` full SHA256 digest. Use the original `resources/evidence/recovery-routing.json` route mask `8556C8CB6140A7F9A5123AC7571BEE1C` and desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, preserving their exact bytes and source SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.

Enumerate **all 6! = 720 permutations** of the accepted components. For each ordering, use three combined input encodings (concatenated raw bytes, uppercase concatenated hex ASCII, uppercase hex lines separated and terminated with LF). Use eighteen frozen original-source/domain context strings: K04/K08 names and LF variants, REC8/H17 full slot labels, ESC-N, selected job/attempt, original route mask, original nonce, combined-prefix text, and three keeper/desk/caption literals. For each encoding and context, compute both digest halves for SHA256 and four 16-byte SHA512 quarters of raw input, appended-context input, and prepended-context input.

On the *raw* six-component concatenation, additionally use five HKDF extraction salt representations: 32 zero bytes, original route mask, original nonce, mask||nonce, nonce||mask. For each context, HMAC-SHA256 HKDF-Extract followed by HKDF-Expand first block `HMAC(PRK, info || 0x01)`, testing both 16-byte halves. Also test direct HMAC over `six_component_concatenation || context` under each of the six original accepted 16-byte components as key, again both halves.

For **every generated 16-byte value**, evaluate three complete-slot hypotheses:

1. Direct K04 component: `SHA256(value)` against original full K04 commitment.
2. Generated K04 physical coupon: `SHA256(value XOR original_route_mask)` against original full K04 commitment.
3. Direct alternative K08 component: `SHA256(value)` against original full K08 commitment.

These tests leave the original route, nonce, hashes, source records and candidate file unchanged.

## Executed result and positive controls

The original-source Python implementation ran successfully with **1,607,040 complete assignments per interpretation**, or **4,821,120 full original-slot commitment checks**. All three original comparisons found **zero** matches. Counts describe deterministic assignments, with overlaps expected from empty/repeated contexts; they are not independent information or necessarily unique byte strings.

A *planted* synthetic expected KDF output was constructed using the original six accepted components in natural key order, the original route mask as HKDF salt and the literal `K04` as HKDF info. This is a full 16-byte synthetic output of the very extraction method under test, `5AAC53D12D0A276B3D1B6DA7808C8039`. The actual complete enumerator recovered the planted value **exactly once**. This validates the exact HKDF input ordering, digest extraction and enumeration against a generated known answer. It does not supply evidence of the historical producer.

[Reproducible single-file Python3 SFT](../agents/agent12/h17_sixslot_kdf_sft.py) uses only standard-library `hashlib`, `hmac`, `itertools`, `json` and original repository resources. The original run used the user's unmodified attached 46-file ZIP and the already validated six slot values. The committed source uses the corresponding repository `resources/` paths and asserts exact counters plus the planted-positive count.

## Decision for further cracking

This closes the stated **joint-six-slot HKDF and named digest permutations**; it does not establish that K04 and K08 are independent. Source information still favors the specific ESC-N coupon and Emily final-caption reducers, so there is no basis to expand an arbitrary KDF context or prefix lottery. A productive departure would require an archive-manufacturer record specifying an actual cross-slot extractor, or a reconstructible source-selected historical print/authoring stage that reaches the original complete value.

**Original REC8/1 remains K01/K02/K03/K05/K06/K07 PASS, K04 and K08 MISSING, combined INCOMPLETE.**