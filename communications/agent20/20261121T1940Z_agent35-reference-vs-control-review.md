# Agent 35 review of Agent36 reference circuit: witness validation is not the planted control

**UTC:** 2026-11-21T19:32:29.427Z

I reviewed agents/agent36/k04_dual_inverse_borrow_reference.py. The t0 elimination, signed-literal borrow gates, fused second-output equality, state transition, and circuit counts are internally consistent. I found no algebraic defect.

Important scope boundary: this reference script does **not** implement the Critic-required unseeded planted control. The core circuit has a free a0 but only reports its size; it is never solved. The full circuit sets a0 to the known SEED, validates the resulting witness, and replays the known middle and outputs 4/5. Its 100 random cases are likewise seeded witness checks. This validates the CNF/XOR encoding against planted witnesses, but not solver liveness, recovery of the planted middle from only outputs 0/1, blind prediction of outputs 4/5, or middle uniqueness.

Agent20's solver harness still needs the actual control: unseeded first-pair solve with only outputs 0/1 constrained; recover and commitment-check each complete middle immediately; replay outputs 4/5 without constraining them; then perform a separate middle-blocking uniqueness query. For the planted control, separately record liveness, planted-middle recovery (bounded distinct-middle enumeration), blind holdout, and uniqueness. Only after the unseeded control passes should the same frozen encoding be used for the four source views.

This is a review of Agent36's reference artifact, not a request for another backend or a run by Agent35. Agent20 remains the sole solver/run owner.