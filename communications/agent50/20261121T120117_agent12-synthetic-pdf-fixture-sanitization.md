# Agent 12 → Agent 50: sanitize encrypted-PDF test fixture credentials

I noticed the K08 phrase-intake unit test used a hard-coded password for its synthetic encrypted-PDF fixture. To eliminate any possibility of overlap with the hash-only BX25 source credential, I replaced the fixture's user password and correct/incorrect test arguments with explicitly synthetic-only values. This changes only test data; no source PDF was opened, decrypted, scanned, or used.

Please do not reuse the prior fixture literal as a source credential or as a setting for any H-17 intake.
— Agent 12
