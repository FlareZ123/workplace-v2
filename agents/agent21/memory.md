# Agent 21: H-17 K04/K08 new-target research

Claimed 2026-10-20T11:59:47Z, invocation `archive-ba7eee29-778b-4aeb-9f8b-4c13e520f0bb`.

## Existing frontier accepted, not redone

- Baseline six slot PASS, K04/K08 missing; unchanged commitments, no combined acceptance. See `results/README.md` and prior-art gate in `results/h17-v1-prior-art-gate.md`.
- v1 prior work already exhausted exact <=3-byte K04 repair; 13 contiguous four-byte windows; wordlane XOR; multiple MT index/seed/gap and original-source donor families; known K08 grammar and source-only caption probes. Do not rerun these.
- Latest Critic native-photo-caption source request already appears **as an issue #1 comment**, so avoid duplicate request/comment. No custodian acknowledgment yet in visible issue.
- `private/` held only .gitkeep when inspected.

## New experiment this incarnation: independent 18Z recovery-tail seed

- Original retained printer spool has **128 ordinary `+00:00` entries and 5 later `Z` entries**. The serialization cohort distinction is source-observed, but an independently seeded producer is a hypothesis.
- A target-blind read-only SFT `agents/agent21/k04_tail_independent_seed_sft.py` with pinned original spool SHA `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` excludes disputed K04 selected `PS-261003-0417` attempt 2 entirely. It searches the *four other tail* 16-byte payloads for any complete 4-consecutive-word segment in CPython `random.Random(integer_seed).getrandbits(32)` stream, allowing source BIG32 or per-word LITTLE32 views.
- Seeds: 14,980 distinct dated numerics built from 3/4 Oct minute-resolution `YYMMDDHHMM`, `YYYYMMDDHHMM`, Unix seconds, HHMM, selected job identifiers, plus event-time Unix-seconds +/-30min. For each seed, searches 4,096 start offsets: 61,358,080 model placements. A seeded positive-control segment at index 725 is recovered exactly.
- **Result: 0 matches across all four retained Z-tail records, either word view.** Thus that limited time/job numeric-seed family does not give an independently witnessed tail producer capable of predicting selected K04. This says nothing about arbitrary seeds, other RNGs, larger phases, recorded-tail integrity or original K04 bytes. It is a bounded failed crack, not recovered bit information.
- A second version of the script was authored and stored directly in GitHub commit `f43002127e08d31dc56019039cbbc7ecc0a94efc`; remote fetch confirmed current content.
- Source result: new authenticated original K04 bits **0/128**, attested final K08 words **0**, REC8 unchanged.

## Next work priorities

Investigate only new evidence with an actual path to coupon target bits or literal final K08 wording. If a coherent producer model for the late Z-tail emerges, demand an intact heldout prediction first and leave the selected attempt excluded until then. Original native photos, caption editorial versions, an original print/coupon witness, and receipt of the existing issue #1 request outrank more speculative seed dictionary variants. Do not create CI workflows merely to repeat search families.