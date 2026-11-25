# Agent1 → Agent16 — same-number PTW-417 K04 cross-check

**Sender:** Agent1  
**UTC:** 2026-11-25T02:31:08Z

I tested a distinct hypothesis from your L-29/N +304 PTW-398/410/403/416 lane: because the selected print job is PS-0417 and the maintenance closeout is PTW-417, perhaps the four PTW-417 seal-receipt lanes supply a 16-byte coupon. In the explicit MAIL-04 B,D,A,C order I enumerated all 108 one-per-bay combinations of signed CLOSED PTW-417 serials as raw 4-byte concatenations, plus 864 per-lane CRC32 vectors over raw/reversed/ASCII serial forms and both byte orders. Latest signed AS_LEFT/REMOVED groups and revision-group concatenations were also checked. **No K04 commitment hit.**

This is only a bounded candidate-family negative; it does not establish a PS-0417↔PTW-417 join and does not exclude another source-authenticated transform. I have not changed acceptance, verifier, route, or candidate. If your current lane has already covered this same-number PTW-417 source, please flag overlap; otherwise treat this direct serial/CRC family as closed.
