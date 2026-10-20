# H-17 incident archive recovery

**Current independently verified status: six of eight components.** Root `candidate.json` has verified K01, K02, K03, K05, K06 and K07; K04 and K08 are intentionally null pending independent acceptance. The original `resources/acceptance.json` and `resources/verify.py` are unchanged.

Read [six-slot evidence report](h17-initial-six.md) for exact bytes, evidence links, unresolved causes, and a reproducible reducer in [`work/h17_recover6.py`](../work/h17_recover6.py). Six PASS means the full combined commitment remains INCOMPLETE.

Primary open tasks: recover a checksum-valid K04 printer payload beyond the unverified ACK2 spool bytes; reconstruct K08 keeper's final remembered desk caption beyond the exported drafts. Do not claim completion until all eight original commitments and combined commitment pass.
