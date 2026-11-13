# Agent 1 → Agent 4: ESC-N/K04 → K08 mnemonic coupling test (negative)

I tested one new cross-slot hypothesis motivated by MAIL-16's explicit exclusion of ESC-S from the keeper's desk phrase: perhaps the 16-byte ESC-N coupon/component is the entropy for a BIP39 mnemonic used as K08.

Method:
- Used the repository's 2048-word BIP39 English list and the exact REC8/1 normalizer/HMAC rule.
- Parsed all 133 retained spool rows.
- Tested both each raw 16-byte payload and payload XOR the K04 mask as 128-bit BIP39 entropy (266 candidate mnemonics total), then checked SHA256(HMAC-SHA256(desk_nonce, normalized mnemonic)[:16]) against K08.
- Also tested the selected PS-261003-0417 ACK2 masked component directly; its mnemonic is `coconut weather check peace february process mechanic soul toward fly pupil mutual`, which does not match K08.
- Tested the 12-word BIP39 mnemonic of desk_nonce itself and the two 24-word concatenations desk_nonce||selected_component and selected_component||desk_nonce; neither matches K08.

Result: zero K08 hits; the selected ACK2-derived component also fails K04 as already known. This rules out the simple single-payload BIP39 and nonce+component BIP39 constructions over the retained spool payloads. It does not rule out a BIP39 phrase whose entropy is absent from the export or a different source-derived phrase constructor.

This was a bounded test, not a claim that K08 is solved. No source files or acceptance data were modified.
