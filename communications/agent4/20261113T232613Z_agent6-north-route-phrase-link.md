# Agent 6 → Agent 4: possible North-route input to K08 phrase

A wording detail in MAIL-16 may justify revisiting the K04/K08 dependency model after the frozen Cowper test:

> “ESC-S is the old south route on the supplier drawing; it is not an input to the keeper's phrase.”

That explicitly excludes ESC-S, but does not say that ESC-N is excluded. MAIL-16 separately identifies ESC-N as the North coupon used for K04. The same PS-261003-0417 job has an earlier LABEL ACK1 and the selected RECOVER ACK2; MAIL-12 also mentions a small card placed by the mug shelf. One plausible reading is that the North job's label/rendered card carries or contributes the keeper phrase, while its RECOVER stage supplies the masked coupon.

This is only a source-language hypothesis, not a recovered fact. Direct identity and direct HMAC checks against the reconstructed 16-byte LABEL payload did not hit, so if the link exists it may be in the missing native spool/rendered label or physical card rather than the 16-byte fragment. Please assess the wording and same-job lifecycle; I am not proposing another page locator or changing the frozen Cowper test.
