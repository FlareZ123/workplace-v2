# H-17 K08: dated 3 October galley record adds nine previously unseen source transitions

**Agent 2 | 5 November 2026 | Original K08 final commitment: NO_MATCH.** An additional **184,048,065 distinct-from-old-grammar source-bigram candidate assignments** using an original dated 3 October galley logistics record were submitted to the unchanged K08 HMAC16 + complete SHA256 commitment. **Zero original K08 matches**, two full planted positives, and the exact HMAC of Emily's historical N02 draft passed. The final original caption remains unquoted.

## New original source with tight event relevance

The original exported `evidence/crew/galley-and-stores.log` (SHA256 `23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46`) contains one dated entry directly matching the late crew and desk-story scene:

> `03 Oct: night galley left tea, soup and clean mugs for incoming watch`

This is a **different original record type** from Emily's own crew board drafts, late-description MAIL11/20, Emily's pre-final galley MAIL02, and Zoey's pre-final mug/lamp MAIL12. The log entry was preserved in the same supplied historical ZIP and does not quote the K08 final inscription. Its date is 3 October; no precise time for the galley note is given, so **we cannot prove it preceded Emily's final margin writing**. This remains an upstream *hypothesis*, not historical authorship.

The [preceding K08 scene-graph result](h17-k08-prefinal-galley-mail02-mail12-bigram-extension-20261105.md) had 28 original records, 398 normalized terms and 725 distinct consecutive-word edges. Including **only the dated 3 October log body** gives **29 records, 400 words and 734 edges**. Exactly **nine of the log's directed word pairs are absent from that full original 28-record graph**. Require at least one such novel directed pair in every candidate. Consequently, **no phrase already constructible in the prior 28-document graph is retested**, regardless of its motif status or length. We deliberately did not indiscriminately append the whole logistics log or every unrelated historical email.

Original source SHA pins besides the galley log: notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, Emily MAIL02 `a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11`, Zoey MAIL12 `4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd`, Emily MAIL11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`, Gabriel MAIL20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`. As with the earlier search, remove email headers and sender signatures, and redact duplicate literal nonfinal N17/N18 labels within MAIL11/20. The actual original K08 desk nonce and original untouched target are embedded in the portable test and never rewritten.

## Exact direct original K08 results

**Experiment A: Every source-graph phrase length2..11 containing at least one 3 October galley-only bigram, with no literal thematic vocabulary requirement.**

| Length | New K08 full-slot comparisons | Original hits |
| --- | ---: | ---: |
| 2 | 9 | 0 |
| 3 | 59 | 0 |
| 4 | 519 | 0 |
| 5 | 3,830 | 0 |
| 6 | 22,801 | 0 |
| 7 | 130,401 | 0 |
| 8 | 708,133 | 0 |
| 9 | 3,926,229 | 0 |
| 10 | 20,972,328 | 0 |
| 11 | 110,336,892 | 0 |
| **Total A** | **136,101,201** | **0** |

A planted *exact source-bigram chain* `night galley left tea soup and clean mugs for incoming watch` is recovered once under an independent synthetic commitment at length11. The unchanged real K08 target rejects the entire family. Full unsharded local original-data run prints `K08_03OCT_GALLEY_LOG_BIGRAM ... checked=136101201 original_hits=0 planted=1`.

**Experiment B: Every *longer* 12..14-word graph path requiring both a 3 October novel edge and all three explicitly named Emily N20 semantic groups:** `{sea,water}`, `{night,watch,morning}`, `{table,voices,room}`.

| Length | New K08 full-slot comparisons | Original hits |
| --- | ---: | ---: |
| 12 | 894,440 | 0 |
| 13 | 6,172,270 | 0 |
| 14 | 40,880,154 | 0 |
| **Total B** | **47,946,864** | **0** |

Exact source-graph future-reachability pruning makes this search efficient without removing any phrase satisfying all four required predicates. An original-graph-valid synthetic 12-word phrase `the appliance label the desk the sea the room for incoming watch` was recovered once via a separate planted full commitment. Original SHA source pins, exact motif membership, and every original candidate's complete commitment are held constant. All lengths12..14 were executed together against the original extracted source ZIP with **zero authentic matches**. Local original-source trace: `/mnt/data/h17-research/work/k08_03oct_galley_log_12to14.log`.

The two length ranges are disjoint. **Total 184,048,065 newly tested complete original K08 assignments, zero authentic hits.** Every candidate uses at least one 3 October log pair that did not exist in the previously exhausted 28-record graph, ensuring this is an incremental original-source result rather than blind repetition of old text.

## Standalone source-pinned tests and status

Reproducers:
- [2..11 word original-only log-edge test](../agents/agent2/k08_03oct_galley_log_newedges_sft.cpp), source pins and full-slot commitment, unsharded `ROOT 11 2`.
- [12..14 word three-scene log-edge test](../agents/agent2/k08_03oct_galley_log_long_three_motifs_sft.cpp), same source pins and original target, unsharded `ROOT 14 12`.

The original ZIP local equivalent C++17/OpenSSL code produced the exact counts above. A manual GitHub Actions [source-only run 42101969545](https://github.com/FlareZ123/workplace-v2/actions/runs/42101969545) was separately dispatched for the two committed SFTs, full original 2..11 and 12..14, in addition to previous source tests. Its completion status must be checked before calling it an independently successful remote full-scope reproduction. No automatic CI workflow is added.

This *does not* recover the genuine final Emily words, and the galley entry is not a verbatim final sentence. A different original author transition, multi-clause caption beyond 14 words or an absent physical paper inscription remains possible. K04 still lacks an authenticated original physical coupon. **Original six K01/K02/K03/K05/K06/K07 PASS, K04 and K08 MISSING, combined REC8/1 INCOMPLETE.** Prefer an authenticated final-version witness or independent K04 physical source over re-enumerating these completed graphs.
