# K04: North L-29/N ticket-row digest constructor with South holdout

**Agent 3 | 13 November 2026 | 96 distinct candidates per route | 0 North commitment hits | 0 South control hits**

## Question

Could the selected North ESC-N coupon be a 128-bit digest of the five North return-ticket rows associated with the printer fleet register, rather than a value reconstructed from the unverified copied ACK buffer?

This is a bounded source-derived constructor, not an assertion that the ticket register is the coupon issuer. The South ESC-S job provides a historical-job holdout for the same constructor.

## Source relation and selection

The fleet return register associates job `PS-261003-0417` with `ESC-N`, return set `L-29/N`, account `FA-17`, and folio `H17-POL-17/A3`. Its binder index gives five tickets in this order:

`ST-094, ST-081, ST-106, ST-099, ST-112`.

The reconciliation CSV contains five corresponding rows with `run=R3`, `posting=POSTED`, `account=FA-17`, and `folio_or_jacket=H17-POL-17/A3`. The selection deliberately excludes the earlier `R2/VOID` ST-099 row and the later `R4/HELD` duplicate ST-112 row. The CSV's own row order is `ST-094, ST-106, ST-112, ST-081, ST-099`.

The same fleet register associates `PS-261003-0448` with `ESC-S`, `L-29/S`, `LV-42`, and `CS-18/5`. Its five binder tickets are `ST-130, ST-151, ST-121, ST-135, ST-142`; the corresponding R3/POSTED CSV row order is `ST-151, ST-121, ST-130, ST-142, ST-135`. The retained PS-0448 RECOVER ACK1 payload is `234BE186E97EE05830909790E336109E`. This is used only as a same-format historical-job control, not as an independently authenticated physical coupon.

Pinned original source SHA-256 values:

- `print-fleet-retirement-note.txt`: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `supplier-reconciliation-L29.csv`: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`
- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `recovery-routing.json`: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json`: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

## Candidate construction

For each route (North and South), use the two source-defined row orders (binder order and CSV order). Serialize the five exact selected CSV rows as:

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

Test each digest both as the complete component and as a pre-mask payload (digest XOR the supplied K04 mask). This gives **96 distinct complete 16-byte candidates per route**. The North set is compared by SHA-256 against the official K04 commitment; the South set is compared byte-for-byte against the retained PS-0448 RECOVER ACK1 payload.

The script also performs an in-family planted-target positive control on the North candidate set; the identical SHA-256 comparison finds the planted candidate exactly once.

## Result

**No match on either route.**

- North: 0 of 96 candidates match the official K04 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
- South: 0 of 96 candidates match the retained PS-0448 RECOVER ACK1 payload `234BE186E97EE05830909790E336109E`.

The independent South holdout means this exact ticket-row digest constructor does not explain even the intact-copied control job. Reject this bounded family. This does **not** establish that no source-derived North/South relationship exists, nor does it authenticate an individual ticket-to-coupon foreign key.

## Reproduction

Run:

`python agents/agent3/k04_north_ticket_row_digest_sft.py`

The script pins all five source files, reconstructs both route-specific row selections, asserts 96 unique candidates per route, verifies the planted positive control, and asserts zero North and South matches. It does not modify `candidate.json`, the official verifier, source resources, or acceptance commitments.

**Archive status unchanged:** K01, K02, K03, K05, K06, and K07 remain accepted; K04 and K08 remain unresolved; combined REC8/1 remains incomplete.
