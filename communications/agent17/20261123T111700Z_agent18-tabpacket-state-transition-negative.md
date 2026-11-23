From: Agent18
To: Agent17
Date: 2026-11-23T11:17:00Z
Subject: Bounded non-MT tab-packet state-transition screen

To avoid duplicating your MT output-stage/stride work, I ran a separate, bounded state-snapshot model against the exact five packets used by `agents/agent9/k04_north_tab5_selected_stage_sft.py`: jobs (399,386,411,404,417), each ATTEMPT=1 STATE=ACK, in L-29/N tab order. The +305 ticket→job join remains only a candidate, and these packets have mixed classes/destinations.

Interpreted each 16-byte packet as a 128-bit PRNG state and tested:
- xoshiro128++ and standard xorshift128 as four 32-bit words;
- xoroshiro128++ as two 64-bit words;
- both word endiannesses and forward/reversed word order;
- one fixed state-advance stride from 1 through 32, required to hold across all four adjacent tab transitions.

No family/serialization/stride matched all four transitions. As additional controls, none of those same transitions matched PS-0417 attempt1 ACK→attempt2 ACK or attempt2 ACK→attempt3 REQUESTED. This is only a negative for state-snapshot transitions; it does not test your MT output-stage/stride hypothesis and does not authenticate the +305 join. No K04 candidate resulted.
