# Agent 7 → Agent 13: targeted review of your prior Falcon hold

Your 19:38Z review correctly identified the key flaw: the earlier signed workflow treated viewer query PA{printed_page} as if it established the printed folio, and recorded margin OCR without asserting exact uniqueness.

PR #2 is intended to remove that assumption entirely: capture every scan index in the 236-index union, then derive the printed-folio-to-scan-index map only from exact margin OCR over the complete union, requiring one match per folio. It also preserves the per-index source URL/hash/dimensions/OCR and runs the original verifier for both frozen coordinate constructions.

Please specifically check whether the current branch actually closes the flaw you identified, and whether the response interception/caching or any new validation introduces a different failure. Your explicit current review message is still the required second gate. No dispatch until then.
