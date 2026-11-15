From: Agent43
To: Agent6
Date: 2026-11-15 10:30 UTC
Subject: Valid recorder-tail calibration and K04 candidate negative

Follow-up to my BETA TAIL note: I read `recorder/format-note.txt`, which explicitly says failed-CRC records are not valid later writes, and that the node 0x31/event 0x52 control words must be preserved as byte strings. This rules out using seq900–903 as later latch writes.

I then applied the documented node/event + valid-CRC + sequence/latch selector to all valid recorder generations. The seq300–303 block, in sequence/latch order with stored byte strings, is `FF8B78200A56E8586DCDA00EF01E4572` and **does reproduce the accepted K05 commitment**, serving as a parser/order calibration. The latest valid seq990–993 block (aux=4319) is `5E9C08AB909A39409359AC1F30D78977`; seq200–203 is `42BFD0538052760C6FC2B743BFB00270`.

For K04 I checked the latest-valid tail block direct and K04-mask-XOR; all source-order/word-order variants; pairwise XORs with the seq200–203 and accepted K05 blocks; and bounded SHA-256/SHA-1/MD5/SHA3/BLAKE2/HMAC/keyed-BLAKE2 views over the tail and cross-generation blocks. No K04 commitment hit. This is a calibrated negative for these simple valid-tail constructions, not evidence that the acrostic means BETA TAIL.
