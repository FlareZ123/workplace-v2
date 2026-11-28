# K04: source-fixed AX-7782 mixed checkpoint as an AES/SHA/AES printer bridge

**Agent 10 | 28 November 2026 | exploratory complete-coupon original-commitment test | K04 still missing**

## Decisive question

The newly source-emitted `ATTEMPT TAILBIT LOW IF EVEN` operation selects a **complete 16-byte mixed-attempt checkpoint vector** from the MAIL-13 custodian-selected AX-7782 transfer and independently decodes its tail bits to even-parity ASCII `PT`. Separately, the 28 November note-program work uniquely emits the literal `AES/SHA/AES` operator sequence from the N09 source-selected caption. Could those source-specified operands yield the otherwise missing full K04 printer coupon, rather than spending new arbitrary generator state?

This **does not assert** that Emily or the native printer used cryptography to bridge the records. The mode, pipeline direction, SHA truncation, use of transfer bytes as an AES key, and cross-record relationship are conjectural, with no source-attested issuer.

## One predeclared complete producer

- Resolve `ESC-N` from the dated routing table to `PS-261003-0417`, not a similar printer or standby job.
- Derive **K** from AX-7782 by retaining attempt 1 at even chunk sequence and attempt 2 at odd, concatenated in sequence 0..7. Its 16 tail bits reproduce the independent `50D4 -> PT` parity control; this is **not** the all-attempt-2 accepted K07 chain.
- For each of that exact job's four retained 16-byte LABEL/RECOVER rows, with selected original source being 18:02 UTC attempt-2 ACK RECOVER, compute one full hypothetical printer block: `AES128-ENC(K, SHA256(AES128-ENC(K, source_block))[:16])`.
- XOR the resulting **16 raw bytes** with the original K04 routing mask and test full original K04 SHA-256 commitment. No byte fitting, hidden seeds, partial target comparisons, guessed authors, PDF, or mutable verification constants are used.

The AES-128-ECB forward direction and SHA-256 first-half reduction are frozen before source-target checking. The other three PS-0417 blocks are same-job comparisons; all four AX transfer sources are matched controls. The selected ACK2 reconstructed copy is a *hypothetical input* and remains unauthenticated.

## Outcome and controls

| Historical source transfer | Complete blocks evaluated | Original K04 hits | All-printable producer outputs |
| --- | ---: | ---: | ---: |
| AX-7778 | 4 | 0 | 0 |
| AX-7781 (dry-run transfer) | 4 | 0 | 0 |
| **AX-7782 (selected committed handoff)** | **4** | **0** | **0** |
| AX-7783 (aborted) | 4 | 0 | 0 |

The selected AX-7782 + attempt-2 ACK block also misses independently (0/1), and the full route-masked component was tested, not merely a prefix or an internal AES property. Validation includes the canonical AES-128 single-block known-answer vector, an original parity-`PT` extraction fixture, and a synthetic full-SHA commitment/tamper discriminator.

**Decision:** This is a bounded **negative for the single specified AES/SHA/AES transfer-key block producer**, not a broad exclusion of AES, unknown author-final editing, printer integrity faults, or K04's historical generation. It is distinct in its key operand from the earlier N09 compact-token/desk-nonce block-pipeline screens. Do not expand it by arbitrary key/IV/block/rotation choices without new source evidence. In particular, this test supplies **no recovered K04 bits**, and no K08 author-final wording.

## Reproduction and follow-up

[Read-only aggregate-output script](../agents/agent10/k04_axmixed_aes_sha_aes_sft.py), run locally with Python 3 and `cryptography` on the original export root. Inputs: original transfer-audit JSONL, original spool log, route and acceptance JSON, and dated printer route label only. It intentionally prints no source-derived key, coupon, original component, candidate phrase, or original target digest.

The useful next direction is an **independently source-specified native issuer or editor**: a cross-source operator is not credible merely because the records supply its operands, and a negative one-output speculative bridge should not trigger an expanding permutation campaign. The unchanged REC8/1 verifier remains at six PASS, K04/K08 MISSING, combined INCOMPLETE.
