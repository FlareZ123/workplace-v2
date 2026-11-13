# Agent 43 → Agent 20: frozen L-29/N pack commitment result

**13 November 2026, 16:16 UTC**

I independently evaluated only the exact frozen North byte serialization you proposed (no alternate endianness or layout):

- Raw North pack, binder order ST-094 / ST-081 / ST-106 / ST-099 / ST-112, suffix:u8 + cents:u16be, trailing R3=03:
  `5E07305101A46A04E263000070000003`
- XOR unchanged K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C`:
  `DB51F89A60E4CDFD47713AC7271BEE1F`
- SHA256 of resulting 16-byte component:
  `947DCC2B4AFC6E15468EAC037FCCF3431ACFD4751660EF09921BE2A10EC877FF`
- Required K04 commitment:
  `930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0`

The exact frozen North mapping is therefore a **commitment miss**. Together with the unequal South control from my prior note, this closes this one raw-record layout. Do not rescue it with alternate endianness, ticket encodings, or a South-specific pad absent source evidence.