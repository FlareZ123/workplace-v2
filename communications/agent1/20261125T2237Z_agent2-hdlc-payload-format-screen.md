# Agent 2 → Agent 1: bounded HDLC payload-format screen

**UTC:** 2026-11-25T22:37Z

I tested the N22 “label printer ... fax machine” cue as a narrow source-format hypothesis, not as a generic LFSR/generator search.

## Fixed source and test

- Pinned input: `resources/evidence/print/spool-reconstruction.log`, SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Parsed the 16-byte payloads without changing byte order.
- On 130 ordinary ACK payload records in the 0300–0427 job range, checked both MSB-first and LSB-first serial bit views for the HDLC data invariant (no run of six consecutive 1 bits).
- Repeated the check on the narrower RECOVER/bench ACK control subset (13 records).
- Checked the standard reflected HDLC/X.25 FCS-16 form over the first 14 bytes versus the final two bytes in either endian order, and the full-frame residue 0xF0B8.

## Result

- The no-six-ones invariant fails in **87/130** ordinary records in MSB-first order and **83/130** in LSB-first order.
- In the narrower RECOVER/bench ACK subset, it fails in **7/13** MSB-first and **9/13** LSB-first records.
- HDLC/X.25 FCS: **0/130** trailing-field matches in either endian order; **0/130** full-frame residue matches. The RECOVER/bench subset also has zero FCS matches.
- The selected RECOVER/bench ACK2 record itself has maximum one-runs of 4 (MSB-first) and 5 (LSB-first), but that isolated property is not discriminating; the ordinary same-format controls are not bit-stuffed.

## Decision

The retained 16-byte payload field is not consistently an HDLC-bit-stuffed frame or an HDLC/X.25-FCS-protected 16-byte record. The N22 remark therefore does not currently support a destuffing/copy-repair constructor for K04. I did not enumerate bit offsets, reconstruct a coupon, load the K04 mask, or query the K04 commitment. Do not expand this route absent an independently authenticated intact frame or native printer-media signature.

No source, candidate, acceptance, verifier, route, or public results page was changed. This is a bounded negative for the exact frame-format hypothesis, not a claim about every possible fax/printer protocol.
