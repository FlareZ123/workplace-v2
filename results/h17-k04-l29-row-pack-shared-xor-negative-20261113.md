# K04: L-29 five-row binary pack and shared-XOR bridge (negative)

**Date:** 2026-11-13  
**Owner:** Agent 43  
**Status:** Exact row-pack misses K04 and fails South control; one-control shared-XOR bridge also misses.

## Question

Can the five R3/POSTED reconciliation rows in each L-29 binder set be serialized into one 16-byte record using five 3-byte rows `ticket_suffix:u8 || amount_eur_in_cents:u16be`, followed by a one-byte R3 code? If the direct serializer does not match the South control, does a single shared XOR copy-stage delta calibrated from the South set predict the North target?

This is a bounded hypothesis, not a documented vendor binary format. The source gives the row fields and binder order, but does not specify this binary serialization or a shared XOR copy stage.

## Source-pinned inputs

The reproducer is `agents/agent43/k04_l29_row_pack_negative.py`. It pins the supplier reconciliation CSV, print-fleet return register, spool reconstruction, recovery routing, and acceptance file. The print-fleet register gives these binder orders:

- L-29/N: ST-094, ST-081, ST-106, ST-099, ST-112.
- L-29/S: ST-130, ST-151, ST-121, ST-135, ST-142.

The North rows are FA-17 / H17-POL-17/A3, R3/POSTED. The South rows are LV-42 / CS-18/5, R3/POSTED. The South control is PS-261003-0448, attempt 1, ACK/RECOVER, payload `234BE186E97EE05830909790E336109E`.

## Frozen direct serialization

Each ticket suffix is parsed as an unsigned decimal byte. Each euro amount is converted to integer cents and encoded as unsigned big-endian 16-bit. The R3 run code is appended as byte `03`.

| Set | 16-byte raw serialization |
|---|---|
| North | `5E07305101A46A04E263000070000003` |
| South | `8201369700007902F88703D48E025803` |

The South serialization does **not** equal the source-pinned PS-0448 ACK/RECOVER payload. Therefore the direct serializer fails its intact role control.

For North, XOR with the unchanged K04 mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives:

`DB51F89A60E4CDFD47713AC7271BEE1F`

Its SHA-256 is:

`947DCC2B4AFC6E15468EAC037FCCF3431ACFD4751660EF09921BE2A10EC877FF`

Required K04 SHA-256:

`930A52A1BAB97CA2966332137C99E99298EA6182FB32AB63A3421DFB4FD8C9E0`

No hit.

## One-control shared-XOR bridge

As one deterministic follow-on, derive a shared 16-byte pad from South raw serialization XOR PS-0448 ACK, then apply the same pad to North:

- South-calibrated pad: `A14AD711E97E995AC81794446D34489D`
- Predicted North payload: `FF4DE740E8DAF35E2A7494441D34489E`
- After unchanged K04 mask: `7A1B2F8B899A54A78F66AE834A2FA682`
- Candidate SHA-256: `0BFEBAD3954E2AA590A02794F559C4A4AAF06B6F95E360D7641C0F2D10A57CEA`

No hit. The South pair calibrates this pad by construction, so it is not an independent validation of a shared copy-stage transform.

## Prior-art boundary and conclusion

This exact raw 5×(u8 suffix + u16be cents)+R3 serialization was not found in the adjacent Agent40 weighted mod-256/GF(256) reducers, Agent45 ticket-byte/shared-pad families, or Agent3's 96-candidate row-digest family. Those are distinct prior tests, not this direct pack.

Both the direct North candidate and the single shared-XOR bridge miss K04; the direct South control also fails. Do not rescue the mapping with alternate endianness, suffix encodings, per-byte pads, permutations, or account-specific masks absent a source-defined rule. No source file, route, candidate, or verifier was changed. No K04 component was recovered.
