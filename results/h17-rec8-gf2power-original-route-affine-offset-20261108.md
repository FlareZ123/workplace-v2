# H-17: K04/K08 affine second-order GF(2^w) erasure from the original two route fields

**Agent 18 | 8 November 2026 | 24 complete original candidates, no acceptance matches.**

## New target-generating architecture

A source-specific extension of the [previous four-source GF2^w quadratic reconstruction](h17-rec8-gf2power-secondorder-four-source-holdout-20261108.md) hypothesizes that the archive generator used one of the two **original published route constants** as an additive affine term in each 8/16/32/64/128-bit field lane:

`X[n] = a*X[n-1] XOR b*X[n-2] XOR c`,

where `c` is either the exact K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C` or the exact K08 desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, partitioned in the same endian/orientation as the slot bytes. There is **no historical documentation** that either constant acted as a recurrence offset. These are source-linked alternatives to using arbitrary unsourced pads. The K04 copied ACK2 payload and K08 missing final phrase are excluded entirely.

For one field lane, the four true accepted symbols `x1,x2,x3,x5` and source-constant c determine candidate coefficients by solving the degree-two finite-field equation

`D*a² XOR E*a XOR F = 0`,

with `D=x1*x3 XOR x2²`, `E=c*(x1 XOR x2)`, `F=(x3 XOR c)*x3 XOR x1*(x5 XOR c)`. The equation is solved exactly for all roots via binary linear algebra on `t²+t=v` when needed. Every valid a determines `b=(x3 XOR a*x2 XOR c)/x1`. The model then constructs K04 and K08 and predicts the **complete withheld historical K06 and K07** without either having entered the coefficient fit.

## Complete authentic trial

The tested field polynomials and two symbol endiannesses × two block orientations are exactly the nine irreducible fields of the referenced non-affine model. The only extra source choices are the **two distinct original route constants**, giving 72 finite source configurations before quadratic root branching. All six known original slot SHA256 values are checked; original route values are read from the untouched `resources/evidence/recovery-routing.json`.

- **72/72 generated complete eight-slot controls:** the true planted recurrence coefficient occurs in the exact recovered quadratic-root set for every lane, with each original route constant and representation.
- **64/72 original source configurations** have no complete coefficient assignment; all original nonzero and nondegenerate source cases were independently checked.
- **24 complete original candidate K04/K08 pairs** across the eight remaining original source configurations, counting distinct model assignments rather than deduplicated values.
- **0/24 original complete K06/K07 historical holdout predictions** match.
- **0/24 original K04 SHA256 hits; 0/24 original K08 SHA256 hits.**

[Source-pinned standard-library reproducer](../agents/agent18/h17_rec8_gf2power_route_affine_sft.py). It reuses the verified finite-field arithmetic of the preceding SFT and reads the original acceptance and route files directly, read-only. This is a **bounded rejection** of these two source-constant affine recurrence models; it does not prove no cross-slot relation can exist or identify the original physical coupon/caption. Six genuine slots PASS, K04/K08 MISSING and combined REC8/1 INCOMPLETE.
