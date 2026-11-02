# K08: cross-crew photograph/galley caption ancestor with two interior revisions

**Agent 3 | 2 November 2026 | Complete bounded source-literal mechanism test: zero original matches.**

## Question and separation from predecessor experiments

Emily's N10 says her desk wording should sound like the crew, and N20 names the sea, the end of night and voices at the table. Other crew members left original galley, mug and photograph captions in the same extract. Could the final caption have retained most of **another crew member's existing line**, with Emily making two localized revisions?

Earlier v2 [N13 two-edit](h17-k08-two-interior-edit-sieve.md) and [MAIL11 two-edit](h17-k08-mail11-two-interior-edits.md) searches use **Emily-authored** base sentences. Earlier v1 [photo+Emily splice](https://github.com/FlareZ123/workplace-v1/blob/main/results/k08-photo-splices.py) tests two source fragments joined into a fresh caption. The experiment here differs: it preserves **three ordered regions of one non-Emily caption**, with two separate substituted interior regions. It retains the source author's unedited outer flanks and middle spine and tests both orders for Emily's two replacement themes. No source states Emily actually used this editing process.

## Exact frozen candidate family

The original source is `resources/evidence/crew/noticeboard-and-desk-notes.txt`, SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. Use the original K08 desk nonce, normalization, truncated HMAC-SHA256 and unmodified acceptance SHA-256.

- **Base captions:** N01, N04, N08, N09, N11, N19, written by Jason, David or Zoey. Normalize each full caption's prose after the introductory colon. These are actual photograph, galley, mug or related crew descriptions, rather than source-attributed final Emily words.
- **First replacement:** contiguous 2–5-word spans of Emily N20 touching at least one literal anchor in `sea, night, voices, table`; **50 distinct** fragments.
- **Second replacement:** contiguous 2–5-word spans from Emily N02, N06 or N13 touching at least one anchor in `watch, room, hands, lamp, window, mugs, night, quiet`; **82 distinct** fragments.
- Select two disjoint deleted interior spans of **1–4 words each**, retaining at least two source words on both outer flanks and in the middle spine. Try both orders of the two theme families. Keep the remaining base words in original order. Use ordinary single spaces. The normalizer removes punctuation and case.
  
| Preserved base caption | Two-edit configurations | Complete candidate assignments |
| --- | ---: | ---: |
| N01 | 35 | 287,000 |
| N04 | 35 | 287,000 |
| N08 | 116 | 951,200 |
| N09 | 116 | 951,200 |
| N11 | 180 | 1,476,000 |
| N19 | 1,268 | 10,397,600 |
| **Total** | **1,750** | **14,350,000** |

Per-base assignment count is `cuts × 50 × 82 × 2`. These are attempts, not proven unique normalized messages.

## Observation and controls

The complete **14,350,000** candidate assignments yielded **zero matches** to the original K08 commitment. A separately planted synthetic two-edit N09 caption was recovered exactly once. The original N02 first-draft HMAC is independently reproduced as `BF889359B0303F2B2B2FD96AE841210B`. Original note SHA pin, nonce and acceptance are verified at runtime.

The source-pinned [single-file Python SFT](../agents/agent3/k08_crosscrew_twoedit_sft.py) produces exact per-base assignment counts and independently checks the synthetic and original controls. It makes no writes to the evidence, verifier, original commitments or canonical candidate.

## Interpretation

Under this *specific literal, two-cut crew-voice editing grammar*, the final Emily caption is absent. The negative does not exclude borrowing another crew line with different edits, using entirely new words, or a final independent inscription. It creates no newly authenticated K08 word and leaves K04 unaffected. The six known slots remain individually accepted; original combined acceptance remains incomplete.

A genuinely new path should supply an author-final wording witness or a source-selected editing operation. Growing the same unrestricted wordlist is unlikely to resolve the missing phrase.
