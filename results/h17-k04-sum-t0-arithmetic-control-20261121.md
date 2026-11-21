# K04 sum-parameterized dual-borrow arithmetic control

**Status:** <badge>PASS — arithmetic identity only</badge>

This note records a reproducible pure-Python control for the sum-parameterized, dual-borrow form proposed as a same-Z3 encoding of the xoroshiro128++ 1.0 first-pair equations.

## Question

Can the first-output inverse and the two borrow-chain identities be expressed without materializing the initial second state word, while preserving the exact six-output stream?

## Identities

Let (x_0=a_0+b_0\pmod{2^{64}}), and let the first output be

[
y_0=\operatorname{ROTL}(a_0+b_0,17)+a_0.
]

Then

[
a_0=y_0-\operatorname{ROTL}(x_0,17),\qquad b_0=x_0-a_0.
]

For (t_0=a_0\oplus b_0), the bitwise subtraction recurrence for (x_0-a_0) gives

[
(t_0)_i=(x_0)_i\oplus borrow_i,
]

where (borrow_0=0) and

[
borrow_{i+1}=\operatorname{MAJ}(\neg(x_0)_i,(a_0)_i,borrow_i).
]

The transition is

[
a_1=\operatorname{ROTL}(a_0,49)\oplus t_0\oplus(t_0\ll21),\qquad
b_1=\operatorname{ROTL}(t_0,28).
]

For the second output (y_1), define (u_1=\operatorname{ROTR}(y_1-a_1,17)). Then (u_1-a_1=b_1); this equality can also be constrained bitwise with a second borrow chain.

## Reproduction

Run:

```bash
python agents/agent1/k04_sum_t0_identity_control.py
```

The test uses Python's `random.Random(0xA17E8BC05E34DB24)`, 10,000 independent 64-bit state pairs, the exact xoroshiro128++ 1.0 transition/output, both borrow identities, and six-output replay.

## Result

**10,000 / 10,000 passed.** The script prints:

```text
PASS: 10000 deterministic states; seed=0xA17E8BC05E34DB24
Arithmetic identities only; no source data or solver performance tested.
```

## Limits and next use

- This establishes arithmetic equivalence and bit ordering for the proposed encoding.
- It does **not** establish that the PS-0417 payloads are xoroshiro128++ outputs.
- It does **not** establish that Z3 can solve the unseeded planted-middle control.
- It does **not** produce a K04 candidate or satisfy the K04 commitment.
- Agent50 remains the single owner of the existing gated Z3 solver line. The encoding should be integrated there only, with the same unseeded synthetic control and commitment-first candidate handling.
