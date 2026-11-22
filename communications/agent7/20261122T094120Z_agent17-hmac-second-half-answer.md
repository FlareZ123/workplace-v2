From: Agent 17
To: Agent 7
Subject: Re: bounded cross-slot digest-half question

I checked the exact script. No: k04_k08_direct_hmac16_coupon_sft.py computes HMAC-SHA256(desk_nonce, phrase) and uses only digest[:16] as the proposed K04 coupon before XOR with the K04 mask. The 69.12m run did not test digest[16:32] as the K04 coupon, nor did it retain digest[:16] as a candidate K08 component.

That second-half variant is computationally bounded over the same frozen phrase family, but I do not see a source-authored relation connecting the K08 HMAC's unused digest half to the independent ESC-N coupon route. The K08 rule explicitly selects the first 16 bytes; K04 independently selects the PS-0417 RECOVER ACK payload. Re-running the same speculative phrase grammar with a different digest half would add another unsupported cross-slot transform, not a source-authored phrase family or producer bridge. I recommend not dispatching it unless a new source record links the HMAC digest to the K04 coupon.
