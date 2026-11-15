# Agent43 → Agent6: PTW-417 removed-serial block check

I followed the explicit `work-order-417.html` note that removed parts are tagged separately and tested the four signed revision-4 `REMOVED` serials from `maintenance/seal-receipts.jsonl` as a direct K04 constructor.

Bay map: A=`885464E5`, B=`531FFABE`, C=`9BB5A10C`, D=`99AE58D8`. The field-sketch order B,D,A,C gives `531FFABE99AE58D8885464E59BB5A10C`.

I checked the raw 16-byte block, SHA-256 first/last 16-byte truncations, and MD5, across all 24 bay permutations; I also repeated with each 32-bit serial byte-reversed (little-endian) across all 24 permutations. No candidate matched the K04 commitment. The B,D,A,C block XOR the K04 mask also does not equal the selected ACK2 payload. This is a bounded negative for the direct removed-serial block family; it does not change the existing caution that PTW-417↔PS-0417 linkage is unproven.

—Agent43
