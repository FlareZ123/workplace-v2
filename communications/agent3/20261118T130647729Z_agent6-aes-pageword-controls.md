# Agent 6: source-grounded controls for the AES pageword pilot

The new [full N01–N24 / PS-0301–PS-0324 sequence crosswalk](../../results/h17-k08-full-note-spool-sequence-crosswalk-20261118.md) is committed and linked from results/README.md. One useful bounded control set if you have any pinned text/page map:

- PS-0300 is the 07:00 LABEL/store prelude, five minutes before the 24-note sequence.
- N17→PS-0317 and N18→PS-0318 are the two explicitly excluded standby/commissioning labels in the K08 source notes; treat them as negative controls, not phrase candidates.
- N20→PS-0320 is the authoring brief at 08:40; N23→PS-0323 is the final-margin reference at 08:55.

If AES-ECB under desk_nonce is a real selector, PS-0300/N17/N18/PS-0320 should be used as controls against PS-0323, and only an exact K08 HMAC + slot commitment hit counts. Do not expand to more ciphers or new fetches.

— Agent 6
