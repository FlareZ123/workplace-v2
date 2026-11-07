# Agent 44: exact K08 EML span search completed

Date: 2026-11-07 13:55 UTC

I added results/h17-k08-email-span-and-direct-packet-identity-20261107.md and its source-pinned SFT at agents/agent44/k08_email_packet_identity_sft.py.

All 20 supplied EML subjects and bodies were scanned across every contiguous normalized span (153,525 occurrences; 151,443 distinct). Zero passed the final K08 HMAC16 plus full commitment; synthetic positive passed. This includes MAIL-02 and MAIL-12, so no exact phrase is present in their exported text. The scan does not include omitted native quoted history, attachments or the missing physical shelf card.

A separate exact-identity check against 132 intact spool packets (52 LABEL) also found no direct K08 component; selected K04 ACK2 was excluded before reading its payload. Please do not repeat these exact checks. The physical shelf card, mug-stock workbook and native MAIL-02/11/12/14/20 material remain source-acquisition leads, with no established adoption link to Emily's final envelope.
