# K08: source-pinned Falcon AES pageword pilot and complete literal-span closure

**Agent 43 | 18 November 2026 | 0/16 AES-derived complete K08 candidates and 0/5,044,289 literal caption candidates matched.** The original REC8 status remains six individual PASS, K04/K08 missing, combined INCOMPLETE. Original `resources/`, canonical candidate, commitments and verifier unchanged.

## Complete source-dependent AES constructor

The [18 November decision map](README.md) identified one bounded unexecuted possibility: the original printer `PS-261003-0323` ACK/RECOVER packet (or adjacent `PS-261003-0320` control) might encode the final keeper's eight words as unsigned 16-bit absolute positions in the 1889 *Falcon on the Baltic* book, after a one-block AES-128 transformation keyed by the source-preserved K08 desk nonce. The proposed `N23→PS-0323` link is **only an ordinal conjecture**; neither the original note nor the printer log independently authenticates it. No book has been shown to be the source of Emily's final line.

The read-only runnable test [Agent43's single-file implementation](../agents/agent43/k08_ps0323_falcon_aes_offsets_sft.py) loads the independent source-pinned [Agent3 original-book parser](../agents/agent3/k08_ps0323_falcon_word_offsets.py), checks:
- original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`;
- raw Falcon HTML SHA256 `2741b1054d1369a7dcfc51b32da1f4b4931c5ca8a10c9b200cee548db496176e`;
- **81,392** normalized book words, word stream SHA256 `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`;
- official K08 nonce `5F933DA6A1BD03C32DA5CBC25344F497` and slot target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`;
- independently known original Emily N02 HMAC16 `BF889359B0303F2B2B2FD96AE841210B`, NIST AES-128-ECB test vector and test-pipeline synthetic hash positives.

For each preserved job, AES-128-ECB encrypt **and** decrypt its actual intact 16-byte packet with the 16-byte nonce. Interpret each resulting block as eight unsigned u16 word indices, both byte orders, 0-based/1-based indices. Construct full normalized eight-word phrase, compute original HMAC-SHA256(first16) then SHA256. The complete fixed grid is 2 jobs × 2 AES directions × 2 endian views × 2 index bases = **16** full commitment checks.

**[Actual completed GitHub Actions run 44338133855](https://github.com/FlareZ123/workplace-v2/actions/runs/44338133855)**, commit `82fd42a3580fab6d6ea684edd03a02623131cb5a`, finished success on 18 November 15:39:36Z. Log prints `complete_candidates=16, target_hits=0, status=NO_MATCH`. All four book/route/acceptance known-answer controls passed. None of the 16 generated phrases was the correct final caption under the exact original reducer. All 16 complete generated phrases, components and digests are preserved in the run artifact.

## Independent 81,392-word literal book-span closure

Having obtained the **exact pinned** normalized word stream from the same successful run, a new read-only local whole-object test enumerated all complete contiguous book phrases of **3 through 64 words**, starting at all 81,392 normalized positions, testing the original unchanged K08 HMAC(first16) and full 32-byte SHA256. Across **5,044,289** exact in-range candidate spans, **0** original commitment hits. The independent N02 known-answer HMAC16 passes before the scan, and the joined source stream is checked against `36997e8c...`. Full actual execution of a standard-library Python `hmac.digest`/SHA256 loop took 15.127 seconds locally. This is a precise original-data negative for **literal contiguous quotes in that version of the public book**. It does not rule out a different physical edition, selected isolated word positions, edited quotations, a different book, or Emily's actual unique authored words.

## Reusable, independently hashed corpus and next test

[Artifact 14441409429](https://github.com/FlareZ123/workplace-v2/actions/runs/44338133855/artifacts/14441409429) stores **`falcon-normalized-wordstream.txt`** (429,198 B, including one trailing newline) and `aes-word-offset-report.json` (8,497 B). The 7-day retention is explicit: artifact expires **25 November 2026 15:39:32 UTC**. The normalized words are independently pinned to the 81,392-word text hash above; do not hash the trailing newline as part of that stream. This cache lets other agents execute genuine, fixed indexed constructors offline without asking the public host again. It should not be represented as an authentic scan of David's physical book or as a copy of Emily's final envelope.

**Decision:** The AES-u16 book-offset and literal book-quotation constructors fail the exact original commitment, while the unavailable indexed book corpus has now been materialized with reproducible hashes. Any subsequent attack should use an independently justified whole-phrase selector or source correspondence. Blind per-byte offsets and unanchored book edits have no privileged claim. No K04 bits or final Emily K08 words were recovered.


## Durable corpus checkpoint (15:50 UTC)

The source cache is now **committed to the shared repository** as [`work/h17_falcon_1889_normalized_words.txt`](../work/h17_falcon_1889_normalized_words.txt), an exact 429,198-byte plaintext file (one trailing newline). Remote Git blob `782d4687c98cdc0012e56447fcc4dfa77728603c` was read back and the manual [archival Actions run 44339997429](https://github.com/FlareZ123/workplace-v2/actions/runs/44339997429) completed all steps successfully. The same run asserted the original 81,392-word normalization SHA256 before atomic authenticated GitHub Contents API creation. This removes the 25-November artifact-expiry dependency for future reproducible K08 indexed-book tests. It still does not authenticate this public transcription as the physical original.
