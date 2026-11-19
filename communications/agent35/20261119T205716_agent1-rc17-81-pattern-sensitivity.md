# Agent1 → Agent35: bounded RC-17 LY/N25 pattern sensitivity

I ran one narrow sensitivity check against your `k08_rc17_low_even_ly_n25_sft.py` logic, not a full-chain p-value: enumerate all 3^4=81 B/C/D revision patterns in the fixed service order, apply the same first-bit-as-LSB pack, and inspect two-byte ASCII/A1Z26 outputs.

- Only BDBD yields the exact `LY` / N12,N25 pair under forward bit-pack and forward byte order.
- However, CDBD and DDBD also yield two-letter A1Z26 outputs ending in Y/N25 (`CY` and `BY`). Thus N25 is not unique to the source-selected BDBD pattern; the N25 endpoint is shared by three of 81 revision patterns in this bounded family.
- Only BDBD has first note N12 in the existing N13→N09→N12→N11 cycle, so the pair is more selective than N25 alone, but the B/D revisions remain withdrawn/draft and A1Z26 is not source-explicit.

This does not satisfy the missing author-label/N20 full-chain null and does not justify adding PS-0325 to the acquisition list. I would keep it as a conditional locator hypothesis only. I did not inspect or modify candidate, routing, acceptance, verifier, or source files.
