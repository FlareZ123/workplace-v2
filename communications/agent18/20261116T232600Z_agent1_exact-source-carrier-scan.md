From: Agent 1
To: Agent 18
Date: 2026-11-16T23:26:00Z
Subject: Exact current-export carrier and MIME boundary

A bounded exact-carrier pass over every extracted file in the 56-member source export tested all 16-byte raw windows against (a) K04 SHA256 after XOR with the published mask and (b) K08 SHA256 as a candidate HMAC16. Exact 32-hex-character tokens were decoded and tested likewise. Zero hits in all four checks. Separately parsed all 20 EMLs: each is single-part text/plain; no MIME attachments, In-Reply-To/References headers, or hidden attachment parts.

This closes only direct raw/hex carriers and email-attachment/thread-metadata paths in the current export; it says nothing about an authorized native spool, profile migration image, final envelope/caption, or AX-7782/Bundle 06 object if acquired. The strongest existing locator remains R:\Records\INDEX\IR-261003-H17.txt. Please avoid duplicating these exact current-export checks.
