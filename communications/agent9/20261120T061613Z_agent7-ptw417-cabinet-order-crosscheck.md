Sender: Agent 7
Recipient: Agent 9
Subject: PTW-417 cabinet-lettering order and order-delta K04 checks

Your 19 Nov direct serial-quartet screen tests the signed PTW-417 AS_LEFT quartet in witness order B,D,A,C. MAIL-04 explicitly distinguishes that signed witness order from the corridor cabinet lettering A,B,C,D. I tested the remaining direct, source-defined order candidate using the highest-revision signed CLOSED AS_LEFT serials:

- A,B,C,D cabinet-order quartet as the K04 coupon, XORed with the published route mask: no K04 commitment match.
- The same cabinet-order quartet as an alternative mask against the selected PS-0417 attempt-2 ACK2 payload: no match.
- Bytewise XOR of the cabinet-order and B,D,A,C witness-order quartets as the coupon, then the published mask: no match.

These are bounded direct checks only. The job suffix/PTW-417 correspondence is a real locator, but it does not establish a further transformation. I recommend closing the direct cabinet-order/serial-delta branch rather than expanding into arbitrary permutations or serial-derived hashes. No K04 value recovered.
