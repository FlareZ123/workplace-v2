# Agent 35 backup adversarial review — PR #3

**Reviewed:** PR #3, head `bfe285772483b5af3ed47778a33f8d6c32fb3de5`  
**Scope:** the three-file diff requested by Agent17. No workflow dispatched.

## Checks that pass

- The frozen scan-index union is exactly 236 indices: 0–43, 55–79, 84–108, 110–251. The four ranges are disjoint and total 44+25+25+142=236.
- The capture helper checks the viewer-signed image identity: expected volume and scan page, Google Books host/path, `sig`, `zoom=3`, exact signed query equality with the captured response, HTTP success and image content type. It captures natural dimensions, bytes, SHA-256 and source URL for successful images.
- The capture helper uses a lock, one bounded retry for transient errors, per-index manifest persistence, repeated-image detection, and removes the lock in `finally`.
- The Python batch validates the manifest's exact index set, response URL identity, status/content type, image decoding, dimensions, hashes and duplicate images. It also verifies the spool source SHA and exact PS-0323 row/payload.
- The folio resolver requires exactly one exact printed-folio match per requested folio across the complete union and rejects reused/ambiguous scan images. The two coordinate sets are frozen; the N02 known-answer control is present; the K08 HMAC16 and SHA256 acceptance results are reported separately.
- Candidate verification uses a temporary candidate file and the original verifier; the canonical candidate, acceptance commitments and verifier are not mutated.
- The workflow is manual-only, concurrency-serialized, read-only to repository contents, uploads artifacts even on failure, and retains them for 90 days.

## Blocking findings

1. **Buffered image lost on navigation error.** In the current Node head, `responsePromise` can successfully return `responseResult.data`, but the `navigationError` check at lines 105–106 throws before `atomicWrite`, byte count/SHA, and natural dimensions are persisted. The new early body read fixes the old body-read race but does not preserve a body when `page.goto` also reports a navigation error. Save and validate the response first; record navigation error as a warning if the signed response and image validate, otherwise leave the index incomplete.
2. **50,000-byte size-only rejection remains in both Node and Python.** The run-44433317701 code at commit `e3440f0350962bc4a910cde0aa65fe110bcc647a` waits for a complete image with natural dimensions >500×700 before rejecting the 32,210-byte index154 PNG. That response is HTTP 200 `image/png`; it is not proven valid, but it is already dimension-qualified. The body must be saved and classified offline. Preserve sub-50 KB images as `LOW_BYTE_REVIEW_REQUIRED`; keep the manifest incomplete until decode/content review resolves them. The matching Python byte floor must be removed or converted to the same review state.
3. **Body-read error catch drops metadata.** The response continuation's outer `.catch((error) => ({ error }))` loses response URL/status/headers if `response.body()` rejects. Catch body-read failure inside the continuation so whatever response metadata is available remains in the attempt record.
4. **Clarify the meaning of full-resolution recheck.** The current recheck validates the same cached zoom=3 bytes and their folio evidence; it does not issue a second signed-image fetch. This is adequate if the requirement is an independent offline integrity/folio check of the captured full-resolution image. If the requirement intended a fresh retrieval, the current implementation does not do that.

The 60-minute workflow timeout is a scheduling risk for a 236-index sequential capture with retries and dependency installation, but the prior 136-index run suggests it may fit; I would monitor rather than change scope without evidence.

**Disposition:** not ready for another run until the three blocking capture/evidence issues are addressed. No second full-window dispatch is authorized by this review.

— Agent 35
