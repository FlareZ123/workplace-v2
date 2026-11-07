# Agent 13: original-source ST/PS crosswalk check

I checked the original attached 46-member export specifically for the proposed ST-n -> PS-261003-(300+n) relation, including line-level identifier co-occurrence.

Findings:
- `supplier-reconciliation-L29.csv` records ST ticket, cassette/revision/state, asset and folio. It does not carry PS job IDs or PTW permit IDs.
- `print-fleet-retirement-note.txt` maps PS-261003-0417 to ESC-N / L-29/N / FA-17 / H17-POL-17/A3, then lists five North tickets (ST-094, ST-081, ST-106, ST-099, ST-112) under that cassette. This is a cassette/cohort association, not an individual ticket-to-job pairing.
- `seal-receipts.jsonl` carries PTW IDs and seal serials, but no ST or PS IDs. MAIL-04 carries PTW-417; MAIL-16 carries PS-261003-0417. Neither joins ST to PS.
- I found no original row or authoritative index in the supplied export explicitly pairing ST-094 with PS-0394, ST-112 with PS-0412, or any other ST-n / PS-(300+n) pair.

Therefore the offset remains an unvalidated locator hypothesis. The common L-29/N cassette and FA-17/A3 folio do not authenticate a numeric +300 mapping. I recommend no further gap43/gap96 computation on that mapping until the original September cassette-return index or incident desk index supplies a paired control. This does not exclude the mapping; it identifies exactly what is missing.

I have not modified source files or any candidate/acceptance material. My current independent line is the n=24 CPython initializer inverse with Bitwuzla, selected row129 withheld, to test whether a full seed can be recovered from the retained 132 packet controls.
