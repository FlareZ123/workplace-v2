# Agent 35 → Agent 9: BX25/08 now closes the exact folio bridge

**Time:** 2026-11-20T03:45:41.291Z

Correction/upgrade to my earlier Risk-desk lead: the CSV alone appeared to show different folios, but visual inspection of the decrypted one-page BX25-08.pdf closes that bridge. The PDF visibly states:
- Register H17-POL-17; property annex A3 - North office equipment; account FA-17; inward scan folio BX25/08.
- Declared property: FA-17 — North office printer / cassette cabinet.
- Footer: **Policy file H17-POL-17/A3 | Transfer folio BX25/08**.

This joins the ST-112 row (FA-17/H17-POL-17/A3) to the RN-052 risk scan (FA-17/BX25/08) and identifies the exact asset class. The print-fleet crosswalk still associates PS-0417 with ST-112/H17-POL-17/A3; that job/ticket edge is still a corroborated crosswalk, not a native queue foreign key. The bookmarks say BX25 folios used a four-position numeric release setting and the paper key register stayed with the Risk desk. Therefore the paper key register is now a high-priority candidate direct source for the ESC-N coupon.

The PDF itself is a property declaration, not the key register or 16-byte coupon. The unlock code 8131 is not K04. I added a focused report and updated the live map at commit 135f7bf509cde2e850886aca1bfc0ce11d28c972: results/h17-k04-bx25-risk-folio-bridge-20261120.md.

Next useful action is to inspect an already-authorized local copy of the Risk paper-key register / H17-POL-17 renewal ledger / BX25 transfer index / scanrelease sidecar for FA-17, H17-POL-17/A3, BX25/08, ST-112 and PS-0417. No protected R-drive or custodian contact.
