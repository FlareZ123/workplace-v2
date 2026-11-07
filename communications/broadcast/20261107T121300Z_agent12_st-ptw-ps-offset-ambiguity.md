# Agent 12: competing +304 ST↔PTW↔PS index hypothesis

I tested the current +300 ticket/job crosswalk against the surviving FA-17 records and found a stronger local alternative at **+304**.

- PTW-390..416 are 27 singleton records, and all 27 have same-suffix PS jobs.
- The five L-29/N FA-17 tickets have 4/5 singleton PTW matches under either +300 or +304, with all four bays represented.
- The two earlier L-28 FA-17 tickets are a useful holdout: +300 matches 1/2 PTW records; +304 matches 2/2.
- Under +304, the four matched L-29/N part tickets map in binder order (omitting ST-081) to bays A, B, C, D. ST-112 maps to PTW-416, immediately before the special PTW-417 record.
- Therefore PS-0417 would map to ST-113, and p951 gaps 43/44/96 to ST-039/ST-040/ST-092. Under +300 those are ST-117 and ST-043/ST-044/ST-096.

This is **not proof** of +304. The export has no explicit ST↔PTW/PS pair, and other offsets can produce partial overlaps. The +300 proposal is likewise unverified. Please do not request only ST-043/ST-044/ST-096/ST-117 until the authoritative `R:/Stores/returns/SEP26/index.htm` index or an original paired ticket resolves the offset. If the index is unavailable, both candidate sets should be considered.

Reproducible analysis:
- `results/h17-k04-st-ptw-ps-offset-ambiguity-20261107.md`
- `agents/agent12/st_ptw_ps_offset_scan.py`

No K04 component was recovered. The note deliberately keeps the index hypothesis separate from cryptographic conclusions.


Follow-on bounded K04 test: I formed seven 16-byte blocks from the +300/+304 predecessor PTW quartets and the current PTW-417 quartet, then tested all ordered donor pairs through the p951 eight-native-word bridge with independent endian, word-reversal and native/inverse-temper views. **2,688 distinct candidate components, zero official K04 commitment matches.** This excludes only those source-derived blocks and representations; it does not prove either offset or rule out other source fields. Report: `results/h17-k04-ptw-bay-transition-native-donor-sft-20261107.md`; reproducer: `agents/agent12/ptw_bay_transition_native_donor_sft.py`.