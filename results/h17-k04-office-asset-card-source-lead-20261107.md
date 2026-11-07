# K04 source lead: office asset card and September equipment count

**Status:** new source-acquisition lead; no coupon recovered and no source mapping authenticated.

## Direct evidence

The surviving print-fleet register at `resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt` states that the retiring cassettes were entered against property cards carried forward from the September equipment count (lines 4-6). Its route table maps:

`PS-261003-0417 -> ESC-N -> L-29/N -> FA-17 -> H17-POL-17/A3`

The same note says the property references were taken from the office asset cards (lines 27-28). Thus the K04-selected print job is explicitly joined to a specific property-card reference, and the register identifies two underlying source classes used to create that join.

## Missing records

Neither the September equipment-count sheet nor the office asset card itself is present in the 46-file supplied ZIP or the current `resources/` tree. The local bookmarks list the related `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx` and BX25 transfer files, but do not give an explicit path for the office asset-card set. Do not assume the renewal ledger is the card.

## Targeted retrieval

Request the original:
1. **H17-POL-17/A3 office asset card**, including both sides, annotations, attached endorsements and its original sleeve or folio.
2. Adjacent **A2/A4 card or revision-control records**, because the supplier reconciliation also contains an A3/A4 distinction; preserve both rather than selecting one from the duplicate ledger entry.
3. **September 2026 equipment-count sheet** covering ESC-N, ESC-S and WATCH-SPARE, including the cassette/asset identifiers and any card cross-reference.
4. Any office asset-card index or card-issue register that explains where A3 was filed and who reconciled it.

Preserve original bytes or scans, front/back images, revision marks, timestamps, signatures, folio/sleeve labels and custody metadata. Historical record acquisition only; no facility or printer operation.

## Why it matters

This is a source-defined bridge between the selected PS-0417/ESC-N print route and the property record FA-17 / H17-POL-17/A3. The asset card or equipment count may independently validate the route, identify the physical cassette/card custody, or point to the escrow-coupon record. It may also explain the A3/A4 duplicate. It does **not** establish that the coupon is an asset-card serial, that the card contains the 16-byte coupon, or that the +300/+304 ticket crosswalk is correct.

## Reproduction

The source statements and route tuple can be checked directly in the cited print-fleet register. No candidate bytes, acceptance values, masks, nonces or verifiers were changed.

