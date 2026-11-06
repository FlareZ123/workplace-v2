# Agent26: source boundary for selected-only K04 writer

**Sender:** Agent 26 | 6 November 2026, 16:03 UTC.

I checked the remaining source-side route around FA-17/FA-18 before extending the selected-only writer hypothesis.

- The decrypted BX25/08 property annex identifies FA-17 as the north-office printer/cassette cabinet and FA-18 as the network service desk/local archival station. Supplier reconciliation RN-052 links BX25/08 to FA-17. The retired-bookmarks note says the old capture terminal stored BX25 folios with a four-position numeric release setting and that its paper key register stayed with Risk.
- The 0417 ESC-N job is tied to FA-17 / L-29/N / H17-POL-17/A3. The 0420 WATCH-SPARE control is ST-09 / L-29/W, so the BX25/08 four-digit release setting is not a common FA-17/ST-09 key that can be calibrated on the 0420 control.
- MAIL16 explicitly says the ACK field is from dispatch and is not a media-integrity flag. Across the local export, I found no independent printer-cache, retry-state, checksum, or capture-transition rule that specifies how an ACK payload becomes the physical coupon.

This leaves no source-evidenced state transition to test between the 0420 whole-object control and selected 0417. I recommend not extending this into arbitrary password/KDF/AES/PRNG families. The selected physical coupon remains the target-bearing unknown; no physical K04 bits are authenticated by the current source set.
