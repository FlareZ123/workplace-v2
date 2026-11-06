# K04 ticket-indexed five-part spool-fragment assembly: bounded negative

**Date:** 2026-11-06  
**Identity:** Agent 26  
**Status:** no K04 candidate hit; no component recovered

## Question

Can the five L-29/N service-ticket records associated with the selected FA-17 / ESC-N cassette be treated as five source packets whose contiguous fragments assemble the 16-byte K04 printer coupon?

This is a deliberately exploratory source-relationship hypothesis. The print-fleet register ties job `PS-261003-0417` to `ESC-N`, `L-29/N`, account `FA-17`, and folio `H17-POL-17/A3`. Its binder index lists, in order:

1. ST-094 — lid plate, return
2. ST-081 — edge guide, exchange
3. ST-106 — separator, refit
4. ST-099 — hinge, retain
5. ST-112 — catch, clean

The L-29 supplier docket has R3/POSTED records for all five tickets under the same FA-17 / H17-POL-17/A3 account/folio. ST-112 also has an R4/HELD duplicate-settlement record; the test uses its R3/POSTED record.

**Unproven mapping:** interpreting each three-digit ticket suffix as a one-based payload-record ordinal in `spool-reconstruction.log` maps the five tickets to job IDs 0393, 0380, 0405, 0398, and 0411. Each mapped record is attempt-1 ACK, and each precedes the selected `PS-261003-0417` attempt-2 ACK at zero-based payload-record index 129. No source explicitly states that ticket suffixes are spool ordinals. The numerical alignment is the hypothesis under test, not an established fact.

## Candidate model

Each of the five mapped 16-byte payloads contributes one contiguous fragment to a 16-byte coupon. The coupon is partitioned as one 4-byte fragment plus four 3-byte fragments. The 4-byte fragment may come from any of the five parts. Every fragment may be taken from any valid offset and in forward or reverse byte order.

Two source-grounded concatenation orders were tested:

- **Binder order:** ST-094, ST-081, ST-106, ST-099, ST-112.
- **Chronological spool order:** ST-081, ST-094, ST-099, ST-106, ST-112.

For each candidate coupon, the unchanged route mask is applied as `component = coupon XOR masked_component`; the original K04 SHA-256 commitment is then checked. The complete family contains **79,905,280 assignments per ordering**.

## Result

| Ordering | Assignments | Original K04 hits | Planted positive hits | Exact selected ACK2 reconstructions |
|---|---:|---:|---:|---:|
| Binder | 79,905,280 | 0 | 2 | 0 |
| Chronological | 79,905,280 | 0 | 1 | 0 |
| **Total** | **159,810,560** | **0** | **3** | **0** |

The planted positive controls use a synthetic target constructed from the same source fragments and verify that each enumeration reaches a valid construction. The binder control has two representations of the same planted coupon under different segment boundaries; the chronological control has one. These are assignment counts, not claims of unique candidate values.

The selected attempt-2 ACK payload was also used as a source-to-source holdout. No candidate in either family reconstructs it exactly.

**Conclusion:** the tested five-source, contiguous `4+3+3+3+3` fragment model does not produce the committed K04 coupon and does not reproduce the selected ACK2 copy. This rejects only this explicit model. It does not establish that ticket suffixes really index spool records, and it does not exclude other encodings, transforms, fragment boundaries, or source relationships.

## Reproduction

Source-pinned C++17 implementation: [`agents/agent26/k04_ticket_five_part_fragment_sft.cpp`](../agents/agent26/k04_ticket_five_part_fragment_sft.cpp).

Compile with OpenSSL available:

```bash
g++ -O3 -march=native -std=c++17 agents/agent26/k04_ticket_five_part_fragment_sft.cpp -lcrypto -o k04_ticket_five_part_fragment_sft
```

Run once for each ordering:

```bash
./k04_ticket_five_part_fragment_sft /path/to/extracted/h17-archive-dump binder
./k04_ticket_five_part_fragment_sft /path/to/extracted/h17-archive-dump chronological
```

The program pins the spool, fleet note, supplier docket, route, and acceptance SHA-256 values; asserts the five binder and R3 supplier rows; checks the ticket-indexed job identities and selected ACK2; and requires the planted positive control to be found. Local `g++ -O3 -march=native` / OpenSSL 3.0.13 runs took 25.60 s (binder) and 25.86 s (chronological).

## Limits and next use

The most important uncertainty is the ticket-suffix-to-spool-ordinal mapping. It is not authenticated by the source. The 4+3+3+3+3 partition and contiguous-fragment rule are also modeling choices, not source-defined mechanics. Do not expand this into arbitrary ticket-derived transformations without new evidence that links the ticket receipts to those exact spool records or specifies a fragment/assembly operation. If that link emerges, a new model should use the authenticated part order and an independently checkable intact control.

No K04 bits were recovered. The six established components remain the only accepted slots; combined REC8/1 acceptance remains incomplete.
