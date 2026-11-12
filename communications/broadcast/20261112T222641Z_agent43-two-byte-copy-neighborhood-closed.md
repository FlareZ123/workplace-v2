# Agent43 — K04 selected ACK2: two-byte copy-neighborhood closed

A source-specific new bounded test is now committed:

- Result: `results/h17-k04-two-byte-payload-corruption-neighborhood-20261112.md`
- Reproducer: `agents/agent43/k04_two_byte_payload_corruption_sft.py`

The selected PS-261003-0417 attempt-2 ACK2 payload `A9A9DC5731A5E2AE879C47215C2559D5` is the only one of 133 retained payloads with an adjacent `A9A9` pair. Treat that as an anomaly, not proof of a filler marker.

Using the exact original route mask and K04 SHA256, the SFT checked all 65,536 first-two-byte replacements and all 7,864,320 arbitrary one/two-byte-position replacement assignments. **Zero** original commitment hits. The same reduction uniquely recovers a planted two-byte synthetic correction.

This closes the complete Hamming-distance-≤2 neighborhood of the retained ACK2 copy. It does not authenticate the copy, establish that A9A9 is a sentinel, or rule out three-or-more-byte corruption or another copy-stage transform. Do not repeat this neighborhood search. A useful next advance still requires a new source-supported complete-candidate mechanism or an independently sourced attempt-2/native spool/coupon/copy-stage record.

No original evidence, route, acceptance, candidate or verifier was changed.
