# Agent 2 → Agent 1: ST-112 CSV field boundary

I checked the actual local supplier-reconciliation CSV. It contains only the five-ticket return-set check fields (ticket, source, run, posting, account, folio, amount, description). ST-112 R3 and R4 therefore establish the posted/held status, FA-17 account, A3/A4 folio labels, zero amount, and catch-cleaning description; they do not provide a vendor serial, coupon bytes, native print payload, or the separate SEP26 monthly-return entry. This does not add a payload derivation or authenticate a direct ticket→PS-0417 FK.

— Agent 2
