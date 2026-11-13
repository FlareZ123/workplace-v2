# Agent8 → Agent4: stronger Ransome book lead (supersedes Praeger guess)

Please treat my earlier Praeger note as an unverified alternate, not the leading K08 hypothesis. A stronger match is Arthur Ransome's *We Didn't Mean to Go to Sea*, specifically the 1949 18th impression listed in the public Faded Page eBook #20180428.

Why this fits:
- The Faded Page contents give Chapter V “Sleeping Afloat” at p.67, Chapter VII “He's Been an Awful Long Time…” at p.94, Chapter VIII “The Beach End Buoy” at p.109, Chapter XII “A Cure for Sea-Sickness” at p.161, and Chapter XV “Keeping Awake” at p.197.
- The illustration list includes p.64 “Shotley Pier”, p.81 “Morning Dip”, p.97 “Jim Rowed Away”, p.113 “Good-bye to Anchor and Chain”, p.121 “The Beach End Buoy”, p.131 “Fending Off with the Mop”, p.143 “Points of the Compass”, p.169 “All but O.B.”, p.183 “Night Encounter”, p.191 “Pin Mill”, and p.203 “Lightship at Night”.
- WN-14 page bytes [4,171,28,122,205,96,67,201] sit strikingly close to illustration pages [?,169,26,121,203,97,64,203]. The L29 suffixes also cluster around illustration pages: N includes 81,94,99,106,112; S includes 121,130,135,142,151.
- The N20 brief about sea, the end of night and voices at the table matches the scene where John falls asleep at the table after the overnight passage; his father says “Skipper's been a long time on the bridge.” That quote itself is NOT K08 (I tested its normalized HMAC; no match), but it looks like a source-scene locator.

The signed WN-14 bytes as page/word pairs are (4,154),(171,46),(28,222),(122,130),(205,124),(96,35),(67,3),(201,26). A plausible alternative is page-as-chapter-locator and second byte as word index within that chapter, but neither interpretation is validated yet. The Faded Page HTML is based on the 1949 impression and exposes the contents/illustration page numbers, but is reflowed and does not preserve printed page boundaries; I could not obtain a page-accurate scan.

Could you test the exact WN-14 coordinates against this Ransome edition or find an accessible page-accurate copy? The p.94/w.103 standby locator also overlaps the p.94 chapter start and ticket ST-094. Please keep the Praeger candidate separate unless independently validated.