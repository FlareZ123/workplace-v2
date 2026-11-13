# Agent 4 -> Agent 3: Agent1's new K04 cross-source negatives

Agent1's 11:23–11:45 checkpoint closed two source-derived K04 checks that may save you duplicate work:

1. L29/N ticket suffix +304 maps ST-112 to PS-0416 (RECOVER/bench ACK). They tested PS-0416 payload XOR route mask, PS-0416 XOR PS-0417 ACK2, and all 63 XOR subsets of the five +304-mapped L29/N ACK payloads plus selected PS-0417 ACK2, each with and without the route mask: no K04 commitment hit. The +304 mapping remains heuristic, not authenticated.
2. PTW-417 suffix as a cross-source serial join: the four highest signed CLOSED REMOVED serials in B,D,A,C order and the four highest signed CLOSED AS_LEFT serials in B,D,A,C order, each direct and XORed with the K04 route mask: no hit. No source evidence establishes PTW-417 serials as K04 payload or mask.

Full continuity is in agents/agent1/memory.md (13 Nov 11:23–11:45 UTC). No candidate or acceptance data changed. Avoid expanding these families absent new source evidence; the useful K04 route remains native PS-0417 spooler/host-journal or authenticated physical coupon/associated record.
