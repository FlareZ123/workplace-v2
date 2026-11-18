# K08: source-pinned 1889 *Falcon on the Baltic* whole-text absolute WN-14 offsets

**Agent 20 | 18 November 2026 | zero K08 acceptance hits, four actual complete candidates.** This is a new source-domain test, distinct from Agent24's 1903 *Riddle of the Sands* absolute-coordinate test. It neither proves David owned this title nor argues that other map-back books fail.

## Source and fixed operation

MAIL09 mentions David's book with a rear map and a tea-receipt bookmark. Knight's 1889 first-edition *The "Falcon" on the Baltic* has a rear folding map: [contemporary edition bibliographic description](https://www.abebooks.fr/Falcon-Baltic-Coasting-Voyage-Hammersmith-Copenhagen/32346424434/bd). A public [full-book HTML transcription](https://soul-trade.com/sailing/falcon/falcon_frames.htm) includes the original **2 October 1888 author note** and all fifteen chapters. Whether it is the historical *physical* copy is unknown.

With accepted WN-14 signed K01 `049AAB2E1CDE7A82CD7C60234303C91A`, interpret each consecutive byte pair as an unsigned 16-bit **absolute normalized book-word position**, in the eight original pair orders. Test both endian orders and 0/1 indexing conventions, totaling four whole eight-word phrases. The script pins the transcription **before** testing the original K08 acceptance. It uses the published original K08 desk nonce `5F933DA6A1BD03C32DA5CBC25344F497`, first 16 bytes of HMAC-SHA256 on normalized phrase, then SHA256 of the 16-byte component against unchanged target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

The fixed transcription boundaries are prose beginning “IN the summer of '86” through the author's 2 October 1888 closing date, inclusive, with heading and note words retained. Normalization splits on non-ASCII-alphanumeric characters, lowercases, and retains digits.

## Independent source acquisition

[Source-only workflow run 44248700400](https://github.com/FlareZ123/workplace-v2/actions/runs/44248700400), finished **success** before enabling acceptance mode:

- HTTP response 1,308,829 raw bytes; SHA256 `2741b1054d1369a7dcfc51b32da1f4b4931c5ca8a10c9b200cee548db496176e`.
- Exactly **81,392** normalized body words; joined-word SHA256 `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`.
- Source starts “in the summer of 86 i was without” and ends “the author october 2nd 1888”; Chapter XV and Kronborg markers verified.

The pinned raw and token stream digests were committed **before** dispatching [acceptance workflow run 44248824834](https://github.com/FlareZ123/workplace-v2/actions/runs/44248824834), which completed successfully. The independent known-answer HMAC fixture for Emily's N02 draft returned `BF889359B0303F2B2B2FD96AE841210B`.

## Four complete original commitment comparisons

| Byte order / coordinate base | Actual assembled phrase | 16-byte component candidate | Accepted? |
| --- | --- | --- | --- |
| big / 0 | `could a south to fed wet seemingly boys` | `AAE795E1B998D9482EE817E169CA633F` | **NO** |
| big / 1 | `heart but the order sounds constantly the the` | `084ECD294CB2DEE79A628A701CD6906D` | **NO** |
| little / 0 | `should black province had reached tumbled been lively` | `E79871227E670DDAB31D3CDFA0A0E790` | **NO** |
| little / 1 | `we large my he and had had peculiarly` | `7C0789B6649400C7017D5A049084B74B` | **NO** |

All four phrases are semantically incongruent with Emily's documented final-caption scene; their independently computed hashes also fail the unchanged K08 target.

**Reproducer:** [Python standard-library one-file SFT](../agents/agent20/k08_falcon_1889_absolute_words_sft.py) and [reused Agent20 source-holdout workflow](../.github/workflows/agent20-k04-class-oneword-manual.yml). The source acquisition (success) and final checking (success) jobs both fetched the same pinned original bytes. No original evidence, candidate.json, immutable verifier or commitment changed.

## Interpretation and next use

This closes exactly the four source-pinned **whole-book absolute word-offset** interpretations on the transcribed *Falcon* body. The earlier Childers study closes the same operation on a different published source, and should not be repeated. The result has **no bearing on printed-page/word coordinates**, especially the eight WN14 page numbers reaching 201 and 205; those require an edition-verified printed-folio layout. Agent10 is already pursuing that distinct layout. Do not present this negative as proof that no book-derived relation exists.

The original REC8/1 remains K01/K02/K03/K05/K06/K07 PASS, K04 and K08 unresolved, combined INCOMPLETE. A seventh slot has not passed.
