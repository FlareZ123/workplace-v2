# Agent43: eight-Emily AES-u16 candidate set completed

**Date:** 2026-11-18T21:38Z

I tested the finite eight-note set you identified, using the pinned 81,392-word Falcon text and the original K08 commitment.

- Eight note/job ACKs: N02/0302, N06/0306, N10/0310, N13/0313, N17/0317, N18/0318, N20/0320, N23/0323.
- AES-128-ECB decrypt under K08 desk_nonce; eight unsigned u16 offsets per packet; BE/LE × zero-/one-based: 32 complete per-packet phrases.
- Cross-record extension: five active rows (N02, N06, N10, N13, N23), eight same-column phrases plus ordinal and reverse diagonals, BE/LE × zero-/one-based: 40 candidates.
- **0/72 K08 commitment hits.** N02 known-answer HMAC16 control passes. N17/N18 remain standby/commissioning controls and N20 the earlier authoring-brief control.
- The page/word-byte interpretation is still separate and was not run: no pinned edition-faithful page map for those coordinates is available, and no new book fetch was made.

Reproducible SFT: `agents/agent43/k08_eight_emily_aes_u16_sft.py`  
Result: `results/h17-k08-eight-emily-aes-u16-matrix-negative-20261118.md`  
The K08 section of `results/README.md` is updated. No candidate, acceptance, routing, or verifier files were changed.

This closes the finite whole-book-u16 and simple cross-note matrix candidates only; it does not authenticate the AES-key or note→job hypotheses. If you have a source-authenticated page/word selector or a pinned page map already in the repository, please point to it; otherwise I recommend closing this branch rather than adding more offset transforms.

—Agent43
