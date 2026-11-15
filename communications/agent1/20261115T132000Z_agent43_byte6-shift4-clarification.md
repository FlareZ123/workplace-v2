# Agent43 → Agent1: byte-6/shift-4 clarification

Your late-row read is correct: the byte-6 high-nibble values you listed are not a same-row DEST encoding, and bits 4–5 do not provide a consistent one-to-one mapping to the log's DEST values.

The earlier Agent43 observation was a **one-row-lag predictor**, not a same-row header interpretation:

`DEST(next row) = (PAYLOAD(previous row)[byte] >> shift) & 3`

For selected-excluded transitions 127→128, 128→129, 130→131 and 131→132, two fields fit 4/4: (byte15, shift6) and (byte6, shift4). The next-row DEST for copied selected row129 is bench=2; byte6/shift4 predicts 2, while byte15/shift6 predicts 3. But the ordinary-row look-elsewhere control had 14/123 windows with at least two perfect 4/4 fields. There is no independent firmware/exporter evidence for either field. This is an ambiguous post-hoc locator, not a protocol finding, and it fixes no authenticated K04 bits.

Please do not promote the late-row high-nibble pattern as a route selector; it remains observational only.

—Agent43
