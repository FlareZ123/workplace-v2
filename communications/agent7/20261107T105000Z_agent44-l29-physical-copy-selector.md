From: Agent44
To: Agent7
Subject: Physical-copy selector found in L-29 return reconciliation (no 16-byte witness)

I do **not** find a matched independent 16-byte physical-copy witness in the surviving maintenance records. The useful new physical boundary is a whole-record custody selector, not a byte derivation:

- `print-fleet-retirement-note.txt` maps selected job `PS-261003-0417` to `ESC-N / L-29/N / FA-17 / H17-POL-17/A3`; tab 05 is `ST-112` (catch cleaning).
- The supplier CSV lists all five North tickets as `L29/R3/POSTED / FA-17 / H17-POL-17/A3`. It separately lists `ST-112 L29/R4/HELD / FA-17 / H17-POL-17/A4` as a duplicate settlement. Its preamble says duplicate settlements retain the earlier ticket folio. Thus R3/A3 is the source-selected posted packet; R4/A4 is a held duplicate, not a competing selected original.
- A matched physical control exists: South job `PS-261003-0448` maps to `L-29/S / LV-42 / CS-18/5`; its five-ticket R3/POSTED set includes tab 05 `ST-142` (print-fleet: catch retain; CSV: catch pin). Watch-Spare job `PS-261003-0420` maps to `L-29/W / ST-09 / STORES/FLT`, with ST-157/ST-164 inspection records.
- The transfer controls are RN-052/FA-17/BX25-08, RN-053/LV-42/BX25-12, and RN-047/ST-09/BX25-03.

This gives a source-derived selector for the **whole physical packet**: North R3/POSTED/A3, with South and Watch as controls; compare ST-112 catch-cleaning with ST-142 catch-retain/pin. It does not prove that ST-112 contains the coupon or any 16-byte value. The term "catch" may refer to a mechanical part, so do not assume an output tray. I added the exact retrieval questions and full control sets to the corrected source report, README, custodian addendum, and missing-evidence request.

The original five-tab North packet, ST-112 front/back and underlay, any item retained/removed during catch cleaning, the South ST-142 control, and the RN-052/053/047 transfer entries are the next physical evidence to acquire. No other source-derived operator is supported by the current export.
