# K04: bounded North L-29/N ticket-row digest constructor

**Agent 3 | 13 November 2026 | 96 distinct complete 16-byte candidates | 0 K04 commitment matches**

## Question

Could the selected North ESC-N coupon be a 128-bit digest of the five North return-ticket rows associated with the printer fleet register, rather than a value reconstructed from the unverified copied ACK buffer?

This is a bounded source-derived constructor, not an assertion that the ticket register is the coupon issuer.

## Source relation and selection

The fleet return register associates job `PS-261003-0417` with `ESC-N`, return set `L-29/N`, account `FA-17`, and folio `H17-POL-17/A3`. Its binder index gives the five tickets in this order:

`ST-094, ST-081, ST-106, ST-099, ST-112`.

The reconciliation CSV contains five corresponding rows with `run=R3`, `posting=POSTED`, `account=FA-17`, and `folio_or_jacket=H17-POL-17/A3`. The selection deliberately excludes the earlier `R2/VOID` ST-099 row and the later `R4/HELD` duplicate ST-112 row. The CSV's own row order is `ST-094, ST-106, ST-112, ST-081, ST-099`.

Pinned original source SHA-256 values:

- `print-fleet-retirement-note.txt`: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `supplier-reconciliation-L29.csv`: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`
- `recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

## Candidate construction

For each of the two source-defined row orders (binder order and CSV order), serialize the five exact selected CSV rows as:

1. rows joined by LF;
2. rows joined by LF with a final LF;
3. header plus rows joined by LF;
4. header plus rows joined by LF with a final LF.

For each serialization, compute six natural 128-bit digest outputs:

- MD5;
- first 16 bytes of SHA-256;
- first 16 bytes of SHA-512;
- BLAKE2s with 16-byte digest size;
- BLAKE2b with 16-byte digest size;
- first 16 bytes of SHA3-256.

Test each digest both as the complete K04 component and as a pre-mask payload, in which case XOR it with the official 16-byte K04 mask. This yields 2 × 4 × 6 × 2 = **96 distinct complete 16-byte candidates**.

The script also performs an in-family planted-target positive control: the same SHA-256 commitment comparison finds the planted candidate exactly once.

## Result

**No match.** None of the 96 candidates hashes to the official K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The experiment therefore rejects this bounded ticket-row digest family. It does **not** establish a ticket-to-coupon derivation, validate the separate arithmetic ST-to-PS offset hypothesis, or authenticate any missing printer-side object.

## Reproduction

Run:

`python agents/agent3/k04_north_ticket_row_digest_sft.py`

The script pins the source files and acceptance target, reconstructs the exact row selection, asserts 96 unique candidates, verifies the planted positive control, and asserts zero original-target hits. It does not modify `candidate.json`, the official verifier, source resources, or acceptance commitments.

**Archive status unchanged:** K01, K02, K03, K05, K06, and K07 remain accepted; K04 and K08 remain unresolved; combined REC8/1 remains incomplete.
