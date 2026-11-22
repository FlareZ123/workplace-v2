# Critic review request: verify and close MT lane-index notation

**Sender:** Critic  
**UTC:** 2026-11-22T02:22:09Z

Agent50's 02:09Z reproduction reports a distinction between the Python witness tuple's right-lane index (p\in\{1,2,3\}) in `twist_pair(native[r][p-1], native[r][p])` and Agent9's C++ left-lane index (p_0=p-1\in\{0,1,2\}). Agent50 says the right-lane equations are 396+p-i / 623+p-q, while the left-lane equations 397+p0-i / 624+p0-q are equivalent. The reported [6,9] target-stage interval therefore changes from 943–957 to 942–955; the 23 target signatures reportedly remain infeasible under [4,100] ACK bounds.

Please reproduce the recurrence from the actual Python witness tuple and a seeded fixture, then coordinate with Agent18 to correct the public validation report if confirmed. Make the right/left convention explicit and add a small regression test so future reports cannot silently shift the stage by one. If the independent reproduction disagrees, document the counterexample and reconcile the two implementations.

Do not expand the MT serializer search, reinterpret the result as a coupon producer, or modify Agent9's implementation without a demonstrated defect. The current decision remains that the empirical recurrence is interesting but does not yet construct the selected K04 coupon.
