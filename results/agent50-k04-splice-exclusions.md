# K04 recovered printer-fragment splice checks

Agent 50 tested 265,335 two-source contiguous splices across 133 spool payloads, allowing every cut position from byte 1 through 15. No candidate passed the unchanged K04 SHA-256 commitment after XOR with the supplied mask. Also tested 7,057,911 three-source splices using the four-byte boundaries (4,8), (4,12), (8,12); none passed. Original last-ACK payload is already known to be rejected. This is a bounded corruption-hypothesis test, not evidence that larger corruption is impossible.
