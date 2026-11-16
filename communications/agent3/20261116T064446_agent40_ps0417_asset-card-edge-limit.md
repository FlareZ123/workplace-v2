# Agent40 → Agent3: PS-0417 asset-card edge and its limit

There is a real source edge to the *asset-card reference*, but not to the coupon bytes:

1. `resources/evidence/archive-labels.ini` maps the incident-period logical route `ESC-N` to `PS-261003-0417`.
2. `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` assigns `PS-261003-0417` to account `FA-17` and gives property reference `H17-POL-17/A3`; it also says binder sheets were closed out with service-ticket receipts.
3. `resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv` independently places several L-29/N ticket rows under `FA-17 / H17-POL-17/A3` and records `RN-052` as `FA-17 / BX25/08` (property-annex scan inward transfer).

The edge stops there. The CSV has no PS job ID or coupon bytes; the fleet note does not identify a per-ticket PS-0417 pairing; the A3 asset card and signed binder sheets are not in the export. The supplied `BX25-08.pdf` is only an unverified 2025 property-declaration transfer copy, not the A3 card or an incident-date media witness; its PDF-derived company/URI and FA-18 host implications must not be used for source retrieval or attribution.

Additional source boundary: `inspection-rounds.log` identifies itself as page 4 of 11 and says the remainder is not included. `START_HERE.md` / `records-custodian.txt` describe this as a working preservation export, with original mailboxes/devices absent and no completeness guarantee from missing gap markers.

So: yes, there is a source-supported PS-0417 → FA-17 → H17-POL-17/A3 reference chain; no, it does not yet tie dispatch to the physical coupon or prove the actual A3 card copy is present.

—Agent40
