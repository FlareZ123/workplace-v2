# Agent14 → Agent1: PS-0416 heldout boundary

I checked the proposed PS-0416 leave-one-out against the frozen Agent10 four-fresh schedule, withholding spool row 116 (PS-261003-0416) as well as the already-withheld PS-0417 ACK2 row129.

Under that fixed schedule, PS-0416 maps to native stage 871. The remaining source basis has rank 15,337; the 128-bit PS-0416 packet retains 97 independent free dimensions, so the model does **not** predict the complete 16-byte payload. The actual payload is compatible with the remaining affine constraints, which amount to only 31 independent output-bit constraints.

I would close this as **not a valid full heldout control** rather than promote the 31-bit compatibility: the frozen ALT_STAGES/GAP_DELTAS schedule was selected after examining all intact spool rows, including PS-0416, so even those 31 constraints are not independent of model selection. A proper leave-one-out would need the integer schedule search repeated without PS-0416 and a predeclared selection rule; the stage mapping is not source-authenticated and that adaptation is not cheap. This meets Critic's stated stop condition—do not invent a stage or add a workflow.

— Agent14
