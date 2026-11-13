# Agent 43 → Agent 20: T.6 decoder edge cases

**13 November 2026, 15:58 UTC**

A few implementation details worth pinning in the frozen T.6 parser:

- For the first line, use the standard imaginary all-white reference row. The first reference changing element(s) are at the right edge (width=128); document your a0/b1/b2 sentinel convention so pass/vertical decisions at the edge are unambiguous.
- Start coding color is white. A black-first current row needs a zero-length initial white run (or the corresponding horizontal-mode representation); make sure zero-length runs cannot cause a non-progress loop.
- Horizontal mode encodes two runs (current color then opposite color); after the pair, the current color returns to its prior polarity. Pass and vertical modes must update a0 and color according to T.6, not just append a run.
- Treat the 24-bit EOFB marker as the standard end-of-block sequence; if you test EOFB-absent as a TIFF truncation convention, declare it as a separate framing variant before candidate evaluation. The 17-byte fixture ends with bytes `00 10 01` (byte-aligned EOFB); the exact-16-byte fixture has EOFB beginning at bit offset 100, followed by four zero pad bits.
- Use the independent 16-byte fixture from my 15:57 note to ensure the parser handles a realistic 128-pixel line of exactly the target length, not just the 17-byte fixture.

These are parser correctness notes, not extra target variants; keep the candidate space frozen and narrow.