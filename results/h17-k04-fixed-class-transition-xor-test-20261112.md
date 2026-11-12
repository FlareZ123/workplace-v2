# K04 fixed class-transition XOR test (12 Nov 2026)

## Hypothesis

A different event-sourcing model from the same-job retry-delta test: perhaps the spooler transforms an earlier desk-side job payload into the later `RECOVER` payload by a fixed 16-byte XOR delta. `PS-261003-0420` provides a structural control (STORES at desk, then RECOVER at bench); `PS-261003-0417` is the target (LABEL at desk, then RECOVER at bench).

This is exploratory, not a documented spool format. The route explicitly selects the RECOVER/ESC-N row rather than the earlier label job.

## Inputs and result

- PS-0417 LABEL/ACK (desk): `E1E60D5F6B6DD2225FA6D5A2A63AD932`
- PS-0417 RECOVER/ACK (bench): `A9A9DC5731A5E2AE879C47215C2559D5`
- PS-0420 STORES/ACK (desk): `31C9714DD36DB2677BB9006670A9DFFD`
- PS-0420 RECOVER/ACK (bench): `432475F72A62DB39F3D5693E2C937FA4`

The control transition delta is:

`PS0420_STORES XOR PS0420_RECOVER = 72ED04BAF90F695E886C69585C3AA059`

Applying it to the target's earlier LABEL payload predicts:

`PS0417_LABEL XOR delta = 930B09E59262BB7CD7CABCFAFA00796B`

The actual PS-0417 RECOVER/ACK payload is `A9A9DC5731A5E2AE879C47215C2559D5`; the prediction does not match. The independently observed PS-0417 transition delta is `484FD1085AC8308CD83A9283FA1F80E7`, also different from the PS-0420 control delta.

## Conclusion

Reject a fixed desk-to-bench class-transition XOR transform. This supplies one complete candidate prediction against a structurally similar control and it fails before the K04 mask/commitment stage. It does not authenticate the retained PS-0417 payload or recover K04. Do not promote the predicted bytes or expand this into arbitrary class-pair transformations.

