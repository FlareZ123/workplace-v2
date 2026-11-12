# K04 fixed class-transition XOR test (12 Nov 2026)

## Hypothesis

A different event-sourcing model from the same-job retry-delta test: perhaps the spooler transforms an earlier job payload into the later `RECOVER` payload by a fixed 16-byte XOR delta. **Correction:** the actual `PS-261003-0417` LABEL/ACK row is `DEST=bench`, not desk; its later RECOVER/ACK row is also `DEST=bench`. The proposed `PS-261003-0420` control is STORES/desk → RECOVER/bench. These are not matched transitions, so the comparison is not a source-matched control and cannot reject a bench→bench transition model.

This is exploratory, not a documented spool format. The route explicitly selects the RECOVER/ESC-N row rather than the earlier label job.

## Inputs and result

- PS-0417 LABEL/ACK (bench): `E1E60D5F6B6DD2225FA6D5A2A63AD932`
- PS-0417 RECOVER/ACK (bench): `A9A9DC5731A5E2AE879C47215C2559D5`
- PS-0420 STORES/ACK (desk): `31C9714DD36DB2677BB9006670A9DFFD`
- PS-0420 RECOVER/ACK (bench): `432475F72A62DB39F3D5693E2C937FA4`

The control transition delta is:

`PS0420_STORES XOR PS0420_RECOVER = 72ED04BAF90F695E886C69585C3AA059`

Applying it to the target's earlier LABEL payload predicts:

`PS0417_LABEL XOR delta = 930B09E59262BB7CD7CABCFAFA00796B`

The actual PS-0417 RECOVER/ACK payload is `A9A9DC5731A5E2AE879C47215C2559D5`; the prediction does not match. The independently observed PS-0417 transition delta is `484FD1085AC8308CD83A9283FA1F80E7`, also different from the PS-0420 control delta.

## Corrected conclusion and scope

The proposed control is not role-matched: the target transition is LABEL/bench → RECOVER/bench, while the comparison transition is STORES/desk → RECOVER/bench. The observed deltas differ, and the PS-0420-derived candidate does not equal the retained target ACK, but that is **not** a valid falsifier of a fixed bench→bench transition. The result is therefore an exploratory mismatch, not a rejected source-matched transition rule. No complete K04 value or authenticated payload integrity follows. Do not promote the predicted bytes or expand arbitrary class-pair transformations; a future test would need a genuine same-destination/same-role historical control or an independently specified transform.

