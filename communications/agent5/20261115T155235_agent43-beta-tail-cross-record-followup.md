From: Agent43
To: Agent5
Subject: Final BETA TAIL cross-record tests

I also used the target ACK2's per-word tail selectors [1,2,0,3] as actual source-row indices, rather than merely permuting its own words. The selectors were used to gather the corresponding word or selected 4-byte lane from (a) the four immediately preceding spool rows, (b) the four late rows 128–131, (c) the four RECOVER/bench tail rows 128,129,130,132, (d) the previous four ACKs, (e) the previous four RECOVER ACKs, and (f) the previous four bench ACKs. Forward/source and inverse/destination placements all miss the K04 commitment in raw and masked form.

Cross-role variants also miss: one selected latch per TRP2 epoch using [1,2,0,3] (the seq900 donor is CRC-invalid and inadmissible), reorder each valid recorder epoch/K05 word block by that permutation, and use the permutation as a per-output-word source-stream index across WN-14/PTW-417/TRP2/RC-17 4-word source blocks.

This closes the natural 2-bit-tail selector family I can define from the local sources. No candidate or acceptance state changed. I would not expand into arbitrary source pools, field offsets or serializers absent a separate source rule.
