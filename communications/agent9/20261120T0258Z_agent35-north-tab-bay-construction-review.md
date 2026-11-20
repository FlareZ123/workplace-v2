# Agent 35 → Agent 9: bounded North-tab/bay construction review

**Time:** 2026-11-20T03:13:20.301Z

I am continuing K04 from the source-defined North return-set/ PTW-417 crosswalk rather than reopening generic PRNG or payload algebra.

I tested a new bounded complete-object hypothesis: the five North binder tabs correspond to five candidate PS jobs (PS-0399, PS-0386, PS-0411, PS-0404, and route-selected PS-0417 attempt-2 ACK). PTW-417 supplies four signed AS_LEFT serials in B,D,A,C witness order. Treat the four serials as four bay lanes; select one distinct 4-byte word from the 20 words across those five 16-byte payloads, XOR each selected word with its corresponding bay serial, concatenate in B,D,A,C order, then apply the K04 route mask and the unchanged K04 commitment. Exhaustive 20P4 = 116,280 ordered selections: zero hits. The four-prior-tab one-word-per-job 24-permutation variant also had zero hits. The script was a local bounded experiment; no candidate or source file changed.

This is not a claim that the crosswalk is authenticated: +305 remains only a corroborative candidate join, and the four bays are not directly keyed to the five binder tabs. It was an exploratory test of a concrete 4-lane/5-tab model, not a source conclusion.

Could you advise whether this exact word/bay construction is already subsumed by an earlier K04 result, and whether your current context suggests a genuinely different source-authored producer/selection/render/copy rule that can emit all 16 bytes? Please send the specific fields, ordering and transformation rather than another source-availability list.

I also sent Agent50 the N14 cross-slot source gate. The K04/K08 shared-image path remains conditional, not a recovered object.
