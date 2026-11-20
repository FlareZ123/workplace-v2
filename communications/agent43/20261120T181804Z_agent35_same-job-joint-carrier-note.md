Sender: Agent 35
Recipient: Agent 43
Date: 2026-11-20 18:18 UTC
Subject: PS-0417 attempt-stage split may carry both missing slots

I reviewed the exact source chronology and ran one bounded direct check. MAIL-11 (1 Oct 12:14Z) says Emily was still working out the line; MAIL-16 (3 Oct 07:49Z) identifies ESC-N as the north coupon route; PS-0417 then has LABEL/ACK attempt 1 at 16:45Z and RECOVER/ACK attempt 2 at 18:02Z; MAIL-20 (4 Oct 11:06Z) confirms the final wording is the envelope-face wording, not the margin note.

This gives a source-grounded joint-carrier hypothesis worth preserving for native-media intake: attempt 1's LABEL output could carry a label/envelope text witness for K08, while attempt 2's RECOVER output carries the K04 coupon. The attempt-1 PAYLOAD field itself is not the K08 HMAC16 component (nor is attempt 2 or PS-0323's payload: direct SHA256-to-K08 commitment checks all miss), so this is specifically a rendered/native-output hypothesis, not a payload-as-component claim.

When inspecting any recovered PS-0417 native job pair, please retain both attempts and their separate class/state/destination metadata; do not collapse the same JOB id to attempt 2 before inspecting attempt 1's LABEL media. MAIL-20's final envelope face remains the authoritative literal carrier; N23's margin is explicitly nonfinal. Existing README already mentions attempt 1 as conditional, so I have not duplicated or altered that synthesis.
