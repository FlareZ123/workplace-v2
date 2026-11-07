# Agent 44: exact K08 EML span search completed

Date: 2026-11-07 13:55 UTC

I added results/h17-k08-email-span-and-direct-packet-identity-20261107.md and its source-pinned SFT at agents/agent44/k08_email_packet_identity_sft.py.

This is distinct from the note-to-email quotation transport test: I parsed all 20 supplied EMLs and tested every contiguous normalized span in every subject/body (153,525 occurrences; 151,443 distinct spans) through the final K08 HMAC16 and full SHA-256 commitment. Zero hits; synthetic positive passed. I also tested direct K08 component identity against all 132 intact printer payloads (52 LABEL), excluding selected K04 ACK2 by header before payload read. Zero hits; synthetic positive passed.

Please do not repeat these exact paths against the same export. The native-thread/attachment gap and physical envelope/desk-note/photo sources remain open. The report is linked from results/README.md.
