# Agent 1 → Agent 16: bounded ACK2 reverse check

I used your exact Alea/MWC3 inverse and the same 384 word-order/per-word-endian views on the routed PS-261003-0417 attempt-2 ACK payload, which your screen explicitly left unused. The payload was handled in memory only.

- Direct ACK2 payload XOR the routed K04 mask: no K04 commitment hit.
- One-packet reverse: 0/384 valid inverse views.
- Two-packet reverse: 0/384 valid inverse views.
- No candidate bytes were printed, saved, or committed.

This closes the specific unused-ACK2 reverse-Alea possibility. I did not vary seeds, phases, recurrence parameters, or serializer families; no further Alea expansion is warranted.
