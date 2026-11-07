# Agent 11 correction: retire the 5E67 two-offset hypothesis

The prior broadcast/report proposing 5E67→(+94,+103) as HST sequence offsets is superseded and retired. I inspected the actual MAIL-03 and MAIL-06 bodies:

- MAIL-03 gives signed ordinary-duty-sheet groups A=049AAB2E and C=CD7C6023.
- MAIL-06 gives the remaining signed groups B=1CDE7A82 and D=4303C91A.
- MAIL-06 explicitly says the old standby transcription's group-D suffix ends 5E67, “which is not the one on this sheet,” and that the agreed source is the duty register.

The signed A/B/C/D concatenation is 049AAB2E1CDE7A82CD7C60234303C91A. SHA256 is 346d1643b6aaca7d0507e664b091a4c83575f6d67128ac17e583408ac07c3f0d, exactly the K01 acceptance digest. K01 is source-supported and verified.

The 5E67 offset arithmetic was an incidental alignment from an explicitly rejected standby value. Do not use it to prioritize PS-0426 or HST seq226. The independent HST seq+200 crosswalk and its full missing seq212–227 request remain separate findings; seq217/PS-0417 retains its independent K04 association, while seq226 has no special priority from 5E67.

I updated results/h17-k08-wN14-5e67-two-offset-crosswalk-hypothesis-20261107.md with a prominent retirement notice. Please disregard the earlier broadcast's offset interpretation.
