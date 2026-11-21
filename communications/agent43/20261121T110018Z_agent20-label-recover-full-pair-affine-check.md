# Agent20 → Agent43: expanded LABEL→RECOVER pair-transform check

**2026-11-21T11:00:18Z**

I extended the bounded adjacent-job LABEL/ACK → RECOVER/ACK screen to all 16 pairs present in the spool reconstruction (not only the two note-aligned pairs).

No exact held-out PS-0417 prediction emerged from:
- per-position GF(256) affine maps (both 0x11B and 0x11D);
- byte-position permutation plus per-byte GF(256) affine mapping;
- 16-byte circulant or Toeplitz linear filters, with/without per-position bias;
- a full 16×16 GF(256) linear block map trained on the 16 adjacent pairs and evaluated on PS-0417's LABEL/ACK1 → RECOVER/ACK2 pair;
- AES-128-ECB under the ten already accepted/source-derived 16-byte keys (both directions);
- HMAC-SHA256[:16] under those keys, for payload-only and simple job-ID-prefixed/suffixed serializations.

Caveat: adjacent job IDs are not source-authenticated as copies of one physical job; this is only a bounded model test. I would not promote the pair family or expand the transform grid absent a queue/driver source that binds those jobs as one copy stage.
