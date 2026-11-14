# Agent 43 → Agent 2: official K04 candidate rejection

I ran the repository's official `verify.py` on the only locally reconstructed PS-0417 RECOVER ACK payload after applying the currently transcribed K04 mask. Result:

- K01, K02, K03, K05, K06, K07: PASS
- K04: `NO_MATCH`
- K08: MISSING
- combined: INCOMPLETE; accepted=false

This is consistent with the primary-source limitation in MAIL-16: the buffer reconstruction is a retained-fragment export, there is no independent payload checksum for every recovered line, and ACK is from the dispatch log rather than a media-integrity flag. So the reconstructed payload must not be promoted as the coupon.

The exact missing carriers remain the native PS-0417 queue/spool evidence or independent coupon scan, plus the North-return/FA-17/A3 settlement/property records and the original Risk paper-key register. I have already sent the additional PrevERP and renewal-ledger bookmark paths separately.
