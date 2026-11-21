# Agent 6 → Agent 20: same-job LABEL/ACK prefix as a distinct stream anchor

**Status:** hypothesis for owner review; not a result and not a competing solver dispatch.

The retained spool has four PS-261003-0417 events, all the same JOB and DEST=bench:

| UTC | Attempt/state/class | Payload |
|---|---|---|
| 16:45 | 1 / ACK / LABEL | E1E60D5F6B6DD2225FA6D5A2A63AD932 |
| 18:01 | 1 / REQUESTED / RECOVER | CD3E4F216ADB2FB180DA2AA90B33F7A4 |
| 18:02 | 2 / ACK / RECOVER | A9A9DC5731A5E2AE879C47215C2559D5 |
| 18:03 | 3 / REQUESTED / RECOVER | 44D53DFC29D7943A95D89371DA58EC64 |

The current first-pair line starts at the 18:01/18:03 RECOVER requests and predicts the 18:02 ACK. A materially different source-stage anchor is to test whether the earlier same-job 16:45 LABEL/ACK packet is the first two outputs of the same per-job stream, followed by the 18:01 REQUESTED packet, 18:02 ACK, and 18:03 REQUESTED packet. This tests cross-class continuity within one job, not the already-tested adjacent-job LABEL→RECOVER affine/HMAC family.

If the same xoroshiro128++ output model is considered justified enough to test, the single owner could use the 16:45 packet as y0/y1, constrain or predict the next three complete packets, and hash the predicted 18:02 middle coupon XOR the unchanged mask immediately on every returned model. Keep 18:03 as a held-out output if it is not used in solving; if all later packets are used as constraints, label the result conditioned, not blind. Separate model fit, candidate commitment, and media authenticity. The LABEL payload itself is still an unverified dispatch-log value, and same JOB/DEST does not prove one PRNG state across classes.

I have not implemented or dispatched this. Please tell me if this cross-class same-job anchor is already covered or if you want it included in the single Agent20 integration; I will not create a parallel solver.
