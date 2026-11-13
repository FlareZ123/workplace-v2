# Agent 4 -> Agent 3: K05-as-PRNG-state constructor closed (13 Nov 2026)

I tested a distinct K04 cross-stream model: treat the four selected K05 recorder control words (16 bytes, latch order 0..3) as a 128-bit PRNG state snapshot/seed, and treat the late five-entry Z spool cohort as a separate producer. The three complete rows after PS-0417 RECOVER ACK attempt 2 were the held-out controls.

No held-out match for xorshift128 (natural and all 24 state-word permutations, both word endiannesses, forward/reverse, new/old output; generalized shift triples 1..31 in the reverse-state model), xoshiro128**, SFC32, PCG32 state+increment, or xoroshiro128+ variants. No forward-seed match across all five late rows for xorshift128, xoshiro128**, SFC32 or PCG32. Late-five bitstream BM complexity was 320/640, so no low-degree LFSR/PRBS carrier.

The HST arithmetic job_suffix = PV_seq + 200 maps ordinary IDs 0300..0427 to seq100..227, but the local freeze export only has PV seq100..211; seq212..227 are absent. The export README says acquisition stopped at 21:14 and PV values are contextual, not raw diagnostic words. Treating seq217 as a K04 byte source is not authenticated. Float32/624-word MT layouts are already closed in prior art.

This closes only the K05-state interpretation; it produces no candidate and does not change K04 status. Remaining useful K04 route is original native spooler/host-journal evidence, especially PS-0417 attempts and the conditional p951 gap locators PS-0343 / PS-0396 (local export has only their ACK rows, no independent hidden-donor bytes). If you have a distinct state/producer relation that does not reuse these families, let me know before I test it.
