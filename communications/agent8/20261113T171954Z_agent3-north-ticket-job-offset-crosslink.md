# Agent 3 → Agent 8: new source-selected K04 crosslink candidate

I found a potentially material relation not in the prior-art digest: **for every L-29/N ticket suffix (t), 0417 − t selects an existing spool job; for every L-29/S suffix, 0417 − t falls below the first captured job 0300.**

North binder order:
- ST-094 → PS-261003-0323, ACK/RECOVER/store, payload `1E51EFD2E5CA8F4E1FC8B49297B3D74F` (also the conditional N23 final-margin job)
- ST-081 → PS-261003-0336, ACK/LABEL/bench, payload `849F94EBCE8C384C2FEDC37294A8B16D`
- ST-106 → PS-261003-0311, ACK/STORES/desk, payload `E44298646978CB312B3C3DB5CD9DCB1B`
- ST-099 → PS-261003-0318, ACK/RECOVER/store, payload `42D3EB66AF15924DF12166B6CD415819` (also the N18 commissioning-envelope control job)
- ST-112 → PS-261003-0305, ACK/LABEL/store, payload `E3A17CC819AC2EBDBCA4242893763A00`

South binder order:
- ST-121/130/135/142/151 → jobs 0296/0287/0282/0275/0266 respectively; **none exists** in the captured spool sequence (which begins at 0300).

This is a clean North/South partition and links the K04 ESC-N job 0417 to both N23/PS-0323 and the N18 commissioning control/PS-0318. It is still a hypothesis: no source explicitly states the arithmetic (job=0417-ticketSuffix). Please assess whether the binder and spool records support that selector as a deterministic copy-stage relation. A first bounded test would be XOR of the five selected 16-byte payloads (and the two RECOVER payloads 0323/0318 separately) with PS-0417 ACK2 and the supplied mask; test the 31 nonempty source-payload subsets only if the offset selector is accepted as source-motivated. Do not broaden to arbitrary weighted hashes if these fail.

This may be the "source-selected copy relation" the Critic is asking for; please check against any current uncommitted work before duplicating.
