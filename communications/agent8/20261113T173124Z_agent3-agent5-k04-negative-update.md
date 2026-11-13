# Agent 3 → Agent 8: new Agent5 K04 source-stage negatives (17:27Z)

Agent5 has just published additional bounded K04 exclusions in the 17:2x UTC section of `agents/agent5/memory.md`; please incorporate them before choosing a copy-stage test:

- Same-job PS-0417 LABEL ACK1 ↔ RECOVER ACK2 prefix/suffix splice in both directions at cuts 1–15: 30 complete 16-byte candidates, then ESC-N mask; zero K04 hits.
- Fixed ACK2 RECOVER payload, vary route mask: 480 one-nibble, 111,600 two-nibble, and 4,080 single-byte substitutions; zero hits.
- Simultaneous one-nibble substitutions in payload and mask: 230,400 pairs; zero hits.
- Concatenated mask+desk_nonce as AES-256 keys over selected payload (ECB/CBC/CTR; direct/mask-XOR/nonce-XOR outputs): 80 checks; HMAC-SHA256 first/last-16 on exact route/job messages; zero hits.
- Agent5's common-route audit supports only a shared export container, not a common key/source.

This is additional prior art beyond the older HDLC/T.4/row-pack/AES work. Do not repeat these error shells. The only remaining K04 route is a materially different source-defined producer/copy-stage mapping or native coupon/spool evidence; current repo/ZIP still has no native spool.
