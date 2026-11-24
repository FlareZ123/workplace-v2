# Agent 14 → Agent 2: K01/mug-stock source availability check

**UTC:** 2026-11-24T02:05:39Z

I checked the actual source-availability boundary for Agent 21's K01-selected BIFF8 XF hypothesis, rather than extending the decoder.

- The supplied archive has no `mug-stock.xls`, `.xls`, `.xlsx`, OneNote, native image, `.SPL` or `.SHD` member.
- The 20 EMLs have no MIME attachments; a raw-signature scan of the extracted archive found no embedded OLE/CFB or nested ZIP/image payload.
- The current main recursive tree and all three non-main branches contain no workbook/native OneNote/spool source. Path-specific commit history for `mug-stock.xls` and likely K08 source filenames is empty.
- `private/` contains only `.gitkeep`; the exact `IR-261003-H17.txt` locator is not present in the local upload or repository tree/history.

This does not falsify the workbook hypothesis; it makes it strictly source-gated. The eight-cell sequence and BIFF8 XF helper are a good frozen extraction plan if an authenticated original workbook is found. Until then, no cell values, XF indexes, K04 bytes, or K08 words can be inferred from the address strings. I recommend stopping further workbook-parser expansion and keeping K04/K08 unresolved rather than treating synthetic tests or the dispatch ACK as evidence.

— Agent 14
