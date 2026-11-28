# K04: source-fixed 133-row spool chronology falsifies a saturated first-packet generator fit at four independent whole-packet controls

**Agent 8 · 28 November 2026 | original source private replay performed; no K04 recovery**

## Question and source/fit ledger

The original PS-0417/18:01Z REQUESTED1 contains two intact 64-bit words, i.e. **128 observed bits**. One mathematically recovered xoroshiro128++ (49/21/28) state has **128 fitted state bits** and exactly replays this packet under one explicit **big-endian, BA word-order** serializer. This is a saturated fit, *not* authentication that the print host used xoroshiro128++. Can that very state also predict other independently retained whole printer packets **before using the selected damaged ACK2 or the original K04 commitment**?

| Frozen by surviving source / mathematical specification | Not fixed by surviving source; hypothesis or free fitting |
| --- | --- |
| Pinned original 133-entry printer spool; chronological row order and exact intact retained source strings | Hypothetical xoroshiro128++ output generator; 128-bit initial state chosen to fit one 128-bit packet |
| Target REQUESTED1 is chronological row **128**; source-compatible state is at its first output | A 1:1 mapping of successive logged rows to successive two-word generator packets, with no skipped native outputs, rekey, reset or buffering |
| Source-ordered other retained whole ACK records are rows **117,127,131,132** | A single stream across class and destination changes and the full 07:00–18:25 spool timeline; **historically unproved** |
| Source-fixed relative native-output offsets **-22,-2,+6,+8** from row128 | Retained ACK buffer bytes are independent of the REQUESTED1 fitting pair but do not independently certify physical media integrity |
| Four-byte-order/byte-slip domains are not searched; serializer stays **big/BA** chosen for the source fit | The BA serializer itself is not authenticated by hardware specification |
| Exact complete 16-byte equality of each predicted ACK packet | No use of K04 SHA commitment, K04 mask, selected ACK2 or later REQUESTED3 to choose state, controls or comparisons |

The firstpacket state came from an exact source-private P12/P16 enumeration at P12 parent 1371, with one terminal source-compatible model and fifteen terminal empty child cubes; source bytes and the state are not committed or printed. For control row index `i`, the frozen native word offset is `2×(i−128)`. Generate two consecutive words, serialize big/BA, and compare the **entire 16-byte packet** with the source's independently logged ACK.

A second predeclared downstream interpretation treats the unacknowledged REQUESTED3 as **zero** generator-output consumption, subtracting two native words from the two later ACK prediction offsets. This is an alternative, not a post hoc arbitrary gap sweep.

## Completed original-source results

The pinned original spool SHA256 check and exact original REQUESTED1 firstpacket replay both **PASS**. The four independently retained complete ACK controls give:

| Independent original ACK role | Source row | Fixed native offset | Whole 16-byte source prediction | Byte positions matching of 16 |
| --- | ---: | ---: | --- | ---: |
| Earlier same-job LABEL/ACK1 | 117 | -22 | **MISS** | 0 |
| Immediately preceding routine ACK | 127 | -2 | **MISS** | 1 |
| Later south RECOVER/ACK1 | 131 | +6 | **MISS** | 1 |
| Later spare RECOVER/ACK2 | 132 | +8 | **MISS** | 0 |
| **Total** | **4** | | **0 / 4** | **2 / 64** |

For both later ACK records, the no-REQUESTED3-output alternative also returns **MISS (0/2)**. The original K04 acceptance commitment, K04 mask, disputed selected ACK2 copied payload and later REQUESTED3 payload were **not used** for fitting or the original holdout scoring.

The portable [source-private reproducer](../agents/agent8/k04_bigba_source_fixed_chronology_holdouts.py) pins spool SHA256, requires a private chmod0600 full state that replays the exact source anchor, and never prints historical source words/states/candidates. It includes **16 independent planted 128-bit states × 5 offsets = 80 full-packet positive replay checks**, exact inverse-roundtrip assertions, and single-bit negative controls; the 80 positive controls PASS. Source-free mode reads no archive. Original local execution produced the four complete misses reported above.

## What this decides

**The predeclared uninterrupted one-log-row/one-16-byte-packet source history is contradicted by four independently retained historical printer ACK source records.** Its four errors are complete 16-byte misses, not weak SHA-prefix failures. This materially weakens a simple globally shared printer-stream explanation for the apparent REQUESTED1 source-state match.

This does **not** prove xoroshiro128++ wrong in every possible local epoch, disprove the K04 historical coupon, certify true ACK physical media bytes, or close arbitrary hidden native-output skips and rekeys. Unlike the bounded 2^32-gap source studies, this chooses *no gap* because the literal complete spool row chronology fixes an explicit, testable mapping. A model that arbitrarily inserts hidden gaps or starts a separate state at 18:01 remains possible but is less independently identified; it must supply external evidence for those decisions before receiving more SAT computation.

This is an **independent held-out-source negative**, not an original K04 component or full eight-part key. The acceptance stays **K01/K02/K03/K05/K06/K07 PASS; K04/K08 MISSING; REC8/1 INCOMPLETE**. No primary evidence, acceptance, route, candidate or verifier was changed; no hash-only restricted PDF was inspected.
