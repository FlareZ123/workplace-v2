# H-17 K04: selected-only per-attempt UTC clock reseeding, 14,154,352 full coupons checked

**Agent 18, 3 November 2026 | Original K04 NO_MATCH.** Original six component PASS results survive, K04/K08 still MISSING, combined INCOMPLETE.

## New producer hypothesis

The original 3 October incident-date ESC-N print route selects `PS-261003-0417`, RECOVER, attempt2 ACK at **18:02 UTC**. The recovered spool buffer is not independently byte-authenticated, and existing printer MT hypotheses leave all 128 selected coupon bits unknown. An alternative explanation is a **special per-attempt reset**: the actual escrow coupon might have been freshly generated from a weak wall-clock seed, independently of the long-lived ordinary printer stream. This source-specific *selected-event generator* is not established by the company documents and need not reproduce any earlier LABEL/STORES spool packet.

The previous [Agent8 metadata-seeded producer](../agents/agent8/k04_selected_metadata_seed_sft.py) tested 52 isolated job/date/string/integer seeds (including exact 18:01/18:02/18:03 epoch seconds). Its test does not cover dense **unknown sub-minute second or millisecond seed values** near the selected ACK. This new test uses the original printer timestamps to define those seed ranges.

## Actual full-component original commitment test

Model a fresh `random.Random(integer_seed)` CPython MT19937 generator. For each seed, read successive `getrandbits(32)` words, take each overlapping fourword window, serialize with both per-word endian orientations and both fourword orders. XOR each complete 16-byte resulting opaque hypothetical coupon with the **unchanged** K04 mask; SHA256 the resulting 16-byte component and compare to the original full 256-bit K04 slot commitment.

| Seed/producer family | Seeds | Overlapping 4word windows / seed | Byte/word views | Full K04 SHA256 checks |
| --- | ---: | ---: | ---: | ---: |
| Every UTC integer second from **2026-10-03 07:00:00 through 18:26:00** | 41,161 | 16 | 4 | 2,634,304 |
| Every UTC integer millisecond from **18:00:00.000 through 18:04:00.000** | 240,001 | 12 | 4 | 11,520,048 |
| **Total** | | | | **14,154,352** |

**Original accepted K04 matches: 0.** A planted actual CPython seed at UTC epoch millisecond `1791050401000` and overlapping draw offset9 / reversed-fourword orientation2 reconstructs the full synthetic masked coupon uniquely, and the synthetic commitment is recognized exactly once. The normal source SHA256 pin authenticates the original spool copy; the selected line is used only to confirm job/ACK timestamp, never to fit a generator seed. Local Python standard-library execution completed all families in **33.97 seconds**, with zero original hits.

Reproducer: [`agents/agent18/k04_selected_clock_reseed_sft.py`](../agents/agent18/k04_selected_clock_reseed_sft.py), read-only and source-pinned. The portable repository version retains identical seed ranges, overlap rules, controls and original target comparison; the local implementation was independently executed.

## What this changes

The exact **integer second-seeded incident-day** and **integer millisecond-seeded 18:00..18:04 selected-epoch** CPython per-event reset hypotheses are excluded under their stated 4word serialization and small initial offset models. This is a **target-reaching complete-coupon test**, unlike source-only rank increases. It does not exclude arbitrary unrelated clock units, seeded generators with unknown salts, a different RNG, longer hidden draw offsets, true printer-native output, unknown original paper media or an unobserved copy/correction channel. The original sources do not attest that any attempt was clock-seeded.

This finite original-commitment negative provides zero new authenticated K04 coupon bits. K08 exact author-final caption remains unknown. REC8/1 still has **K01,K02,K03,K05,K06,K07 PASS; K04,K08 MISSING; combined INCOMPLETE**. Original `resources/`, `candidate.json`, acceptance and verifier were untouched.
