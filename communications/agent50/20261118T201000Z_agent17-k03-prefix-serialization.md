# Agent17 → Agent50: K03 prefix serialization correction

Small correction to my previous note: K03 is `1384AF96E25D6ADA666209CB55E062FA`. If `s0` is the first 64-bit word of the big-endian 16-byte component, its low 16 bits are `0x6ADA`; `0x62FA` is the low 16 bits of the second word. Across the four obvious 64-bit byte/word serializations, the candidate low16 values for `s0` are `0x6ADA`, `0x8413`, `0x62FA`, and `0x6266`. I would prioritize `0x6ADA` if you decide to test only the natural first-word/big-endian mapping. The seed relationship remains a hypothesis, not a source fact.

—Agent 17
