# K04 native scalar MT19937 seed exclusion with fifteen pre-spool output origins

**Agent 3, 3 November 2026.** No original K04 component or K08 caption recovered.

## Fresh origin hypothesis

The existing printer-only speculative p951 native-MT recurrence places the first ordinary intact printer ACK at relative word index 0. Other original-source words reconstruct at **negative** native indices. PTW-405 original signed serial F6E935B9 is an independent source-carrier match to the little-endian tempered MT word B935E9F6 at **relative -964**.

Instead of supposing the printer began immediately at a seed-initialized generator's first output, posit that a generator with a single unsigned 32-bit **native std::mt19937 seed** first emitted at one of fifteen earlier, fully source-determined native positions. For each candidate origin, compare its first seeded output and the next two fixed words in the published p951 source chronology. Origin selection is hypothetical and has **no independent historical timestamp or seed-start attestation**.

The source-frozen origin/first-word pairs are:

| Native relative index | Tempered first output |
|---:|---|
| -1081 | 1CC39602 |
| -999 | BE48792F |
| -964 | B935E9F6 |
| -938 | 44744295 |
| -904 | C1968864 |
| -810 | 7A906F32 |
| -775 | 99E65DD9 |
| -769 | F9CE04EA |
| -761 | F1399CE6 |
| -754 | 2A5108F0 |
| -685 | 1D73A775 |
| -684 | 2C912643 |
| -683 | 96AFCA09 |
| -677 | D1326968 |
| -670 | 16F14FA5 |

For each origin except the last, the next two rows are its source-fixed forward controls. For the final origin -670, independently fixed follow-ups are native -622 = 73182ED3 and -616 = 0BD9F8B8.

The original 132 intact spool rows and their source-derived p951 recurrence, excluding disputed row129, provide all fullwords. SHA-256 of unmodified spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. Original receipts SHA-256: c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32. Selected ACK, route XOR mask, target commitments, and K08 were **not used** to select or test seeds.

## Full 32-bit-domain cracking result

An AVX2 eight-lane first-output implementation of the exact C++ scalar MT19937 initialization, twist, and temper was calibrated against real std::mt19937 seeded outputs, including known seed 5489 producing 3499211612 and five distinct seeded-control cases. Candidate first-word hits were verified with independent standard-library generator output at the exact next source-derived offsets.

| Disjoint seed interval | Full seeds | First-word hits across 15 origin tests | Survived second word |
|---|---:|---:|---:|
| [0,1073741824) | 1,073,741,824 | 6 | 0 |
| [1073741824,2147483648) | 1,073,741,824 | 2 | 0 |
| [2147483648,3221225472) | 1,073,741,824 | 6 | 0 |
| [3221225472,4294967296) | 1,073,741,824 | 4 | 0 |
| **Total** | **4,294,967,296** | **18** | **0** |

Every seed from 0 through 4294967295 was tested at each of the fifteen positions: **64,424,509,440 complete first-word origin assignments**, 18 matches; zero candidate seed/origin assignments match the next original fixed word. The final -670 origin's one first-word seed 494480658 independently predicts 47CF4637 at -622 instead of 73182ED3, and 4C276185 at -616 instead of 0BD9F8B8. At -964 specifically, there are zero first-word matches for every possible unsigned 32-bit seed.

**Reproduction:** [Agent3's source-pinned C++ SFT](../agents/agent3/k04_native_pre_spool_seed_sft.cpp), compile with g++ -O3 -std=c++17 -mavx2 -fopenmp and -lcrypto; run the four nonoverlapping seed intervals above. Local compiled implementation completed all four shards; the committed portable variant preserves the same source inputs, algorithm and positive controls but has not separately been compiled on a fresh GitHub checkout.

## Exact scope

This is a complete exclusion only for **native std::mt19937 initialized by one uint32 seed and beginning at one of the fifteen selected historical-source-fixed negative output indices**, under the conditional p951 printer serialization/recurrence. Different first-output origins, hidden startup draws, multiword seeds, CPython's distinct integer seeding, alternate producers or copy damage remain open. The first-output epoch itself is not established by original records. No selected K04 source bit was authenticated; K08 exact final caption likewise remains missing. Six official individual components PASS, combined REC8 INCOMPLETE.