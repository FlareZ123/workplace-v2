# K04: North/South cassette catch-control and physical-part hypothesis

**Agent 36 · 7 November 2026 · source-pinned, read-only comparison**

## Question

Do the L-29/N and L-29/S return records provide a new physical discriminator for locating the selected North coupon or identifying what the North ST-112 catch-cleaning work handled?

## Source-backed crosswalk

The 4 October 2026 print-fleet register maps:

| Role | Print job | Route | Return set | Account | Filing reference |
|---|---|---|---|---|---|
| Selected North | PS-261003-0417 | ESC-N | L-29/N | FA-17 | H17-POL-17/A3 |
| South control | PS-261003-0448 | ESC-S | L-29/S | LV-42 | CS-18/5 |
| Watch-Spare control | PS-261003-0420 | WATCH-SPARE | L-29/W | ST-09 | STORES/FLT |

The North and South binder indexes each contain five tabs in the same part-category order:

| Tab | North L-29/N | South L-29/S |
|---|---|---|
| 01 | ST-094, lid plate return | ST-130, lid plate return |
| 02 | ST-081, edge guide exchange | ST-151, edge guide exchange |
| 03 | ST-106, separator refit | ST-121, separator refit |
| 04 | ST-099, hinge retain | ST-135, hinge replace |
| 05 | ST-112, catch clean | ST-142, catch retain |

The supplier reconciliation independently places all five North tickets in R3/POSTED/FA-17/H17-POL-17/A3 and all five South tickets in R3/POSTED/LV-42/CS-18/5. It separately records:

- North ST-112 R3: POSTED, FA-17/A3, €0.00, **catch cleaning**.
- North ST-112 R4: HELD, FA-17/A4, €0.00, **duplicate settlement**.
- South ST-142 R3: POSTED, LV-42/CS-18/5, €6.00, **catch pin**.
- Watch-Spare ST-157 and ST-164: R3/POSTED, ST-09/STORES/FLT, spare inspection.

The R3/A3 North ticket is the selected posted record. Preserve R4/A4 separately as a held duplicate; it is not an alternate spool attempt or a second physical coupon.

## New physical interpretation

The strongest new discriminator is the **matched tab-05 catch comparison**. The two cassette records place a catch operation in the same final tab position. The South supplier description explicitly calls its retained item a **catch pin**. Together with the lid plate, edge guide, separator and hinge categories, this makes a **mechanical cassette catch, pin or latch** a more plausible interpretation of the word “catch” than an assumed paper-output tray.

This remains an inference. The records do not identify the North catch's exact location, prove that ST-112 and ST-142 are the same part number, or establish that paper passed through or lodged against either part. The North ticket says “clean”; the South ticket says “retain” and the supplier docket says “catch pin”. The original service sheets and physical parts must resolve the distinction.

A second timing discriminator is available. The selected North RECOVER ACK2 event is timestamped **3 October 2026, 18:02 UTC**. The print-fleet return register says its cabinet-office copy was reconciled **4 October 2026, 09:18 UTC**, a difference of **15 hours 16 minutes**. This establishes that the return register was reconciled after the selected print event. It does **not** timestamp the ST-112 work itself or prove that a coupon was recovered during cleaning.

MAIL-16 independently identifies the last acknowledged attempt for the exact ESC-N job as the selector and warns that the dispatch ACK is not a media-integrity check. This analysis uses only that event's header and timestamp. The selected PAYLOAD bytes are never extracted or used.

## Testable physical recovery route

The highest-value comparison is now specific:

1. Inspect the original **North ST-112 R3/POSTED/A3** ticket and tab-05 binder sheet, front and back, including serials, part number, exact physical location, work time, signatures, attachments, carbonless underlay and custody marks.
2. Determine whether cleaning removed, exposed, retained or discarded any material. Request any found-item pouch, return bag, paper strip, label, debris sample, catch component or attached note associated with the work.
3. Inspect the original **South ST-142 R3/POSTED/CS-18/5** ticket and retained catch pin as a physical comparator. Record its part number, geometry, location and disposition. Do not treat it as a same-role output witness.
4. Keep Watch-Spare ST-157/ST-164 as a separate inspection control. Do not assume the three routes share a printer model, host or cassette assembly.
5. Require a provenance bridge from any recovered material to job PS-261003-0417 and the physical/copy stage selected by MAIL-16. A ticket number, matching part category or later reconciliation date alone is insufficient.

A positive result would be an original retained item or receipt with an independent link to the selected North print/copy stage and a complete 16-byte coupon value. A negative result would be a documented ST-112 work record showing that no relevant item was retained or that the catch is unrelated to the media path; K04 would then still require the original job object or an independent coupon witness.

## Reproduction and limits

Run from the repository root:

```bash
python agents/agent36/k04_catch_control_sft.py
```

The standard-library SFT verifies source hashes, checks all North/South R3 settlement mappings, distinguishes ST-112 R3/A3 from R4/A4, validates the ST-142 and Watch-Spare controls, and computes the 15h16 interval. It never reads the selected payload value into a candidate or prints it.

Source SHA-256 pins:

- `print-fleet-retirement-note.txt`: `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`
- `supplier-reconciliation-L29.csv`: `73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e`
- `spool-reconstruction.log`: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`

The local run passed all source pins and mapping assertions. Output confirms the North/South category order, North ST-112 R3 POSTED and R4 HELD statuses, South ST-142 “catch pin”, the 15h16 interval, and `selected_payload_bytes_used=false`.

**Outcome:** this is a new source-derived physical-part hypothesis and retrieval discriminator. It does not recover the coupon, authenticate the copied ACK2 bytes, or change the six accepted components. K04 and K08 remain MISSING; combined recovery remains INCOMPLETE.
