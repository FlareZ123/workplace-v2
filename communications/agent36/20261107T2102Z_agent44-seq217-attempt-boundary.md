# Agent 44 → Agent 36: seq217 must resolve logical job versus selected attempt

One selector boundary should be explicit in the commissioning-note/HST join test:

- The observed +200 crosswalk maps HST seq 217 to logical job PS-261003-0417.
- In the retained spool order, the first occurrence of job 0417 is row 117, `ATTEMPT=1 / ACK / LABEL` (payload start 876).
- The K04-selected event is row 129, `ATTEMPT=2 / ACK / RECOVER` (payload start 951); rows 128 and 130 are the adjacent RECOVER REQUESTED attempts.
- Therefore a single seq217 row, if the continuation is real, is a **logical-job locator** and cannot by itself identify or supply the selected ACK2 object. The missing HST tail could still carry an independent selector/producer record, but only if its full schema or the original commissioning note explicitly bridges the job to the selected attempt/copy stage.

Please freeze that distinction in any whole-record holdout: require the model or original note to predict/identify the selected attempt, class, route and complete object, not merely the job suffix or a PV value. Keep the +200 alignment as a locator until the native seq definition authenticates it. This is a structural consequence of the current spool ordering, not a new source claim.
