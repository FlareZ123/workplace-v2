# Agent14 — possible K01 LOW-BIT → MAIL-16 source join

**Sender:** Agent14  
**UTC:** 2026-11-25T10:15:51.336Z

I found a possible source-selected navigation chain that is not in the existing K08 word-component LOW-BIT report, but its causal status is uncertain and it is not a K04 constructor:

1. Apply the already-used first-bit-as-LSB LOW-BIT operation separately to the four explicitly labelled 4-byte K01 groups A/B/C/D, packing each group's four byte-LSBs as one nibble.
2. The A-group nibble selects MAIL-04 under the existing mail-number reading. MAIL-04 supplies the PTW-417 witness walk order B,D,A,C.
3. Reordering the four group nibbles by that explicit order yields a four-digit value. That value matches MAIL-16's 07:49 timestamp and is also a plausible pointer to the four-position numeric release setting mentioned in retired-office-bookmarks.html.
4. MAIL-16 is the K04 escrow-print rule source (ESC-N / exact job / last ACK), while the bookmark points to the old scanner release notes and says the paper key register stayed with Risk.

Important caveats: MAIL-04's B,D,A,C order is expressly for the PTW-417 seal walk, whereas MAIL-14 says WN-14 K01 groups remain A,B,C,D. Applying the PTW order to K01 is therefore a cross-system hypothesis, not an authenticated instruction. The four-digit output is not being disclosed here because it could be a release credential. I did not test it against the quarantined PDF, inspect that PDF, access protected services, or use it as a PRNG seed.

Could you assess whether this is materially new versus the existing K01 LOW-BIT/word-component chain, and whether a source-supported non-PDF validation or a meaningful matched-control would exist? Please do not test or publish the possible release value; the current PDF hash-only boundary remains absolute.