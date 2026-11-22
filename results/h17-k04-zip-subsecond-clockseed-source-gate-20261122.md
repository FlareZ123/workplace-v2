# K04 packaging-subsecond clockseed: complete source-packet negative

**Agent 23 | 22 November 2026 | original-source-only producer exclusion; no recovered K04.**

## Question and causal test

Previous ZIP packaging-clock study exhausted **whole-second** CPython MT seeds over a two-day window; separate microsecond studies considered the **incident-day** clock for an unrelated late ACK. This test asks a different bounded question: if the artificial ZIP preservation process itself produced printer bytes using a CPython `random.Random` state seeded from the **fractional second** of its first preserved UTC packaging timestamp, can that stream reproduce one complete, undisputed historical printer packet?

The earliest preserved ZIP extended UTC entry timestamp corresponds to **2026-10-20T04:12:14Z**, epoch **1792469534**. It is an export-packaging time, not a demonstrated historic producer event. The frozen source comparator is intact **PS-261003-0300**, payload `FBBBC54356483F5864BB3F06794518A5`, in `resources/evidence/print/spool-reconstruction.log`, SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

For every microsecond integer `us = 0..999999`, two independently specified source seed families:

1. `random.Random(float(1792469534) + us/1e6)`.
2. `random.Random(1792469534*1000000 + us)`.

For each seed, generate native CPython `randbytes(32768)`, representing 8,192 consecutive 32-bit words. Search **every 4-word consecutive window** with **all 24 fourword orders and all 16 within-word byte reversal combinations**, hash-indexing a whole 4byte source word to avoid needless full checks. A source hit is a **full matching 16byte intact coupon**; word-prefix coincidences are never accepted. No disputed PS-0417 ACK2 bytes, K04 route mask, K04 acceptance hash, or K08 information enter this test.

## Complete local execution

| Model | Complete interval | Historical full-packet hits | Runtime |
| --- | ---: | ---: | ---: |
| Float epoch seconds + microsecond fraction | 1,000,000 microseconds | **0** | 172.306 seconds |
| Integer Unix epoch microseconds | 1,000,000 microseconds | **0** | 169.124 seconds |
| **Combined** | **2,000,000 seed assignments** | **0** | **341.430 seconds** |

Both locally executed versions print a genuine seeded, complete-packet fourword-permutation/reversal positive control PASS, and check the original spool SHA before the historical sweep. The float calibration additionally mutates one recovered byte and rejects the planted corrupted whole-packet. The execution logs ended in the full `tested=1000000` and `source_packet_matches=0` summaries, with no aborted shards.

The portable read-only [consolidated SFT](../agents/agent23/k04_zip_subsecond_source_sft.py) codifies both models; the complete local execution used logically identical separate Python implementations. The report contains observed results, not a claim of independent remote rerun.

## Scope and next decision

Neither exact microsecond seed family can issue that original intact 16byte first printer packet within the 8,192-word prefix under those word serializers. Therefore it provides no source-grounded stage/seed from which to construct the selected K04 physical coupon. This does not exclude different seed clocks, float conversions, separate late-job streams, buffering, original printer/host processes, or genuine physical coupon reconstruction. The packaging timestamp is an observed export time only, not an authenticated spool generation time. **Original K04 commitment was NOT_EVALUATED, because no source model matched.** Six old components remain PASS; K04/K08 remain MISSING; combined REC8/1 INCOMPLETE.

Do not multiply the same timestamp neighborhoods or float integer encodings absent a new source-defined clock/writer link. A materially different candidate-generation mechanism or recovered original document is required for a full missing value.
