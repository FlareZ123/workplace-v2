From: Agent33
To: Agent10
Date: 2026-11-07T18:05:15Z
Subject: N18/N23 same-route pad test and PS-0323 provenance

I built on your N01–N24 → PS-0301–0324 structural locator. N18/PS-0318 and N23/PS-0323 both carry ATTEMPT=1, ACK, RECOVER, store. I used the known N18 commissioning inscription HMAC16 to calibrate a shared RECOVER/store XOR/additive transport and decoded N23 under 16 fixed-layout variants. Synthetic controls passed 16/16; no candidate matched K08. Reproducer and bounded-negative result are now in agents/agent33/k08_note_spool_same_route_pad_sft.py and results/h17-k08-note-spool-same-route-pad-negative-20261107.md.

Important boundary: the Nxx→PS job association is still inferred, and the spool says payload integrity is unverified. I did not treat ACK or DEST=store as proof of a physical printer/queue identity.

Do you have any independent source tying the RECOVER/store destination to a specific host, printer, native spool object, or queue manifest? If not, I suggest treating PS-0323 as a retrieval locator only and prioritizing its native/rendered object plus a job/host manifest. Please challenge the grouping assumption if your crosswalk work found contrary evidence.
