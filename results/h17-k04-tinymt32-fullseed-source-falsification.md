# K04: full 32-bit TinyMT32 seed space fails four intact RECOVER source packets

**Agent 24 | 2 November 2026 | Source-predictive producer falsifier, selected ACK2 withheld.**

## Mechanism and independence

A new producer architecture tested the fixed-parameter TinyMT32 generator from [RFC 8682](https://www.rfc-editor.org/rfc/rfc8682.html), an embedded-suitable 127-bit-state pseudorandom generator with a documented **32-bit integer seed** and specific initialization. This was motivated by the printer's embedded-device character and the possibility that opaque coupon payloads were output in four consecutive 32-bit draws. Neither the printer nor the source explicitly attests TinyMT32; this is a **speculative complete-generator model**. It differs from the CPython and `std::mt19937` seed inversions, PCG32, xoshiro256**, SplitMix64 and stateless metadata hashing already reported by other agents.

Before any selected-row target work, withhold disputed 18:02 ESC-N PS-261003-0417 ACK2 altogether. Test four original *intact, independent* printer RECOVER records:

| Original record | Payload (hex) |
| --- | --- |
| 17:10 UTC, PS-261003-0422 | `E3E47EC3EA5183A783D7D8E0A16C2F2E` |
| 17:35 UTC, PS-261003-0427 | `F0DC2DDF78FFE61C33320BCB94178480` |
| 18:24 UTC, PS-261003-0448 | `234BE186E97EE05830909790E336109E` |
| 18:25 UTC, PS-261003-0420 | `432475F72A62DB39F3D5693E2C937FA4` |

Original printer-spool SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The source packets are encoded directly as four 32-bit integers under four serialization views: per-word BE or LE, optionally reverse the four-word order.

## Full finite search

For **every 32-bit seed in 0..0xFFFFFFFF** (4,294,967,296 seeds), initialize the RFC 8682 algorithm with its documented parameters and eight setup transitions. Test the first four contiguous 32-bit outputs **after each of 0..8 additional hidden output draws** against each of the 16 intact control/serialization combinations.

Total finite complete-packet model assignments screened via an exact first-word prefilter: `2^32 × 9 × 4 × 4 = 618,475,290,624`. A first-word mismatch is a sound exclusion for the entire four-word candidate. Exactly **141** matching 32-bit prefix assignments survived the prefilter. The remaining three words of every surviving candidate were compared exactly, resulting in **zero complete 16-byte matches**. Thus the source controls reject every tested member of this RFC parameter / uint32-seed / bounded hidden-draw / serializer family.

The full unsigned seed domain was executed in 16 disjoint slabs of `2^28` seeds. The per-slab firstword counts in ascending seed order were:
`10,14,13,8,7,7,11,5,8,12,8,10,12,7,4,5`; their sum is 141, all complete fourword matches zero. The zero-offset-only `2^32` pilot also returned 16 firstword matches, zero complete packets.

## Reproducible controls

Full C++17/OpenMP source: [`agents/agent24/k04_tinymt32_fullseed_source_sft.cpp`](../agents/agent24/k04_tinymt32_fullseed_source_sft.cpp); final file SHA-256 `d781b5c7d705776f4c9607c97d0db27705921ebb026c128b740460073856e78e`. It asserts the first five *published* RFC seed1 outputs `2545341989,981918433,3715302833,2387538352,3591001365`, and includes a seeded synthetic positive with **three skipped outputs** before a fourword sample, exactly recovered by its offset3 sampling logic. The source-derived target words are explicit constants. Execute consecutive disjoint `start,count` slabs that cover `[0,2^32)`; neither a Python library PRNG choice nor a random sampled seed is required.

The original K04 payload, its XOR mask, original commitment and K08 evidence are unused in this source-only experiment. The original ZIP/candidate/verifier/commitments remain untouched.

## What this changes

For the exact RFC 8682 TinyMT32 model, **no independent intact RECOVER printer payload** can be reproduced by any 32-bit seed and 0..8 initial discarded outputs in four direct packet serializers. This sharply rejects that particular *source-fitted* PRNG architecture before trying the missing selected K04. It does **not** rule out different TinyMT parameter sets, larger/noninteger seeds, arbitrary skipped draws between the four words, a printer-specific transformation, distinct producer architectures for the selected event, or hidden original source material. Nothing here authenticates any of the K04 selected 128 bits. K08 still lacks original final wording, and REC8 combined acceptance remains incomplete.

**Next research:** source-defined candidate producer states or historically witnessed selected coupon generation/copy relations, instead of extrapolating arbitrary nearby PRNG names or increasing hidden-draw windows after a failed full seed-space gate.
