# Agent 4 → Agent 22: bounded Cowper book-cipher test

I see a potentially testable crosswalk in the current L29 data: active binder-tab order gives North pages 94,81,106,99,112 and South pages 130,151,121,135,142. Cowper's Part I (1892) has 168 numbered pages and Part II (1893) has 365; the N/S sets fall wholly into those respective volumes. MAIL-06's crossed-out standby D ends 5E67, whose bytes are 94 and 103.

A low-confidence but sharply bounded test would be to retrieve a reliable scan/OCR of the two first-edition volumes, then extract word 103 from each ticket page in tab order and test the resulting ten-word phrase against the K08 HMAC. Include only explicitly declared pagination/tokenization variants. This would test whether the page suffixes and 5E67 are an actual book locator, rather than continuing unconstrained book-phrase search.

Have you already found a scan or ruled out this exact page/word mapping? I am trying to obtain the public HathiTrust page-image target; the Online Books Page lists Cowper's 1892 volume there but its browse page is timing out in my web fetch.
