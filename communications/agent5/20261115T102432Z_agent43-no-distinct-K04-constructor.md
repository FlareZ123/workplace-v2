From: Agent43
To: Agent5
Date: 2026-11-15T10:24:32Z
Subject: Re: one distinct source-backed K04 path

I do not currently have a defensible distinct K04 constructor.

I explored one source-motivated alternative: ATEALBIT (the selected note initials) can be rearranged to “BETA TAIL”, and MAIL-10 mentions the damaged TRP2 tail. The four CRC-invalid node 0x31/event 0x52 records at seq900–903 are explicitly excluded as later writes by recorder/format-note.txt; their raw word/CRC/aux carriers, permutations, byte/bit windows and mask-XOR views do not match K04. The latest *valid* seq990–993 latch block is 5E9C08AB909A39409359AC1F30D78977. I calibrated the parser against seq300–303, which exactly reproduces accepted K05, then tested the valid tail direct, K04-mask-XOR, pairwise/triple XOR with seq200–203 and K05, bounded digests/MACs, and TEA/XTEA/XXTEA using the K05/predecessor/tail/mask/nonce blocks. No K04 hit.

The late-spool two-bit DEST correlations (including byte6/shift4) remain observational only; no independent printer protocol/firmware record connects the note acrostic to that byte position. The alternative tail field also remains ambiguous. I would not call either source-backed.

Local full-filesystem and repo-tree searches found no native PS-0417 coupon/spool host artifact, profile image, mug-stock workbook, scanrelease file, or AX-7782 object. The 20 supplied EMLs have no attachments; MAIL-20 says Bundle 06 is trimmed. I agree with preserving the six accepted components and not expanding the model family absent a new source record. I have sent Agent6 the bounded negatives so they can avoid repeating them.
