# N12 workshop-card wording: exact K08 candidate test

**Owner:** Agent 18  
**Date:** 2026-11-07  
**Status:** candidate rejected as the K08 phrase; physical card identity unresolved  
**Reproduction:** python agents/agent18/k08_n12_workshop_card_candidate_sft.py

## Question

MAIL-12 says Zoey placed a small card beside the shelf for two night-crew members' chipped blue mugs. N12 is attributed to Simon and titled “Workshop card”; its body is “The best repair is sometimes remembering who comes on after you.” Agent44 identified a possible N12/PS-0312 card-type/store-destination association. Could the exact N12 wording be the shelf-card wording or Emily's final K08 caption?

## Source-pinned test

The SFT checks the SHA-256 of the original note file, recovery-routing file and acceptance file. It applies the original K08 rule exactly: lowercase, replace non-ASCII-letter/digit/whitespace characters with spaces, collapse whitespace, trim, compute HMAC-SHA256 using the decoded desk nonce, retain the first 16 bytes, then SHA-256 those 16 bytes for the acceptance comparison.

The implementation is calibrated against the source-authentic N02 wording. Its HMAC16 is the previously reported BF889359B0303F2B2B2FD96AE841210B, confirming the nonce, normalization and byte order used here.

For the N12 body, normalized text is:

> the best repair is sometimes remembering who comes on after you

Its HMAC16 is FE024F718A937BB79AAA699DBA6EB784. The resulting component SHA-256 is 5a7c4b8c0b02f5a562f56011b1de6c36bf01ca2e2e832dcda61047105dc8d38b, which does not match the original K08 commitment 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

## Interpretation

The exact N12 workshop-card wording is **not** the accepted K08 phrase. This is a direct candidate test, not a statement that N12 and Zoey's shelf card are the same physical object. MAIL-12 does not quote the card, name its author, or say Emily saw/adopted it. N12's PS-0312 association remains a conditional sequence/job locator, not a foreign-key proof.

Keep the shelf card as a distinct antecedent source. Do not promote N12's text to K08, and do not infer the unseen shelf-card wording from N12. If an already-preserved original card or native MAIL-12 thread becomes available, authenticate the physical card and its wording separately, then require a documented path to Emily's final envelope text before treating it as K08.

**Outcome:** zero K08 words recovered; K04 unchanged. No new custodian request or phrase-generation sweep is warranted.
