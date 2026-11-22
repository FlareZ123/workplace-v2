# H-17 K04: tail-eight ACK-copy hypothesis, source-gated exact state inversion

**Agent 30 | 22 November 2026 | Disposition: computational UNKNOWN, original source not executed**

## Recovery model and intended complete-coupon test

Consider the three PS-261003-0417 RECOVER events: attempt1 REQUESTED at 18:01, attempt2 ACK at 18:02, attempt3 REQUESTED at 18:03 (UTC, 3 October 2026). The hypothetical issuer uses xoroshiro128++ 1.0, two successive 64-bit outputs per event and no unobserved draws between attempts. Original REQUESTED1 and REQUESTED3 packets are immutable outer constraints. Unlike earlier wholly blind-middle inversion, this conditional *copy-integrity* model preserves **only bytes 8..15** of the disputed copied ACK2; its first eight bytes are entirely withheld, allowing a hypothetical severe leading-region copier fault. All four endian / word-order serializer views are defined. If a complete source-consistent midpoint becomes reconstructible, encode it, XOR the unchanged original `K04.masked_component`, and hash the resulting entire 16-byte component against the original K04 SHA256 commitment.

The issuer, output schedule, and integrity of even the copied tail are not attested. A successful commitment alone would prove recovery-key acceptance, not automatically authenticate an incident-day physical printer witness.

## Exact executable gate

[Source-pinned Python SFT](../agents/agent30/k04_xoropp_sparse_ack_sft.py), based on the independent [Agent36 borrow/XOR circuit](../agents/agent36/k04_dual_inverse_borrow_reference.py), adds 64-bit *one-middle-output* constraints to the earlier four outer word constraints and retains all 64-bit modulo-addition carry chains. The selected copied first eight bytes never enter the fit.

The SFT first builds **80** separate seeded circuit/witness checks (20 planted 128-bit states by four serializer layouts); all clause identities and state replays passed. The gate then generates a separate original-style synthetic six-output stream from a hidden seed, deliberately XOR-corrupts the copied first eight bytes, and asks **CryptoMiniSat 5.14.7 native-XOR SAT** to reconstruct the entire unobserved original state and middle coupon from only the outer packets plus copied tail8. The actual planted state never enters the inversion solver. Original historical data, route mask and commitment are not consulted until this unseeded planted positive has been recovered exactly.

**Completed [GitHub Actions run 44989447368](https://github.com/FlareZ123/workplace-v2/actions/runs/44989447368), run head `bbdfd30f19a3d25dcc34ae21d952dde0c5e187f1`, job SUCCESS, immutable artifact `k04-sparse-tail8-outcome` id `14741591420`.** The workflow's success means the diagnostic completed and artifact was uploaded, not that the solver obtained a state. Exact artifact:

```json
{"control": "80 seeded circuits and four serializers validated", "status": "PASS"}
{"K04_component_status": "NOT_EVALUATED", "cnf_clauses": 2793, "experiment": "unseeded_planted_tail8_copy", "fit": "REQUESTED1, REQUESTED3, exactly ACK2 copied bytes8..15", "planted_seed_withheld": true, "selected_ACK2_head8_withheld": true, "solve_seconds": 240.166, "solver": "pycryptosat-native-xor", "status": "UNKNOWN", "variables": 1703, "view": 0, "xor_clauses": 1274}
{"source": "SKIPPED", "reason": "unseeded complete middle positive not recovered", "K04_component_status": "NOT_EVALUATED"}
```

## Decision boundary

The new source-conditioned geometry did not overcome the essential unseeded inversion barrier. It **does not** supply a complete original coupon, a source commitment miss, an original contradiction, or a proof that tail8 was damaged. Only the mathematical clauses were validated; the hard source-blind synthetic inversion remains solver-inconclusive after 240.166 seconds. Do not reinterpret the CI job SUCCESS as a K04 PASS or run large equivalent prefix/backend grids with the same liveness deficit.

The original K04 and K08 components remain missing, six other original commitments remain PASS, and combined REC8/1 stays INCOMPLETE. Unmodified original route, verifier, acceptance and candidate were preserved. The next effective discriminator is a new original complete-coupon source or a fundamentally better inversion algorithm demonstrated on an **unseeded complete-middle planted control**, not a longer timeout on this fixed circuit.
