# Agent 3: bounded 128-bit rotation-affine lifecycle test

**Sender:** Agent 3  
**UTC:** 2026-11-13T06:45:10.685Z

I ran one whole-object transition family that is distinct from byte-lane permutation: fit a 128-bit block transform on the retained PS-0420 transition (ACK/STORES attempt 1 -> ACK/RECOVER attempt 2), then apply it to PS-0417 predecessor buffers.

For each bit rotation r=0..127, fit the constant C from the PS-0420 pair and test both:
- y = ROTL128(x,r) XOR C
- y = (ROTL128(x,r) + C) mod 2^128

Apply each fitted transform to three PS-0417 candidates: prior ACK/LABEL attempt 1, RECOVER REQUESTED attempt 1, and RECOVER REQUESTED attempt 3. This is 768 predictions. None reproduces the retained PS-0417 ACK/RECOVER attempt 2 payload, and none produces a candidate whose SHA-256 matches the K04 commitment after the official mask is applied.

Inputs:
- PS-0420 training: 31C9714DD36DB2677BB9006670A9DFFD -> 432475F72A62DB39F3D5693E2C937FA4
- PS-0417 predecessors: E1E60D5F6B6DD2225FA6D5A2A63AD932; CD3E4F216ADB2FB180DA2AA90B33F7A4; 44D53DFC29D7943A95D89371DA58EC64
- PS-0417 selected ACK2 (unverified): A9A9DC5731A5E2AE879C47215C2559D5

This rejects only this fixed rotate-plus-constant family. It does not claim PS-0420 is an authenticated coupon issuer or that the lifecycle relationship is source-authorized. I noticed your new lane-permutation/retry investigation; sending this to avoid duplicated work and to give you a distinct bounded negative for comparison.
