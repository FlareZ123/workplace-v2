# K04: six-full-word-plus-one-bit carrier screen

**Agent 9 | 22 November 2026 | Bounded source-carrier test under the conditional p951 MT19937 model.** No K04 candidate or authenticated target bit recovered.

## Question

Agent19's 193-bit reduction shows that six complete future native MT words at stages 1180, 1181, 1347, 1348, 1574, 1575 plus one selected bit from stage 1179 are sufficient to determine the 128-bit selected coupon under the p951 source model. The single bit may be native bit31 or any of tempered output bits 2, 9, 13, 20, 27 or 31.

The earlier seven-word carrier test assigned three distinct 16-byte source families to donor groups of 3, 2 and 2 complete words. This experiment tests the sharper 193-bit witness against the same eight source families, without requiring a complete 1179 word.

## Frozen inputs and construction

- The original spool SHA-256 is 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083. The 132 intact non-target printer packets constrain the p951 MT basis; selected ACK2 row129 is excluded before payload parsing. Source rank is 15,365.
- The six complete donor positions are 1180, 1181, 1347, 1348, 1574 and 1575. The seventh observation is one bit at 1179.
- The eight source families are K01 WN-14 raw bytes, K05 TRP2 raw bytes, K06 RC-17 raw bytes, the K04 route mask, the K08 desk nonce, and the accepted K02, K03 and K07 16-byte components.
- Each source family is interpreted under all eight whole-word views: little/big endian, native/tempered, and forward/reversed four-word order.
- Three distinct source families are assigned to the three donor groups. The first contributes a one-bit view of its first word plus its next two complete words; the second and third contribute their first two complete words. Whole-word reversal also covers the corresponding last-word layouts.
- The original K04 SHA-256 commitment is used only as the final candidate check. The selected ACK2 payload, acceptance verifier and candidate file are not used to choose donor assignments.

The source-quotient construction has one affine compatibility syndrome for each of the seven partial-bit views. A genuine source-compatible synthetic MT state was used as a positive control for each view.

## Results

| Measure | Result |
|---|---:|
| Source rank | 15,365 |
| Partial-bit views | 7 |
| Synthetic positive controls | 7/7 PASS |
| Three-family assignments | 1,204,224 |
| Source-compatible assignments | 610,176 |
| K04 commitment matches | **0** |

The local source-equivalent run completed in 19.89 seconds. The committed reproducer is agents/agent9/k04_p951_193bit_carrier_sft.py.

## Interpretation

This closes the specified 193-bit extension of the earlier eight-family carrier screen: none of the 1,204,224 assignments in this three-distinct-family, eight-word-view, first/last-layout domain yields the original K04 commitment.

It does not establish that the p951 MT chronology is historically correct, nor exclude other source families, noncontiguous or arbitrary within-carrier word selections, different stage assignments, or a different producer/copy mechanism. The seven donor observations remain hypothetical; no original K04 bits are authenticated by this result.

K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain missing; combined REC8/1 remains incomplete. No original source, candidate, commitment or verifier was changed.


## Additional source-cued test: ATTPTTAILBIT

The first-word initials of the selected 14 notes have been observed as ATTPTTAILBITTE. Treating ATTPT TAIL BIT as a possible locator for the least-significant bit of the selected K04 attempt is posthoc and is **not** prescribed by the source. The incident-date selected attempt is 2, so this interpretation fixes the partial donor bit to 0.

Reusing the same six full donor positions, eight source families, three-distinct-family assignments, eight word views and seven possible MT bit positions, the fixed-zero test produced:

| Measure | Result |
|---|---:|
| Assignments | 1,204,224 |
| Source-compatible assignments | 610,176 |
| K04 commitment matches | **0** |

The local source-equivalent run completed in 20.25 seconds. The repository reproducer now includes this bounded test as well as the carrier-derived partial-bit test.

This closes only the specific ATTPTTAILBIT → selected-attempt-LSB=0 interpretation over the same source-carrier domain. It does not make the acrostic a source-mandated K04 instruction or validate the conditional p951 chronology.


## Raw-preimage extension: 11 source families

The carrier set was extended with the three direct 16-byte preimages of accepted K02, K03 and K07, rather than only their accepted component hashes:

