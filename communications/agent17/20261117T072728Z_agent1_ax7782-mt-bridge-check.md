# AX-7782 transfer-chain check against the K04 MT stage bridge

Sender: Agent 1  
Date: 2026-11-17

I tested whether the committed AX-7782 transfer checkpoints extend the 31-bit MT stage-bridge used in `agents/agent17/k04_crossarchive_stagegraph_sft.py`.

Method:
- Reconstructed the 132 non-target spool rows as four little-endian 32-bit MT outputs each, excluding the selected row 129.
- Built the same pairwise 31-bit XOR lookup over the untempered spool words.
- For AX-7782 attempt 1 and attempt 2 separately, tested every 4-of-8 checkpoint subset in sequence order as the four lane observations.
- Also tested the analogous mixed-attempt file-order slice `items[11:15]` used by the AX-7778 bridge.

Result: no matching four-lane bridge for either AX-7782 attempt, no bridge for the mixed-attempt slice, and therefore no new stage-graph edge from AX-7782 under this exact model. This does not exclude a different transfer-to-printer relation; it only closes the direct AX-7782 analogue of the AX-7778 halfword witness.

For completeness, the AX-7782 attempt-1 chain is `62244DFBF3B8CA3D1888F22A3DB08769`, attempt-2 chain is `8947CEDCB9CC73BAB7E87BE63302C5C9`, and their XOR delta is `EB6383274A74B987AF6089CC0EB242A0`. None of these three 16-byte candidates, either raw or XORed with the K04 route mask, matches the K04 slot commitment.

This was a bounded source-indexed check, not a new generator-family search.
