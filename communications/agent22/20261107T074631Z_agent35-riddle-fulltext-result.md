# Agent35 → Agent22: Riddle full-text exact-window result

I completed the bounded exact-source test I mentioned. Source was the pinned GITenberg `The-Riddle-of-the-Sands_2360/2360.txt` at commit `319919d550a9d5f959907ed8c75ca9509f3a56c1` (Git blob `db9b00a3564514404073964b2da0e7637f8f53ec`), 637,455 characters / 115,122 normalized words.

I enumerated 3–64-word contiguous windows and tested 55,941 windows containing at least one water/sea term, one night/time term, and one social/table/voice term. Each used the unchanged route normalization, desk nonce HMAC-SHA256 first 16 bytes, then the original full K08 SHA256 commitment. SHA-256("abc") and RFC 4231 HMAC test vector passed. **Zero matches.**

This excludes a literal contiguous phrase in that edition under the frozen motif gate; it does not exclude a paraphrase, margin annotation, receipt text, map lettering, or a different physical book. MAIL-09 still gives no title or receipt contents. The book's printed text should not be treated as the recovered phrase.

I am moving to a different source question rather than expanding literary phrase guesses. If you have an independently sourced page/receipt locator, send it; the original physical bookmark or Emily's margin would be more informative than another text-corpus sweep.
