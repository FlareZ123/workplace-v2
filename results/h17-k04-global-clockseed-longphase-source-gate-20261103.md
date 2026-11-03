# H-17 K04: source-only global clock-seed hypothesis across 8192 output positions

**Agent20 | 3 November 2026 | New source-conditioned negative; no seventh component.**

## Different producer hypothesis

[Agent18's selected-only clock-reseed experiment](h17-k04-clock-reseed-selected-only-producer.md) tests new short-offset generator resets at the disputed 18:02 coupon against the K04 commitment. The present experiment instead asks whether the **ordinary retained printer's global shared generator** could be an ordinary integer-seeded CPython `random.Random` initialized from archive dates/times, with any prior draw offset from 0 through 8191. It tests a **full intact source packet**, not a candidate selected coupon or partial MT state. This is a conditional clock-seed producer model, without historical software attestation.

Use original ordinary printer job `PS-261003-0300` intact 16-byte payload `FBBBC54356483F5864BB3F06794518A5`, from original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Interpret each complete 16-byte packet as four consecutive native CPython MT words emitted in little-endian form by `Random.randbytes`. The underlying source-only p951 chronology suggests such a word grouping, but does **not** prove a historical common generator. Retain the packet unchanged and search all 8192 aligned 32-bit word starts in each independent seeded stream. The disputed selected 18:02 ACK, original mask, slot SHA256, K08, verifier and canonical candidate are **never inspected or queried**.

## Source-defined finite seed families and exact local outcome

| Integer seed family | Seed count |
| --- | ---: |
| Every Unix UTC epoch second from **2 October 00:00** through **5 October 00:00 exclusive**, 2026 | **259,200** |
| Eight-digit numeric calendar neighborhood `20260000..20269999`, including `20261003` | **10,000** |
| Every valid twelve-digit `YYYYMMDDHHMM` minute across 2, 3, 4 October 2026 | **4,320** |
| Every valid fourteen-digit `YYYYMMDDHHMMSS` second on 3 October 2026 | **86,400** |
| **Total distinct integer seeds** | **359,920** |

**Executed on original supplied ZIP, unmodified**: every seed emitted its first 8192 complete 32-bit outputs. The exact first four original packet bytes occurred at **zero aligned word offsets** across these 359,920 streams, hence zero complete 16-byte source-packet matches. This is 359,920 × 8192 = **2,948,464,640** tested aligned word positions; the prefix filter avoids unnecessary 16-byte comparisons. Measured local wall runtime 47.41s. Source `random.Random(seed).randbytes(8192*4)` matches CPython’s little-endian 32-bit output assembly. A real seeded synthetic positive at numeric seed `1791079160`, stream word phase **2000**, was recovered exactly once within the three-seed neighborhood `seed-1,seed,seed+1`; the planted positive uses an independent full 16-byte packet.

[Single-file reproducible SFT](../agents/agent20/k04_global_clockseed_longphase_sft.py) pins source SHA256, confirms the intact job identity/bytes, generates exactly all four seed families and asserts the original and synthetic counts. It is read-only with no acceptance oracle.

## Scope and limits

This eliminates **only** the enumerated clock-derived integer seed families when the original intact first print job is a consecutive four-native-output packet somewhere in the first 8192 draws of its generator. It does not test unknown salted seeds, millisecond-valued global seeds, unrelated PRNG producers, different packet serialization, arbitrary earlier draw counts or independent selected-event generation. It does not show that the ordinary printer did use Python MT. The expected number of random first-32-bit accidental collisions at this finite search size is less than one, so **zero firstword hits alone is no evidence for stronger exclusion beyond the exact seeds tested**.

This result yields **zero independent K04 selected coupon bits** and **zero exact K08 final words**; the original six accepted slots are unchanged, K04/K08 unresolved, and combined REC8/1 still INCOMPLETE. Future effort should be tied to evidence of a historical seed or a complete selected-event producer, not a larger arbitrary clock dictionary.
