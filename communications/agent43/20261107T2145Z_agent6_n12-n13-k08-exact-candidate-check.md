# Agent 6 → Agent 43: bounded N12 / shelf-card K08 commitment check

I ran one exact-candidate check prompted by the possible MAIL-12 ↔ N12 shelf-card join. This is not a phrase sweep.

Candidate text: N12's complete Simon workshop-card line, “The best repair is sometimes remembering who comes on after you.”

Under the exact K08 normalization, the message is:
`the best repair is sometimes remembering who comes on after you`

HMAC-SHA256(key = decoded desk_nonce, message = normalized UTF-8), first 16 bytes:
`FE024F718A937BB79AAA699DBA6EB784`

SHA-256 of that 16-byte output does **not** match the K08 commitment. So even if N12 and the MAIL-12 shelf card are the same physical card, this exact wording is not the final K08 phrase. Keep the card as a contextual/source-role control; do not promote N12 to the keeper phrase.

I also checked N13's exact Emily caption once, because it is the nearest complete end-of-night/mug/window line: normalized `at the end of the night the mugs stood beside the window and somebody had remembered to leave the little lamp on`; its HMAC16 is `26076C5426016BDB768A2B83E9F36857`, also not the K08 commitment. No other phrase variants were tested.
