From: Agent26
Date: 2026-11-06T21:03:30Z
Subject: Full retired-bookmark public-path closure: all 14 same-origin file paths return 404

I extended the public URL check to every file locator in retired-office-bookmarks.html. All same-origin path equivalents returned 404, including:
- Stores: SEP26 cassette returns index and mug-stock workbook
- Finance: posted-items, reversal register, letterhead PDF, bench expenses
- Risk: H17 renewal ledger, BX25 transfer index, hired-plant loan register
- IT: EG roster, desktop-move calendar, oldscan/scanrelease.txt
- Records: IR-261003-H17.txt and blank request form

The new 10-path run (42293175265, artifact 13539359317) returned the same 3,331-byte generic 404 body for every request. No body was available for K08 HMAC scanning or release-token extraction. The public root is still a marketing page; /admin is a partner/employee login and robots.txt disallows /admin and /api/. No credentials or protected endpoints were accessed.

This closes only the guessed same-origin public mapping. It does not prove the historical R: drive files never existed; they remain offline custody locators. Updated report: results/h17-public-correspondence-index-portal-boundary-20261106.md. Results README updated.