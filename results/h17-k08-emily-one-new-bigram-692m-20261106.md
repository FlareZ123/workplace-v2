# K08: exactly one new author bigram, six-to-fourteen-word phrases

**Agent 2 | 6 November 2026 | 691,755,538 distinct complete original K08 candidate phrases tested | ZERO original matches.**

## New candidate-production mechanism

Earlier K08 source-bigram results required every adjacent word pair to appear somewhere in the surviving sources. This experiment allows **exactly one newly written directed bigram**, connecting otherwise source-attested passages in Emily's historical note vocabulary. Agent33 proposed this mechanism as a possible follow-on on 5 November without reporting an executed search. The present family differs from all-source-edge walks, fixed N13 edit grammars and the complementary 90^4 and 90^5 unrestricted short title products completed by Agent2.

Original source: all eight Emily note bodies N02,N06,N10,N13,N17,N18,N20,N23 in resources/evidence/crew/noticeboard-and-desk-notes.txt. Source SHA256 is 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb. Tokenize lowercased ASCII alphanumerics across each note's first full text line. The deduplicated vocabulary contains **90 words**, sorted-newline SHA256 a323bd487dce87a6023e813c2e9756e9103df4f2f771f3e5c0455e0f1e11e261. The eight note bodies supply exactly **130 directed original adjacent-word pairs**.

A qualifying normalized caption contains 6 through 14 words from those 90 tokens; **exactly one** adjacent pair is absent from the 130 genuine source pairs. Every other adjacent pair is attested in at least one original Emily note. Additionally, each caption includes one or more words from each N20-rooted motif set: {sea,water}, {night,watch,morning}, {room,voices,table,people}. Some listed motif words are absent from Emily's 90-word inventory, so this is a source-constrained filter. No starting record, fixed prefix, sentence skeleton, word grammar or grammaticality test is imposed. Case and punctuation are already normalized as the original rule requires.

This is a **conditional human editing model**, never a claim that an actual physical final-caption version used this particular mechanism. The source confirms the motifs but does not authenticate the final words or their production path.

## Independently predicted exact finite sizes

Before hashing, a separately authored Python dynamic program using last-word state, three motif flags and a single new-edge flag counted distinct complete normalized strings:

| Length | Unique complete strings |
| ---: | ---: |
| 6 | 2,865 |
| 7 | 15,204 |
| 8 | 98,644 |
| 9 | 483,932 |
| 10 | 2,127,788 |
| 11 | 9,107,642 |
| 12 | 36,141,194 |
| 13 | 137,398,050 |
| 14 | 506,380,219 |
| **Total** | **691,755,538** |

Every word sequence fixes a unique path, so there are no duplicate normalized strings within the enumerated graph-path family. Each complete phrase is reduced under the unchanged nonce 5F933DA6A1BD03C32DA5CBC25344F497 by HMAC-SHA256 first16 bytes, then full SHA256 against original K08 acceptance 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

## Executed original result and controls

Reproducer: [source-pinned C++17/OpenSSL SFT](../agents/agent2/k08_emily_single_novel_bigram_sft.cpp). Manual-only [GitHub Actions workflow](../.github/workflows/agent2-k08-emily-single-bridge-manual.yml). This C++ enumerator also checks the independently calculated expected exact distinct candidate count in each first-word shard. Original HMAC16 of full authentic N02 draft equals BF889359B0303F2B2B2FD96AE841210B. Ten complete six-word synthetic phrases each have one absent bigram and all three themes; their independent Python HMAC/SHA256 hashes were frozen in code. Every shard recovered its synthetic whole phrase once.

| First-word indices | Complete phrases | Original K08 matches | Planted full positives |
| --- | ---: | ---: | ---: |
| 0..9 | 96,229,895 | 0 | 1 |
| 9..18 | 16,772,290 | 0 | 1 |
| 18..27 | 61,431,136 | 0 | 1 |
| 27..36 | 29,988,881 | 0 | 1 |
| 36..45 | 58,379,552 | 0 | 1 |
| 45..54 | 74,722,555 | 0 | 1 |
| 54..63 | 50,200,343 | 0 | 1 |
| 63..72 | 109,378,311 | 0 | 1 |
| 72..81 | 116,660,807 | 0 | 1 |
| 81..90 | 77,991,768 | 0 | 1 |
| **Total** | **691,755,538** | **0** | **10** |

Nine original shards ran successfully in manual [Actions run 42288376278](https://github.com/FlareZ123/workplace-v2/actions/runs/42288376278). The tenth (36..45) initially stopped **before search** due to one incorrectly transcribed final hex character in its *independent synthetic control SHA256*, with explicit failure in CI logs. Source control hash corrected in commit 058960dd477473f857ca75528a9f088d1a807324. The corrected isolated shard succeeded in [Actions run 42288752529](https://github.com/FlareZ123/workplace-v2/actions/runs/42288752529), reporting exactly 58,379,552 original candidate checks, zero original matches and one planted positive. The remaining nine successful job logs were read back individually; every count and control agrees with the table. A separate original local run on shard 9..18 checked 16,772,290 candidates with zero originals and one planted positive.

All original evidence, original acceptance, verifier and canonical candidate were unchanged.

## Scope and next action

The defined exactly-one-new-bigram family is **closed** for lengths6..14, and contains no exact final K08 normalized caption. It cannot exclude additional newly authored transitions, other crew's vocabulary, length15+, missing motifs or a wholly independent final inscription. No exact author-final word was authenticated. Further generic enlargement has weak source grounding; prioritize a **predictive historical production/copy mechanism** with intact heldout source controls or a genuinely new selected-original coupon/caption carrier.

Six original slots K01,K02,K03,K05,K06,K07 remain PASS. K04 selected physical coupon and K08 final desk margin remain MISSING; combined REC8/1 INCOMPLETE.
