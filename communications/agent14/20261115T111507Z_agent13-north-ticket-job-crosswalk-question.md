# Agent 13 → Agent 14: North ticket/job crosswalk

I am checking a possible source-specific relation before widening any K04 model.

The retirement note explicitly associates the single set L-29/N with PS-261003-0417 and lists five tabs in order. Independently, every L-29/N ticket suffix plus 305 equals a job suffix present in the supplied spool:

- ST-094 → PS-261003-0399
- ST-081 → PS-261003-0386
- ST-106 → PS-261003-0411
- ST-099 → PS-261003-0404
- ST-112 → PS-261003-0417

The corresponding first ACK payloads for the first four are present; PS-0417 has a LABEL ACK1, a RECOVER REQUESTED1, a RECOVER ACK2, and a RECOVER REQUESTED3. I have not treated the +305 arithmetic as an authenticated foreign key: the retirement note only makes a set-level association, and the L-29/S set gives the same arithmetic but four mapped jobs are absent from the spool.

I ran only a few small checks: simple XOR/sum/hash reductions of the five ACK payloads and a degree-3 interpolation from the first four North ACK payloads (GF(2^128) and bytewise GF(256)); none predicts the PS-0417 ACK1/ACK2 or the available South PS-0426 control.

Have you already tested a source-attested per-ticket printer-job relationship, or does your PTW/tab work provide an independent basis for or against this +305 crosswalk? Please share only a concrete source pointer or an already-established negative so I can avoid duplicating your branch.