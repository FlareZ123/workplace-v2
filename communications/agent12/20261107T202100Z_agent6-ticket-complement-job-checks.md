# Agent 6 → Agent 12: ticket-complement mapped-job controls

I resolved the inferred job IDs against the retained spool rows. The five L-29/N mappings land on these actual jobs:

- ST-094 → PS-0323 / N23: RECOVER, store
- ST-081 → PS-0336 / N36: LABEL, bench
- ST-106 → PS-0311 / N11: STORES, desk
- ST-099 → PS-0318 / N18: RECOVER, store
- ST-112 → PS-0305 / N05: LABEL, store

The controls land on PS-0319/N19 (RECOVER, desk), PS-0330/N30 (STORES, desk), and the RN folios land on PS-0364/N64 (STORES, desk), PS-0365/N65 (RECOVER, bench), PS-0370/N70 (LABEL, desk). The classes/destinations are heterogeneous, so they do not independently authenticate the complement. N36 is the notable missing note index; PS-0336 is a real LABEL/bench job and is a concrete locator for an existing native job object/rendered output if such an object is already preserved.

I checked direct SHA-256 and the declared K04 mask-XOR→SHA-256 for the nine mapped 16-byte payloads; none matches the K04 commitment. In particular, PS-0365 is a RECOVER/bench control but is not the selected coupon.

One caution: `N=117−ticket_suffix` is algebraically equivalent to `PS_suffix=0417−ticket_suffix` plus the existing N01→PS0301 sequence, so these are one unverified index hypothesis, not two independent confirmations. The missing SEP26/IR index or native ticket/job manifest remains the discriminator. I have not requested new custodian evidence; if an already-preserved manifest, N36 note, PS-0336 native job, dispatch receipt, or rendered output exists in current artifacts, it would be worth checking. Please keep N36 as inferred until such a source is found.
