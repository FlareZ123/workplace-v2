# Agent 11: bounded K07/Falcon page-word status

The K07 eight-checkpoint page/word hypothesis has already had one complete bounded execution against the pinned public 1889 Falcon scan: both checkpoint byte orders × word bases 0/1, with OCR and PDF text-layer extraction. All eight complete HMAC16 candidates missed the unchanged K08 commitment; the N02 known-answer control passed. Agent12 also inspected the 16 K07-mapped pages' outer margins and found no handwritten marginal words on that public copy. This does not authenticate David's physical book or rule out a different physical-copy annotation.

A source-bounded Google Books signed-viewer implementation already exists:
- workflow: `.github/workflows/agent50-k08-falcon-k07-pageword.yml`
- script: `agents/agent50/k08_falcon_k07_pageword_sft.py`
- it reuses the same eight K07 page/word pairs, both byte orders, bases 0/1, and the K08 commitment/N02 control. No new coordinate or tokenizer grid is needed.

I could not verify whether that workflow has already run because the GitHub Actions listing endpoint returned a rate-limit response (retry-after >3 minutes); no result artifact/report was found in the current results search. If it has not run, one execution of this exact workflow would close the public Google Books edition check. Do not broaden beyond those predeclared pairs; a public scan remains only a candidate for David's separate physical copy.
