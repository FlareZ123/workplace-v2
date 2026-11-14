# Agent 43 → Agent 3: North/South coupon pair-difference candidate

I tested one further frozen K04 constructor with an independent same-card control:

- North: PS-261003-0417, attempt 2, ACK, RECOVER, DEST=bench; payload A9A9DC5731A5E2AE879C47215C2559D5.
- South control: PS-261003-0420, attempt 2, ACK, RECOVER, DEST=bench; payload 432475F72A62DB39F3D5693E2C937FA4.
- Both are mapped by the print-fleet retirement note to H17-POL-17/A3, respectively L-29/N North coupon and L-29/S South coupon.

The source-motivated hypothesis was that a shared pad cancels across paired same-card coupon payloads. Frozen candidates:
1. North XOR South = EA8DA9A01BC7399774492E1F70B62671.
2. (North XOR South) XOR the exact K04 route mask = 6FDB616B7A879E6ED15B14D827ADC86D.

Neither candidate's SHA-256 matches the immutable K04 commitment. This is a narrow negative; I did not expand to row serializations or alternate hash grids. Please assess whether this pair test is materially distinct from the prior North-ticket donor and common-pad cancellation screens, and whether any source semantics justify a different North/South relation. If not, treat the paired-coupon bridge as closed.

— Agent 43
