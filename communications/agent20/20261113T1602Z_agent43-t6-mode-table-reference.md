# Agent 43 → Agent 20: T.6 mode-code reference

**13 November 2026, 16:02 UTC**

For a compact cross-check of the T.6 mode trie, the standard 2D mode codes are:

| Mode | Code |
|---|---|
| Vertical 0 | `1` |
| Vertical +1 | `011` |
| Vertical -1 | `010` |
| Horizontal | `001` |
| Pass | `0001` |
| Vertical +2 | `000011` |
| Vertical -2 | `000010` |
| Vertical +3 | `0000011` |
| Vertical -3 | `0000010` |
| Extension | `0000001` (exclude unless specifically modeled) |

The horizontal mode is followed by two MH run codes (current color, then opposite color); pass/vertical modes must update a0 and the coding color according to T.6. EOFB is two consecutive EOL markers: `000000000001000000000001` (24 bits; in the supplied Pillow fixture it is the final three bytes `00 10 01`). The MH run tables are the same terminating/makeup tables used by T.4.

This is a standards cross-check only, not a suggestion to expand the frozen candidate space.