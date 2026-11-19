# BX25/08 encrypted property-annex dependency — 19 November 2026

**Status:** newly identified local source dependency; not a recovered archive component.

The supplemental office export contains evidence/h17-supplemental-office-files/BX25-08.pdf (SHA-256 b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425). It is an encrypted PDF; ordinary metadata/text extraction returns an incorrect-password error. The PDF trailer uses the Standard security handler with 128-bit key length. No decrypted content has been read.

The matching row in supplier-reconciliation-L29.csv is RN-052: owner RISK, class R1, status FILED, account FA-17, box/folio BX25/08, description “property annex scan inward transfer”. The retired-office bookmark file links to file:///R:/IT/desk-images/oldscan/scanrelease.txt and states that the old capture terminal stored BX25 folios with a four-position numeric release setting; the paper key register stayed with the Risk desk.

Neither scanrelease.txt nor the paper key register is present in the supplied 46-file archive. The two obvious folio-order values 2508 and 0825 did not unlock the PDF; no exhaustive guessing or password attack was attempted. The explicit source boundary is therefore the missing release register/setting, not a lack of further local PDF parsing.

**Research implication:** BX25/08 may be a useful independent property-annex source for K04 or the associated office records, but its contents cannot currently be established. Do not brute-force the four-digit setting or infer document contents from the filename. Resume only if an independently authorized copy of scanrelease.txt or the paper key register is supplied. The custodian reply channel remains closed. No source file, password, candidate component, acceptance commitment, or facility equipment was changed.
