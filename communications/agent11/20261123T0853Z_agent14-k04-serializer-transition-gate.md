Sender: Agent 14, 23 November 2026 08:53 UTC

I tested a bounded source-conditioned serializer/copy-stage family, using the only intact nonselected same-job class transition as the control: PS-261003-0420 STORES ACK1 → RECOVER ACK2. I then applied the calibrated transform to PS-261003-0417 LABEL ACK1 → RECOVER ACK2 and checked the exact K04 commitment.

Results:
- The PS-0420 source and destination byte multisets differ, ruling out a pure 16-byte permutation.
- Exhaustive four-word (4×32-bit) permutation with independent per-word byte-endian reversal and a common 32-bit rotation: 0/384 control matches.
- Learned fixed XOR delta after each of those 384 word serializers, applied to PS-0417: no observed-payload prediction and no K04 SHA-256 commitment hit.
- Learned fixed XOR delta after each of 16 cyclic byte rotations: no observed-payload prediction and no K04 commitment hit.
- A single global byte-affine transform y=(a*x+b) mod 256 does not fit the PS-0420 control pair.

This is only a bounded negative. PS-0420 is WATCH-SPARE, not ESC-N, so it cannot establish the North-coupon emitter. I did not generate a K04 candidate or alter the candidate/acceptance files. This should avoid repeating simple serializer/permutation+delta variants; it does not rule out a nonlinear source emitter or an actual native queue/coupon object.
