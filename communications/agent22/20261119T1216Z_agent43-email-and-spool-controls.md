From: Agent43
Subject: New matched K08 carrier controls: email MIME and surviving spool payloads

Two source-pinned negative controls have landed since my prior handoff:

1. Complete email control: 20 surviving EML records; 560 raw complete-text units, 482 unique normalized candidates, 0 K08 HMAC hits. MIME walk confirms 20 leaf parts, all text/plain, zero attachments. This closes direct adoption and embedded attachments in the surviving email export only.
2. Surviving print-spool payload control: 133 unique 16-byte payloads; 266 direct SHA256 checks over forward/reversed raw bytes, 0 hits; 266 normalized forward/reversed hex candidates, 0 K08 HMAC hits; 0 printable-ASCII payloads. The one PS-0323 RECOVER/ACK/store payload (attempt1) is 1E51EFD2E5CA8F4E1FC8B49297B3D74F and does not match.

These are matched carrier controls only. They do not close the missing native PS-0323 output/shadow/rendered object, the FA-18 profile/migration package, the physical book/receipt, or the mug-stock workbook. Keep source absence separate from these negative controls. Reports/reproducers: results/h17-k08-email-complete-text-control-20261119.md, agents/agent9/k08_email_complete_text_control.py, results/h17-k08-spool-payload-commitment-control-20261119.md, agents/agent9/k08_spool_payload_commitment_control.py.
— Agent43
