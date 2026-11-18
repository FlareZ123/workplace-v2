# K04/K05 cross-source check: authoritative recorder selection is not an MT anchor

**Status:** bounded negative; source-derived, not a K04 recovery.

## Question

Could the accepted K05 trip-recorder control words provide an independent cross-source constraint on the p951 printer MT stream, and thereby help resolve the K04 missing 128-bit window?

## Method

- Rebuilt the exact p951 printer-only GF(2) MT basis using the existing Agent49 implementation at agents/agent49/k04_p951_symbolic_basis.py, with selected spool row129 omitted as required.
- Confirmed rank **15,365** over the declared symbolic stage range **-1100 through 1040**.
- Parsed all 88 TRP2 recorder records, retaining the 84 CRC-valid records.
- Applied the route-defined K05 selection exactly: node 49, event 82, UTC interval [21:14:00, 21:14:08), greatest sequence per latch, then latch order 0–3.
- Compared each selected 32-bit control word against every fully or partially known tempered MT output in the symbolic range, in both byte orders.
- Separately checked nonselected records in the same route filter for exact full-word matches.

Reproduction: python3 agents/agent50/k04_trip_recorder_cross_stream_sft.py

## Authoritative K05 selection

The route rule selects these four CRC-valid records, all timestamped 2026-10-03 21:14:02Z:

| Record index | Latch | Sequence | Control |
|---:|---:|---:|---|
| 34 | 0 | 300 | FF8B7820 |
| 53 | 1 | 301 | 0A56E858 |
| 0 | 2 | 302 | 6DCDA00E |
| 10 | 3 | 303 | F01E4572 |

Concatenation in latch order is:

FF8B78200A56E8586DCDA00EF01E4572

Its SHA-256 matches the K05 acceptance commitment. The selection is internally consistent.

## Cross-stream result

None of the four authoritative K05 control words has an exact 32-bit match at any stage in the -1100..1040 printer-only MT basis.

Best agreement with known output bits (maximum over the scanned stages):

| Latch | Control | Little-endian best | Big-endian best |
|---:|---|---:|---:|
| 0 | FF8B7820 | 25/32 | 26/32 |
| 1 | 0A56E858 | 26/32 | 24/32 |
| 2 | 6DCDA00E | 25/32 | 24/32 |
| 3 | F01E4572 | 25/32 | 25/32 |

There are exact full-word MT matches among **nonselected** records in the same node/event family, but the route rule excludes them:

| Record index | Latch | Sequence | Control | Timestamp | Exact MT stage |
|---:|---:|---:|---|---|---:|
| 40 | 0 | 990 | 5E9C08AB | 21:14:10Z | -322 |
| 12 | 1 | 201 | 8052760C | 21:14:02Z | -321 |
| 28 | 2 | 992 | 9359AC1F | 21:14:10Z | -316 |
| 17 | 3 | 203 | BFB00270 | 21:14:02Z | -315 |

Records 40 and 28 are outside the K05 time window. Records 12 and 17 are superseded by the higher-sequence in-window records 53 and 10. They must not replace the route-selected values.

The four nonselected exact matches are already implied by the printer-only basis: adding their 128 untempered bit equations at stages -322, -321, -316 and -315 leaves rank at **15,365**. They do not reduce the selected K04 128-bit nullspace.

## Conclusion and limitation

The apparent recorder/MT link is a stale-record trap, not a valid K05 anchor. The authoritative accepted K05 component is not an exact raw MT-output window under the p951 printer-only basis. Do not use the superseded/out-of-window records to claim a cross-source phase anchor.

This does **not** prove that no other recorder field or generator model can relate the two subsystems. It only closes the specific raw-control-word bridge tested here. K04 remains unrecovered; this result supplies no candidate bytes, seed, or selector.