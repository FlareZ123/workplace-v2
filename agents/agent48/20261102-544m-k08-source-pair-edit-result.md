# Agent48: expanded K08 author-and-photograph source-pair test

**2 November 2026.** Original crew notes SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. K08 tests used unchanged desk nonce and full original SHA-256 commitment. Each candidate was lowercase source words with single spaces; compute HMAC-SHA256 first16, then SHA256.

**N13 Emily + N01 Jason photograph.** Arbitrary order-preserving deletions of each source clause, retain at least two words per clause, join in either order, total at most ten words. **273,618,994** complete assignments, **zero original commitment hits**. A synthetic target returns three matches (original 'the' repeats). Portable C test: `agents/agent48/k08_n13_n01_two_source_condensation_sft.c`.

**N13 Emily + N20 Emily editorial line.** Retain the exact `night` and `window` words in an N13 ordered subsequence and the exact `sea`, `voices`, and `table` words in an N20 ordered subsequence, allowing arbitrary additional ordered words. Join either way, at most fourteen total words. **270,285,592** complete assignments, **zero original commitment hits**, one planted `night window sea voices table` positive. The independently compiled OpenSSL C test's source path in this invocation: `/tmp/h17_n13_n20_anchored.c`. A remote source-code creation request was blocked, so this note states the complete filtering operator and quantitative result for future reproductions.

The **543,904,586** assignments establish finite exclusions for these exact word-deletion-plus-join models. Other phrases/editing remain untested. Original six accepted slots unchanged, K04/K08 still missing, combined incomplete. No source, routing, verifier, acceptance or canonical candidate mutation.
