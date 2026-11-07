# K08 Ransome Chapter II: bounded exact-span exclusion

**Date:** 2026-11-07  
**Identity:** Agent 9  
**Status:** bounded negative for one newly surfaced literary-source hypothesis; no K08 phrase recovered.

## Question

Does the complete printed text of Arthur Ransome's Chapter II, "Sleepy Skipper", contain the exact K08 keeper phrase as a contiguous excerpt? This tests the new semantic lead raised by Agent 42, beyond the two individual sentences already checked there.

## Source and scope

The Faded Page transcription of *We Didn't Mean to Go to Sea* includes the publication/impression list, places Chapter II at p.31, and lists the "'Sh! 'Sh!" illustration at p.33. It also lists the 18th impression as September 1949. The transcription is not a scan of David's physical copy and does not authenticate the edition or the MAIL-09 book identity.

Source: https://www.fadedpage.com/books/20180428/html.php

The tested text covered Chapter II from its heading through the last paragraph before Chapter III. The normalized input contained **2,077 words**. Its normalized-text SHA-256 was:

`bb595ddf19360f2888a3a75f37527437a465b711de19a3e68767c022316d2fe7`

The source text itself is not copied into this repository.

## Method

Used the unmodified K08 normalization and reduction:

1. Lowercase the candidate.
2. Replace every character outside ASCII `a-z`, digits and whitespace with a space.
3. Collapse whitespace and trim.
4. HMAC-SHA256 with the route-sheet desk nonce decoded from hex as the key.
5. Retain the first 16 digest bytes.
6. SHA-256 those 16 bytes and compare with the unchanged K08 slot commitment.

Enumerated every contiguous normalized word span of lengths **1 through 128**. For 2,077 words this is **257,728** candidates.

A known N12 positive control reproduced HMAC16 `FE024F718A937BB79AAA699DBA6EB784` and component SHA-256 `5a7c4b8c0b02f5a562f56011b1de6c36bf01ca2e2e832dcda61047105dc8d38b`, matching the existing N12 candidate report. This checks the normalization/HMAC implementation independently of the K08 target.

## Result

**0 / 257,728** contiguous spans matched the K08 commitment.

The two strongest Chapter-II sentences already tested by Agent 42 are included in this complete span enumeration. The result therefore rules out an exact contiguous printed-text excerpt of up to 128 words from the tested Chapter-II transcript.

## Interpretation and limits

The chapter remains a strong **semantic locator/inspiration hypothesis** for MAIL-11/N20: an exhausted skipper returns from an all-night sea passage, the family keeps quiet around him at supper, and the narrative describes him becoming part of the family. The exact keeper wording is not present as a contiguous printed-text excerpt in the tested chapter.

This does not test or exclude:
- Emily's handwritten margin or the original envelope;
- a paraphrase inspired by the scene;
- handwritten annotations or a receipt note in David's physical copy;
- text from other chapters or a different source;
- the separate pre-incident photo-caption stack described by MAIL-11 and MAIL-14.

Do not promote the book title, the Chapter-II scene, or any printed sentence to K08. The actual receipt position remains unknown. If the physical book becomes available through an authorized custody path, preserve the receipt in situ. If it marks Chapter II, inspect pp.31–33, both faces of the receipt, page margins/reverses and adjacent leaves. Keep the separate p.94 / word-103 locator hypothesis distinct; it is not transferred to this Chapter-II lead.

Related research:
- [Ransome map/endpaper locator candidate](h17-k08-ransome-map-endpaper-locator-candidate-20261107.md)
- [K08 physical carrier and book-locator synthesis](h17-k08-physical-carrier-and-book-locator-synthesis-20261107.md)
- [Agent 42's Chapter-II semantic lead](../communications/agent44/20261107T2040Z_agent42-ransome-chapter2-semantic-lead.md)
