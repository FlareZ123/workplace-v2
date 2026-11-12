# K04 transfer-halfword extension of the p951 MT predecessor fingerprint

**Agent 43 — 12 November 2026.** Source-pinned extension of the existing AX-7778 crossarchive relation. No K04 bits recovered.

## Question

Could the 2-byte transfer checkpoints provide a second, target-relevant 227-step MT predecessor anchor? The earlier AX-7778 result found one exact four-halfword group, but the other transfer IDs and the actual AX-7782 committed chain had not been tested against the same source-derived fingerprint.

## Method

- Pinned the original spool and transfer sources by SHA-256:
  - `evidence/print/spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
  - `evidence/transfers/transfer-audit.jsonl`: `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`
- Withheld printer row 129 before parsing its payload. The 132 intact rows were untempered using the existing hypothetical p951 MT19937 packet-start vector.
- Used only the 12 source-vector row pairs whose starts differ by exactly 227: (4,35), (6,37), (10,41), (13,44), (34,64), (38,68), (44,74), (57,87), (75,106), (90,120), (91,121), (98,132).
- For each pair and each of four lanes, computed the two possible tempered high-16-bit predecessor values allowed by the MT twist identity's unknown predecessor MSB.
- Parsed all 64 original transfer CHUNK rows in source order `(transfer ID, seq, attempt)`; each checkpoint was interpreted as a little-endian 16-bit value, preserving the byte-swap convention of the existing AX-7778 bridge.
- Tested every contiguous four-halfword window within each 16-value transfer stream (52 windows total). Separately tested the 8-value K07 chain for each transfer, selecting the greatest attempt per chunk sequence (20 windows total).

The SFT is `agents/agent43/k04_transfer_halfword_twist_sft.py`. It does not read the selected K04 row's payload, the K04 mask or commitment, the candidate, or the verifier. It includes a positive control for the known AX-7778 group and a one-bit mutation negative control.

## Result

The **only** complete four-halfword match is the already-known AX-7778 window at positions 11–14 against printer rows 34 and 64:

`35AE 78FE 42DD FD35`

No other transfer stream or window produced a complete match. There were also **zero 2-of-4 or 3-of-4 partial matches** across the other windows.

The AX-7782 highest-attempt K07 chain, in the same little-endian integer view, is:

`4789 DCCE CCB9 BA73 E8B7 E67B 0233 C9C5`

None of its five four-value windows matched any of the 12 p951 227-step row pairs. The highest-attempt chains for AX-7778, AX-7781 and AX-7783 likewise produced no full or 2-of-4+ match.

The SFT reports 52 all-attempt windows and 20 highest-attempt windows. Its positive and negative controls both pass.

## Interpretation and limits

This closes one concrete extension of the previously reported transfer-halfword idea: source-ordered four-value windows under the existing p951 227-step predecessor/high16 model. It does **not** prove that the transfers and printer share a producer, nor does it exclude other encodings, pair distances, checkpoint-generation rules, or stage assignments. The one AX-7778 match remains a conditional cross-source fingerprint, not an authenticated historical producer specification.

No new K04 source-to-target constraint or K04 component was recovered. The original acceptance state is unchanged: K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; combined REC8/1 INCOMPLETE.

Do not repeat this same 2-byte halfword/window family. A materially different next step requires new original PS-0417 attempt-2 request/native spool/coupon or an independently authenticated transfer/copy-stage record; K08 still requires Emily's original final-margin, envelope, shelf-card or photograph-caption witness.
