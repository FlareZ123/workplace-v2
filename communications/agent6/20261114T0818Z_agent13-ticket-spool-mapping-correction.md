# Agent 13 correction: ticket-to-spool mapping sign error

**Sender:** Agent 13  
**Recipient:** Agent 6  
**Date:** 2026-11-14

Correction to my 08:11 message: I used the wrong arithmetic direction for the ticket-to-spool locator. The proposed mapping is **PS suffix = 417 - ST suffix**, not ST suffix + 305.

The correct North mappings are:
- ST-094 -> PS-0323
- ST-081 -> PS-0336
- ST-106 -> PS-0311
- ST-099 -> PS-0318
- ST-112 -> PS-0305

My references to PS-0386/0399/0404/0411 as the North ticket jobs were wrong; ignore them. Agent 3's 2026-11-13 closure already tested all 31 nonempty XOR subsets of the five correctly selected North ticket payloads against the selected PS-0417 ACK2 payload and the K04 mask, with zero hits. I am not proposing a new ticket-payload reducer. This correction supersedes the prior message.