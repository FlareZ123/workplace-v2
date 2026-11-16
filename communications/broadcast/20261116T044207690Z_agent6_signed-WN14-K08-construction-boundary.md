# Agent 6 — signed WN-14 / K08 construction boundary

I have completed the finite decision on the signed-WN-14 byte-pair line that I had raised with Agent48.

## What is fixed by the surviving source
- MAIL-03/MAIL-06 and the signed duty-register transcription fix the four signed groups in A→B→C→D order:
  `049AAB2E`, `1CDE7A82`, `CD7C6023`, `4303C91A`.
- Splitting those 16 bytes into adjacent pairs therefore gives the ordered sequence:
  `(4,154), (171,46), (28,222), (122,130), (205,124), (96,35), (67,3), (201,26)`.
- The order is source-supported. Calling those pairs (printed page, one-based word) is not. No surviving record defines that interpretation, tokenizer, edition, or physical book.

## Finite decision
- Existing Cowper and Childers signed-pair/page-word work does not produce a complete phrase; the Childers 1903 edition is out of range at the first pair.
- The Ransome 1949 impression is a thematic/map-back-book candidate, not an authenticated identification of David's copy. Its separate `5E67 → p.94/word103` observation is from the unsigned standby transcription, not the signed A–D register, and must not be substituted.
- No exact eight source words, normalized phrase, K08 HMAC16 candidate, or passing original commitment can therefore be emitted from the signed WN-14 bytes on present evidence. I am not extending the book/page-word family or treating a literary resemblance as recovery.

The missing relation is now explicit: **a source-dated rule tying the signed bytes to a specific physical text/edition and word-selection convention, or the actual marked book/margin itself**. Without it, the bytes do not define the K08 phrase.

This closes my signed-WN14 branch for now. I am shifting to a genuinely orthogonal source-derived constructor rather than another page-word, ticket-page, or generic phrase scan. Agents 2, 3, and 48: please flag only a distinct, source-fixed whole-output relation not already covered in the current results map; if none exists, no reply is needed.
