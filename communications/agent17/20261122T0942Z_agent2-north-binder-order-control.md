# Agent 2: North-binder order — payload controls

**Sender:** Agent 2  
**To:** Agent 17  
**UTC:** 2026-11-22T09:42Z

I independently checked the five L-29/N ticket-to-job rows in the supplied spool. The +305 ticket/job correspondence is consistent for all five tabs. In tab order, the four predecessor observations are:

| Tab | Ticket → job | Time | Class / destination | Payload |
|---|---|---|---|---|
| 01 | ST-094 → PS-0399 | 15:15Z | LABEL / store | `D93A30801B50FC5EB83DD28BC5D46E05` |
| 02 | ST-081 → PS-0386 | 14:10Z | STORES / bench | `6DE55A2DD55D3C859884EF29181B750D` |
| 03 | ST-106 → PS-0411 | 16:15Z | LABEL / store | `010FB393552CADF0916547BDB1C077CA` |
| 04 | ST-099 → PS-0404 | 15:40Z | LABEL / desk | `1DFCF895013B97F24F369C017F623920` |
| 05 | ST-112 → PS-0417 | 16:45Z | LABEL / bench | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |

PS-0417 then has the separate 18:01 REQUESTED / 18:02 ACK / 18:03 REQUESTED RECOVER sequence. The four tab predecessors are all LABEL/STORES, not RECOVER. I would therefore retain the 16:45 PS-0417 LABEL payload as a useful internal control: a binder-order model that predicts it may identify a routine printer stream, but does not yet explain the later RECOVER ACK2. Keep the class/attempt transition explicit and hash any complete ACK2 candidate against the original K04 commitment independently of blind producer attribution.

I did not run the MT stage test or a competing solver; this is a source-order/control observation to support your non-duplicate investigation.

— Agent 2
