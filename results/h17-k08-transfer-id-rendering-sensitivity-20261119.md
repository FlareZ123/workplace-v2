# K08 transfer-ID rendering sensitivity

**Agent 43 — 19 November 2026**  
**Status:** deterministic selector sensitivity only; no K08 phrase or component recovered.

## Source inputs

The retained transfer audit is `resources/evidence/transfers/transfer-audit.jsonl` (SHA-256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`). The source-selected identifier in MAIL-13 is `AX-7782` (`resources/evidence/mail/13.eml`, SHA-256 `80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa)). The four IDs present in the audit are AX-7778, AX-7781, AX-7782, and AX-7783.

Reproducer: [`agents/agent43/k08_transfer_id_rendering_sft.py`](../agents/agent43/k08_transfer_id_rendering_sft.py). It is read-only, uses only the Python standard library, checks both source hashes, and emits all bit streams and packed values. It does not change any source or test a candidate against the K08 HMAC.

## Method

For each rendering, map each ASCII character to its least significant bit, then pack the stream with either the first character as bit 0 (LSB-first) or the first character as the most significant bit (MSB-first). The reverse-direction control reverses only the numeric digits while retaining the AX prefix and, for the full form, the hyphen.

The four renderings are kept distinct:

- **Full:** source-exact hyphenated identifier, e.g. `AX-7782`.
- **Compact:** remove the hyphen, e.g. `AX7782`.
- **Prefix:** `AX`.
- **Numeric suffix:** `7782`.

The source supplies the full hyphenated identifier. It does not explicitly instruct the reader to remove the hyphen, discard the prefix, or apply the final-phrase normalization rule to an identifier. Compact and suffix-only forms are therefore controls, not established source facts.

## Results

Values are shown as LSB-first / MSB-first.

| Transfer ID | Full, forward | Full, reversed digits | Compact, forward | Compact, reversed digits | Suffix, forward | Suffix, reversed |
|---|---:|---:|---:|---:|---:|---:|
| AX-7778 | 61 / 94 | 117 / 87 | 29 / 46 | 57 / 39 | 7 / 14 | 14 / 7 |
| AX-7781 | 93 / 93 | 109 / 91 | 45 / 45 | 53 / 43 | 11 / 13 | 13 / 11 |
| AX-7782 | 29 / 92 | 101 / 83 | 13 / 44 | 49 / 35 | 3 / 12 | 12 / 3 |
| AX-7783 | 93 / 93 | 109 / 91 | 45 / 45 | 53 / 43 | 11 / 13 | 13 / 11 |

The prefix `AX` produces selector **1 / 2** for every transfer.

## Consequence for the proposed K08 chain

Two different representation-dependent returns are present for the source-selected AX-7782:

1. Compact `AX7782` produces selector **13** under LSB-first weighting, returning directly to MAIL-13.
2. Numeric suffix `7782` produces selector **3** under forward/LSB-first weighting (also under reverse/MSB-first), which can select bookmark position 3; the proposed reverse bookmark ordinal then returns to MAIL-13.

The full hyphenated ID produces 29/92, outside the 1–15 bookmark domain. Splitting the structured identifier yields prefix selector 1 and suffix selector 3. These are distinct deterministic paths, not independent rarity factors.

Only the suffix rendering produces selector 3 among the four IDs; only compact AX-7782 produces selector 13. The selector therefore depends materially on how the source identifier is rendered. The benchmark should freeze the source-exact full form as baseline and report compact, prefix/suffix split, and suffix-only interpretations as explicit controls. If all three whole-ID renderings are treated as free alternatives, the downstream configuration count would triple; do not pool their frequencies or multiply separate stage probabilities.

This result does not authenticate the intended rendering, establish a complete K08 extraction rule, or recover the committed phrase. It is a representation-sensitivity finding that must be resolved before interpreting the full-chain endpoint.
