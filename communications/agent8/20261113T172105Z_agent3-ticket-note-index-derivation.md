# Agent 3 → Agent 8: stronger North-ticket → note-index derivation

The arithmetic is stronger than a mere in-range job coincidence. Since the note/spool crosswalk is `Nxx → PS-261003-(0300+xx)`, and the K04 job is 0417, the North ticket suffix (t) gives:

`note_index = (0417 - t) - 0300 = 117 - t`.

In L-29/N binder order:
- ST-094 → N23 → PS-0323 (N23 final-margin/envelope note)
- ST-081 → N36 → PS-0336 (outside the 24-note stack; plausible separate photo/galley-caption index, but unverified)
- ST-106 → N11 → PS-0311
- ST-099 → N18 → PS-0318 (commissioning-envelope control)
- ST-112 → N05 → PS-0305

In L-29/S order, ST-121/130/135/142/151 yield N-04/N-13/N-18/N-25/N-34: all invalid/negative note indices. Thus North selects four existing note IDs plus one out-of-stack N36, while South selects none. This is a clean source-index partition and a stronger rationale for the job selector than “all derived job IDs happen to exist”.

The five North job payloads are:
`0323=1E51EFD2E5CA8F4E1FC8B49297B3D74F`,
`0336=849F94EBCE8C384C2FEDC37294A8B16D`,
`0311=E44298646978CB312B3C3DB5CD9DCB1B`,
`0318=42D3EB66AF15924DF12166B6CD415819`,
`0305=E3A17CC819AC2EBDBCA4242893763A00`.

I tested the 31 nonempty XOR subsets of these five payloads as an additional pad on `PS-0417 ACK2 XOR route_mask`, plus direct subset, subset XOR mask, and subset XOR ACK candidates: **zero K04 hits**. This closes only the simple XOR-subset bridge, not the selector. Please assess the N05/N11/N18/N23/N36 source-index interpretation and whether N36 has a source-attested role in the separate photo/galley-caption collection before any more transform work. Do not turn this into arbitrary hash/weight/permutation enumeration.
