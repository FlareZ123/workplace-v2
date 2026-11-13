# K04: 128-bit rotation-affine lifecycle transform

**Agent 3 | 13 November 2026 | 768 held-out predictions | 0 payload reproductions | 0 K04 commitment hits**

## Hypothesis

A printer copy-stage may transform one 128-bit job buffer into the next through a fixed whole-object bit rotation plus a constant. This is distinct from a byte-lane permutation, per-byte affine map, 32-bit-word LCG, or PRNG stream.

Use the retained two-stage PS-0420 history as the fit pair:

- Input: ACK / STORES / attempt 1, `31C9714DD36DB2677BB9006670A9DFFD`
- Output: ACK / RECOVER / attempt 2, `432475F72A62DB39F3D5693E2C937FA4`

For each rotation (r in [0,127]), fit the constant from that pair for both models:

[
y = operatorname{ROTL}_{128}(x,r) oplus C
]

[
y = left(operatorname{ROTL}_{128}(x,r)+Cight) mod 2^{128}
]

Apply each fitted transform to three PS-0417 predecessor candidates: prior ACK/LABEL attempt 1, RECOVER REQUESTED attempt 1, and RECOVER REQUESTED attempt 3. The selected RECOVER ACK attempt 2 is held out and is not used to fit the constants.

## Result

**No match.**

- 128 rotations × 2 transform families × 3 held-out predecessor candidates = **768 predictions**.
- Zero predictions reproduce the retained PS-0417 RECOVER ACK attempt 2 payload `A9A9DC5731A5E2AE879C47215C2559D5`.
- Zero predicted payloads, XORed with the official K04 mask, hash to the K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- Two synthetic positive controls (one for each transform family) reproduce their planted held-out outputs.

This rejects only the fixed 128-bit rotate-plus-constant family. PS-0420 is a retained comparison pair, not proof of a common printer state machine or an authenticated coupon issuer.

## Reproduction

Run:

`python agents/agent3/k04_128bit_rotation_affine_lifecycle_sft.py`

The script pins the spool reconstruction, routing, and acceptance files; parses the exact job events; fits only on PS-0420; and tests PS-0417 as the held-out target. It does not modify the candidate, verifier, source resources, or commitments.
