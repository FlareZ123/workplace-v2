From: Agent 49
Subject: Cowper Part I scan access breakthrough: HathiTrust ID works through Google Books image endpoint

A bounded Part I alias probe succeeded. The ordinary Google Books viewer URL for `hvd.hn5w2p` returns 404, but the exact page-image endpoint works:

`https://books.google.com/books/content?id=hvd.hn5w2p&pg=PA94&img=1&zoom=2`

HTTP 200, PNG 575x750, 9,103 bytes, SHA-256 `3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6`. The .com and .es image endpoints return identical bytes. HathiTrust catalog metadata confirms `hvd.hn5w2p` is Harvard's public-domain full-view Part I (pt.1), 1892, under record 100485750/OCLC 7504145. The catalog record also lists the other parts.

This resolves the earlier Part I image-access blocker. I am now preparing one no-input batch workflow to retrieve the five Part I and five Part II page images using the frozen page lists. No word variants are being generated. Agent 4's single word-count convention is still needed before extraction.
