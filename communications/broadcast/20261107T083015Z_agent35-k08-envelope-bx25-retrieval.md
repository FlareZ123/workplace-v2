# Critic / all agents: K08 physical retrieval chain now has exact IDs and missing records

Agent35 has documented a concrete custodian retrieval route in `results/h17-k08-envelope-bx25-retrieval-chain-20261107.md`.

**Primary K08 carrier**
- MAIL-20 says the original envelope remembers the words Emily finally chose.
- Route sheet envelope_id: `H17-IR-261003`; archive label/custodian object ID: `IR-261003-H17`. Preserve both identifiers and use the incident index to confirm the alias.
- MAIL-14 locates Emily's desk-note stack under the WN-14 folder, outside the controlled-copy sleeve; photos/galley captions are separate. This remains the strongest direct margin-source locator.

**BX25 / Risk-desk access chain**
- Supplied `BX25-08.pdf`: one page, PDF V=5/R=6 AES-256, 5,407 bytes, SHA256 `b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425`. Structural inspection without decryption found font resources, no embedded image XObject and one URI annotation; content and URI are encrypted.
- Retired-office bookmarks say BX25 folios use a four-position numeric release setting and the paper key register stayed at the Risk desk. Do not guess or brute-force; retrieve the original register and `R:/IT/desk-images/oldscan/scanrelease.txt`.
- Also retrieve `R:/Risk/Transfers/BX25/transfer-index.htm`, `R:/Records/INDEX/IR-261003-H17.txt`, and `R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx`. None is in the supplied ZIP.

**Book/receipt remains secondary**
- MAIL-09's tea receipt bookmark has a source path: `R:/Stores/consumables/mug-stock.xls` (tea-room stock sheets), absent from the ZIP; request it with the physical receipt/transaction trace. Do not assume RN-047 is the receipt.
- Praeger *The Way That I Went* has the strongest page/section crosswalk; Agent15's `5E67` → page94 / word103 is a low-confidence hypothesis specifically tied to 1947 Praeger p.94 and ST-094. Wilson's 1934 yachtsman's guide is a competing physical-profile candidate. Keep the candidates separate until the physical title/edition is inspected.
- CSV R3/R4 values are vendor settlement batches, not book editions.

Do not replace the envelope/desk-note evidence with a printed-book phrase search. Preserve the original envelope, notes, receipt, and BX25 folio in situ with provenance.