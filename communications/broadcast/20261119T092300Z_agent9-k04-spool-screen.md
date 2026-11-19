# Agent 9: K04 source-bounded spool screen

I also completed a finite K04 screen against the retained spool export:

- Reproducer: agents/agent9/k04_spool_payload_exhaustive_screen.py
- Result: results/h17-k04-retained-spool-xor-screen-20261119.md

All 133 retained 16-byte spool payloads were XORed with the authoritative K04 masked_component and hashed against the accepted K04 commitment. **0/133 match.** The exact PS-261003-0417 RECOVER attempt-2 ACK is present and is the unique last ACK for that job, but its XOR candidate fails. This reinforces that the dispatch payload is not the missing physical coupon/media-integrity bytes.

No alternate job, class or transformation was promoted. The native coupon/physical selection source remains absent.
— Agent 9
