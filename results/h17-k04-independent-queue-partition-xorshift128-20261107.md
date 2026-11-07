# K04 independent queue-partition xorshift128 holdout test

**Agent 44, 7 November 2026. Result: the frozen partitioned-stream family fails.**

## Question

Could the printer maintain an independent Marsaglia xorshift128 (four 32-bit words, shifts 11/8/19) stream for each explicit queue partition, with the first intact packet in each partition supplying its initial state? This is a bounded test of whether the spool's `DEST`, `CLASS`, or joint `CLASS × DEST` field defines an independent packet stream.

No source claims that the printer used xorshift128. The algorithm is a test hypothesis; the partition keys are taken from actual spool header fields.

## Method

- Pin the original spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Select the target row from the `archive-labels.ini` ESC-N route plus `JOB/ATTEMPT/STATE/CLASS` header fields. The selected zero-based row is **129**, `PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER / DEST=bench`.
- Do not parse the selected row's PAYLOAD. It is retained as a missing target and never compared.
- For each partition map (`DEST`, `CLASS`, `CLASS × DEST`), seed one independent 128-bit state from the first intact packet's four words, then generate exactly four words per subsequent packet.
- Test little-/big-endian word parsing and forward/reversed word order: **12 complete configurations**.
- Compare all generated packets other than the selected target to the corresponding original payloads. This includes both late RECOVER ACK controls: row131 `PS-261003-0448` and row132 `PS-261003-0420`.
- For every partition/serialization configuration, run a synthetic stream with independently seeded states and require exact whole-packet recovery, including the selected-position synthetic packet and both late controls.

Reproducer: [`agents/agent44/k04_destination_partitioned_xorshift128_sft.py`](../agents/agent44/k04_destination_partitioned_xorshift128_sft.py).

## Results

| Partition | Packets checked (target excluded) | Exact matches | Late ACK controls |
|---|---:|---:|---:|
| DEST | 129 per serialization | 0 | 0/2 |
| CLASS | 129 per serialization | 0 | 0/2 |
| CLASS × DEST | 123 per serialization | 0 | 0/2 |

All 12 original-source configurations have zero exact packet matches. Both late ACK controls fail in every configuration. All synthetic positive controls pass. The selected target payload was not parsed and the K04 acceptance commitment was not consulted.

## Interpretation and limits

This excludes only the specific model tested: one continuous Marsaglia xorshift128 state per explicit `DEST`, `CLASS`, or `CLASS × DEST` partition, seeded from that partition's first intact packet, with four consecutive 32-bit outputs per packet and the four tested serializers.

It does not exclude per-job or per-event reseeding, a different generator, a different state initialization, hidden output gaps, a copier/replay stage, or a different physical-source mechanism. There is no evidence that xorshift128 was the historical printer producer. The test recovers **zero** K04 bytes and makes no candidate claim. K04 remains MISSING; the combined recovery remains INCOMPLETE.

This is distinct from continuous-stream hidden-gap tests and same-job xorshift128+ retry tests: the independent state is reset at each explicit queue partition, and whole packets are checked as holdouts.
