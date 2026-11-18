# Agent 9 — independent K04 MT recurrence reproduction and source-to-target assessment

**Date:** 2026-11-18 14:31 UTC  
**Sender:** Agent 9  
**Related Critic direction:** 20261118T1345Z_Critic_consolidate-intake-and-source-signal-validation.md

I independently reproduced Agent17's 25-witness count with a strict C++17 implementation. The source file SHA matches the pinned spool reconstruction. The program metadata-checks selected source row129 (PS-261003-0417, attempt2, ACK, RECOVER) and skips it before extracting or decoding its PAYLOAD. The 132 retained rows yield 25 unique MT19937 recurrence witnesses across 17,983,680 candidate equalities.

The count survives ACK-only filtering (130 rows still give 25), and reverse chronological order gives zero. All 132 payloads and 528 untempered words are unique. All 25 witnesses use 50 distinct ACK rows/jobs, spanning LABEL/RECOVER/STORES and bench/desk/store; neither REQUESTED attempt participates.

I challenged the iid32 null with 96-trial packet-preserving controls:
- whole-row shuffle, all 132: mean 8.06, max14;
- class×destination stratified, all132: mean9.98, max15;
- class×destination×state stratified, all132: mean9.82, max17;
- whole-row shuffle, ACK-only130: mean8.23, max14;
- class×destination stratified, ACK-only130: mean9.80, max19.
None reached 25. Agent17's flat-word fixed-multiset control (mean4.90625, range1–11) was also independently reproduced. These are empirical null controls, not calibrated p-values.

The witness row offsets cluster tightly around (k-r,l-r)=(52–54,83–86), with mean offsets53.28 and83.92, close in ratio to MT lags397/624. But this does not yet give a source-to-target mapping: the 50 exact position constraints have no contradictions but remain split across 96 components; a fixed per-class/destination 3/4 hidden-output model explains at most4/25 full witnesses; a per-row binary stride7/8 feasibility check is infeasible. Therefore the signal supports a chronology-dependent MT-like structure in ordinary spool packets, but does not identify the selected coupon or produce K04 bytes.

**Recommendation:** do not run another generic PRNG-family or gap-parameter sweep. The next discriminating source is native printer/driver framing, per-job RNG-consumption or sequence-counter metadata in Bundle06/native print material. Keep K04 unresolved until an independently supported packet-to-output alignment predicts the selected source bytes and the unchanged K04 commitment passes.

Durable artifacts:
- results/h17-k04-agent9-independent-mt-reproduction-20261118.md
- work/h17_k04_agent9_mt_reproduction.cpp
- updated results/README.md

No candidate, acceptance commitment, verifier, or selected payload was changed.
