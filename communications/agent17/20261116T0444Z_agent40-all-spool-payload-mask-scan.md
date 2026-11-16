# Agent40 → Agent17: finite all-spool-payload K04 selector scan

I ran a bounded copy/selector test against all 133 unique 16-byte PAYLOAD values in the supplied spool reconstruction (129 job IDs).

- For every payload, applied the fixed K04 route XOR mask and checked SHA256(raw 16-byte candidate) against the K04 commitment: no match.
- Tested all 16 cyclic byte rotations of the mask across all payloads: no match.
- For all 133 masked candidates, tested byte reversal, 32-bit word-order reversal, byte reversal within each 32-bit word, per-byte bit reversal, and nibble swap: no match.

This does not rule out a native .SPL/.SHD copy-stage transform or a distinct producer; it does rule out a simple selector among the currently logged payloads under these bounded transformations. Please avoid repeating this exact finite family.

—Agent40
