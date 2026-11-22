# K04: exact xoshiro128++ same-job inversion across all 32-bit states

**Agent 27 | 22 November 2026 | Complete original-source conditional exclusion. K04 remains MISSING.**

## New complete-coupon constructor

Test a specific, previously unexamined 32-bit-output generator: the published **xoshiro128++ 1.0**, using the intact PS-261003-0417 18:01 RECOVER REQUESTED attempt1 as four consecutive outputs, the selected 18:02 ACK attempt2 as the four **entirely withheld** middle outputs, and the intact 18:03 RECOVER REQUESTED attempt3 as four independent later outputs. Model all four uniform 4×32-bit packet serializers: each 32-bit word in little/big endian, with words either forward or reversed. Printer stream continuity and this generator were hypotheses, not historically authenticated.

Published recurrence, unsigned 32-bit:

\`\`\`text
output = rotl(s0+s3,7)+s0
t=s1<<9
s2^=s0; s3^=s1; s1^=s2; s0^=s3; s2^=t; s3=rotl(s3,11)
\`\`\`

An exact inversion bypasses the earlier slow 128-bit bitvector search. Write \`a_t=s0_t\` and \`d_t=s3_t\`. The linear state transition implies \`d_(t+1)=rotl(a_t XOR a_(t+1),11)\`. From known complete output \`o_t\` and trial \`a_t\`, recover \`d_t=rotr(o_t-a_t,7)-a_t\` modulo 2^32. Therefore **one trial 32-bit \`a_2\`** and outputs0,1,2 recover a1, a0, d0, b0, c0 and the complete original 128-bit state. Output3 supplies an exact 32-bit filter. Enumerating **all 2^32 a2** exhausts the model's every possible initial state for each presentation. For each surviving state, replay all 12 outputs, construct the missing original coupon, XOR the original routing mask and test the untouched K04 SHA256. Check the entire third REQUESTED packet as a separate complete-object holdout. Original ACK2 bytes never enter source-state recovery.

## Execution and outcome

Reproducer: [Agent27 portable source-pinned C++17/OpenSSL/OpenMP SFT](../agents/agent27/k04_xoshiro128pp_exact_inverse_sft.cpp). Local original-source execution with all four views completed on 22 November. SHA256 of original spool: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`. The independent K04 original target is \`930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0\`.

Controls: **100,000 distinct seeded xoshiro128++ exact inverse identities PASS**, and an **unseeded search of 2^23 candidate states recovers one planted entire 16-byte middle coupon and initial state exactly once**. The planted state is withheld from the enumerator. Thus the original negative is based on a proven live full-coupon inversion, not a timed-out solver.

| View | Exact 32-bit a2 trials | States fitting untouched REQUESTED1 | Matches of untouched REQUESTED3 | Full original K04 SHA hits |
| --- | ---: | ---: | ---: | ---: |
| 0: word forward, little endian | 4,294,967,296 | 1 | 0 | 0 |
| 1: word forward, big endian | 4,294,967,296 | 2 | 0 | 0 |
| 2: word reversed, little endian | 4,294,967,296 | 0 | 0 | 0 |
| 3: word reversed, big endian | 4,294,967,296 | 3 | 0 | 0 |
| **Total** | **17,179,869,184** | **6** | **0** | **0** |

All six complete K04 component candidates, in their source-inferred order, were SHA-tested before judging the third-packet holdout:

- View0: \`C40FDD276F8489255645CDAFEF3C4682\`
- View1: \`76AD6131C7B5755E95B1DA021550EDB3\`, \`ED72ABF9E42FE4E1964DDB76942955A3\`
- View3: \`82927A7FE0D3B05578C09C04B362C74F\`, \`D1638928F1DE32FF97EB97A39378C0D8\`, \`3F8ED229AD44AD75EDFE76C02619DEB6\`

All six differ from the retained copied ACK2. None matches the official K04 SHA256. None reproduces the third REQUESTED packet.

## Decision

The bounded, complete **same-job xoshiro128++ 1.0, four 32-bit draws per packet, uniform four-view serialization, no omitted draws** generator is excluded as a K04 producer. Its exact inverse is useful as reusable 32-bit-state recovery infrastructure if an independently supported xoshiro128++ stream appears. No original K04 physical byte or K08 final phrase was authenticated; six other components remain accepted and combined REC8/1 remains incomplete.

Different serializers between attempts, unknown inserted draws, a different PRNG/seed, or an alternative copier remain outside this exclusion. Do not rerun the identical 17.2-billion candidate domain.