- K02 raw LT-204 words: E1A5E474BAD7E853A2E8C71D3317D507. This is the eight selected GOOD/HOLD raw_u16 values, ordered by sequence and packed big-endian.
- K03 raw PTW-417 serial quartet: D7DAD6BC9714519B7DAD0AD4BE8E87FD. This is the highest signed CLOSED AS_LEFT serial suffix per bay, in field-sketch order B,D,A,C.
- K07 raw AX-7782 checkpoint chain: 8947CEDCB9CC73BAB7E87BE63302C5C9. This is the second-attempt checkpoint for each chunk, ordered by sequence 0 through 7.

The 11-family search retains the same six complete donor stages, seven stage-1179 partial-bit views, three-distinct-family assignment, eight endian/native-tempered/forward-reverse word views, and first/last group layout. A precomputed affine-column C++ kernel evaluates the 193-bit map; Python checks each source-compatible 16-byte component against the original K04 SHA-256 commitment.

| Measure | Result |
|---|---:|
| Source families | 11 |
| Assignments | 3,548,160 |
| Source-compatible assignments | 1,786,176 |
| Candidate commitment checks | 1,786,176 |
| K04 commitment matches | **0** |
| C++ search kernel | 151 ms |
| SHA-256 scan | 1.24 s |

Reproducer: agents/agent9/k04_p951_193bit_raw_preimage_sft.py and its adjacent C++ kernel agents/agent9/k04_p951_193bit_raw_preimage_sft.cpp. The Python driver builds the source quotient, compiles the C++ search, and checks the candidate hashes against resources/acceptance.json.

This adds the direct K02/K03/K07 source preimages to the bounded carrier domain; it still does not provide a source-authored mapping from these values to the future MT stages. It does not validate the p951 chronology or exclude other source families, within-carrier selections, stage assignments, or producer/copy mechanisms.


## Cross-check against the global stage-sum falsifier

Agent18's source-pinned results/h17-k04-twin-template-global-stage-falsifier-20261122.md independently finds 25 historical witnesses but only 23 signatures; the four apparent held-out matches are two duplicated signatures. Under the source-constrained global draw model (ACK rows 4–100 draws, REQUESTED rows 0–100), the selected row's S129-S45 range is 550–613, while all 23 transferred signatures require 621–626. Thus 0/23 signatures transfer to row 129. The p951 schedule is a feasible positive control for the historical equations and gives target gaps 401/609; it is not the repeated-twin schedule (396/622) and is not proof of the printer's actual generator.

The 193-bit screen above is conditional on the p951 future-stage construction; its zero-hit result does not authenticate that construction. Keep it as a bounded negative experiment, not a K04 recovery. Do not extend future-stage/carrier searches without a source-authenticated host-stage or serialization record.


A further source-field check of the 25 recurrence triplets found 0/25 with all three rows at the same destination, 2/25 with all three rows in the same class (both LABEL, across different destinations), and 0/25 with a common class and destination. None is an all-RECOVER triplet; the withheld target is RECOVER/bench. This does not rule out every multi-stream architecture, but the observed witnesses do not support a per-class or per-destination stream selector for PS-0417.


The trimmed-export caveat prompted a one-hidden-row sensitivity check. Under the same historical witness system, S99-S45 is bounded below by 398, whereas either repeated twin requires 396. An omitted row with a nonnegative draw count inserted before row 99 can only increase that gap; inserted after row 99 it leaves the gap unchanged. The already-reported all-row 0–100 sensitivity likewise leaves both twins infeasible. Thus one simple omitted-row insertion does not rescue the repeated-twin transfer, although this does not rule out a different raw-row mapping or producer/serialization model.


Partition sensitivity: rerunning the same twist-pair witness detector independently within source partitions yields no witnesses in any of the nine CLASS×DEST groups. CLASS-only counts are LABEL 2 (both span different destinations), RECOVER 0, STORES 0; DEST-only counts are bench 0, desk 0, store 0. The target RECOVER/bench partition has 15 rows and zero witnesses. The 25 global witnesses therefore arise only when mixing classes/destinations; they do not support a simple independent MT stream per class or destination.
