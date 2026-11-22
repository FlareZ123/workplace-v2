# H-17 K04: four stage-feasible three-native-word templates, complete free-32-bit SHA-256 search

**Agent 4 | 22 November 2026 | 17,179,869,184 full original SHA-256 comparisons, zero K04 hits.**

## Recovery question

The retained printer source shows four mutually constraining two-word MT19937 recurrence doublets. Their source-stage sums force one or more ordinary interpacket gaps to consume at most six native outputs if a single chronological generator emitted the packets ([separate source theorem](h17-k04-four-doublet-min7-schedule-obstruction-20261122.md)). Given this restriction, can a complete K04 coupon be reconstructed by treating three of its native words as determined by two intact historical spool packets and enumerating the remaining 32-bit word without using the disputed selected ACK2 payload?

This test constructs and exhausts four specific complete-coupon families. It is a speculative historical producer model, since the surviving source does not attest printer firmware MT19937, shared whole-stream stages, or the exact job gap selected.

## Frozen original inputs and target boundary

- Original spool: resources/evidence/print/spool-reconstruction.log, SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083.
- Selected job: original raw row129, 3 October 2026 18:02 UTC, PS-261003-0417, RECOVER/ACK attempt2. It is identified by original metadata; its copied payload is **omitted before decoding** and never consulted for template construction.
- Source donors: original intact row45 PS-0345 STORES/ACK and row98 PS-0398 LABEL/ACK, parsed as little-endian four-word 32-bit MT19937 outputs and untempered.
- Original K04 mask: 8556C8CB6140A7F9A5123AC7571BEE1C.
- Original K04 SHA256 target: 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.
- The source pins for the original routing JSON and acceptance JSON are checked by the [source-template SFT](../agents/agent4/k04_mt_threeword_free32_sft.py). Canonical candidate.json, original records and verifier are untouched.

For native words x at hypothetical chronological stage S, standard MT19937 gives

    x[S+624] = x[S+397] XOR twist(x[S],x[S+1]).

Let each packet's four native words correspond to stages S_row, ..., S_row+3. The source-connected triple model asserts, for d=0,1,2,

    x[target][q+d] = x[row98][i+d] XOR twist(x[row45][d],x[row45][d+1]).

Here q and i each range over {0,1}, so the full predicted coupon has three contiguous fixed 32-bit native words and one free 32-bit word. Temper the predicted words and write them little-endian as 16-byte raw coupon, XOR the unchanged route mask to obtain a complete candidate component, and compare its SHA256 to the unchanged 256-bit K04 commitment. The free word is enumerated as **every uint32 value 0..2^32-1**, with no prefix pruning.

The corresponding source-stage requirements are S98-S45=397-i and S129-S45=624-q. A source-blind integer linear feasibility check of the seven separate original doublets with row gaps 7..9, one hypothesized six-output exceptional gap at source row65, row117 (same selected job's earlier LABEL ACK), or row120 (separate WATCH-SPARE job), and late-Z gaps 4..12 **admits every one of these four geometries**. Stage feasibility is only a necessary conditional criterion. No source record authenticates the exceptional gap or this generator. The source-bound chronology and record roles remain unproven.

## Exact four fixed templates

The following are complete 16-byte K04 **component** templates, after the published route-mask reduction. Zero bytes designate the entire 32-bit free word, not independently known zero bytes.

| Source construction | Fixed component bytes | Free word |
| --- | --- | --- |
| r45/k98, q0/i0 | 9B1222B432AD70512F49799500000000 | word3 |
| r45/k98, q0/i1 | 9E3499EAD038B488FA2D93C900000000 | word3 |
| r45/k98, q1/i0 | 000000007F044D86F6FFED6FDD40AD4E | word0 |
| r45/k98, q1/i1 | 000000007A22F6D8146A29B608244712 | word0 |

The [source-pinned Python SFT](../agents/agent4/k04_mt_threeword_free32_sft.py) independently reproduces all four templates from the surviving rows and original route mask with MT19937 temper/untemper controls. It neither reads selected ACK2 payload nor attempts a shortcut to the missing free word.

## Completed full-component original run

[Portable C++17/OpenSSL SHA-256/OpenMP full uint32-worker](../agents/agent4/k04_mt_threeword_free32_scan.cpp) partitions each free word into 4,096 disjoint 2^20-value shards. Every shard checks the full 16-byte SHA256 in one standard SHA256 compression block with the correct 16-byte message padding. The worker compares all 256 bits of the untouched official target. It also constructs a synthetic full-component target with free-word value 0x17C0FFEE, using the independent OpenSSL SHA256 API, and must recover that planted positive **exactly once per template** before returning success.

Actual original 22 November local execution, five OpenMP workers, reproduced from the exact original uploaded ZIP:

| Template | Exact complete K04 checks | Original hits | Independent planted hits |
| --- | ---: | ---: | ---: |
| r45/k98 q0/i0 | 4,294,967,296 | 0 | 1 |
| r45/k98 q0/i1 | 4,294,967,296 | 0 | 1 |
| r45/k98 q1/i0 | 4,294,967,296 | 0 | 1 |
| r45/k98 q1/i1 | 4,294,967,296 | 0 | 1 |
| **Total** | **17,179,869,184** | **0** | **4** |

The actual terminal line was:

    SUMMARY full_candidates=17179869184 original_hits=0

Every template printed COMPLETE with exactly 4,294,967,296 checks, planted_hits=1, original_hits=0. The four execution durations were approximately 52.447, 52.343, 52.409 and 52.681 seconds. These are environment-specific timings.

## Interpretation

**This complete 17.18-billion-candidate source-dependent family does not recover K04.** It excludes the four stated three-native-word + arbitrary-final-word formulas under the original mask and SHA256 commitment. It does **not** exclude a different historical issuer, source stage/call schedule, three-word extraction from a different pair of intact packets, another byte serializer, or the lost physical coupon.

The fixed predicted words remain **hypothetical**, as there is no source-authenticated whole-packet holdout that establishes the generator/position mapping. A stage-compatible integer solution does not authenticate any physical K04 bit. Extending the search to arbitrary donor pairs without a source-defined selection rule would compound unsupported hypotheses. The more valuable next milestone is a source-stage relation with a successful blinded intact-packet prediction, leading to all four coupon words, or the actual historical original coupon.

K01/K02/K03/K05/K06/K07 remain individually PASS. K04 and K08 remain MISSING; combined REC8/1 INCOMPLETE. No original evidence, acceptance, canonical candidate or verifier was modified.
