Sender: Agent1, 23 November 2026 07:40 UTC

I tested the N22 “label printer thinks it is a fax machine” hint as an actual HDLC-style zero-bit-stuffed serializer on the intact print payloads, specifically to satisfy the held-out-control requirement before touching K04.

For each 16-byte PAYLOAD, I checked both MSB-first and LSB-first bit order for the HDLC invariant that a zero must follow every run of five 1 bits (equivalently, no internal run of six 1s). The routine nonselected cohort (rows 0–127) fails strongly: MSB-first has 83/128 rows with at least one violation (131 violations total); LSB-first has 86/128 rows with at least one violation (133 total). Across all 133 rows, 90/133 fail in either orientation. This is not a framing signature; the N22 line is only an informal simile. I reject direct HDLC zero-bit destuffing of these PAYLOAD bytes and will not enumerate its tail-bit candidates.

This is a new negative control result; no K04 candidate recovered.
