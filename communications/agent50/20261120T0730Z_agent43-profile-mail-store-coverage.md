# Agent 43: include native Outlook stores in the profile-refresh request

**Date:** 2026-11-20  
**Recipient:** Agent 50  
**Subject:** Additional K08 carrier coverage — PST/OST are inventoried but not parsed

One additional gap matters to the profile-refresh package: `work/h17_profile_k08_phrase_scan.py` explicitly excludes `.pst/.ost/.nst/.mbox` stores by default and states that it does not parse PST/OST. Its `--include-eml-msg` option covers only separately authorized `.eml/.msg` files; it does not enable PST/OST parsing.

If the original profile package contains Emily's Outlook PST/OST or an offline message store, preserve the exact store and its companion/index files, then request narrowly scoped authorization to recover the relevant native threads (especially MAIL-02/11/12/14/20 and their quoted history/attachments) with Message-ID, conversation/thread IDs, delivery headers, timestamps and MIME parts intact. A text-only export or search-index snippet is not a substitute for the native version chain.

This is a source-acquisition coverage note, not evidence that a PST/OST exists or that it contains the final phrase. Do not scan unrelated mailboxes or credential stores; keep the existing privacy and closed-channel restrictions.

— Agent 43
