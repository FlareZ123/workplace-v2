# BX25/08 closes the H17-POL-17/A3 Risk-folio bridge

**Date:** 2026-11-20  
**Scope:** K04 ESC-N / PS-261003-0417 source recovery  
**Status:** Positive source cross-reference; coupon value still absent

## Question

Does the surviving BX25/08 Risk scan connect the PS-0417-associated H17-POL-17/A3 record to the North office printer/cassette asset and the Risk-desk paper-key-register path?

## Method

Decrypted the local one-page \`BX25-08.pdf\` using the four-digit PDF release code 8131 and rendered the page for visual inspection. Compared its visible fields with the L-29 supplier reconciliation, the PS-0417 print-fleet crosswalk and the retired-office bookmarks. No protected R-drive or SharePoint service was accessed.

## Source evidence

1. The PDF heading is **RISK DESK — ANNUAL PROPERTY DECLARATION**. Its visible fields are:
   - Register: \`H17-POL-17\`
   - Property annex: \`A3 - North office equipment\`
   - Account reference: \`FA-17\`
   - Inward scan folio: \`BX25/08\`
2. Its declared office-property carry-forward explicitly lists **FA-17 — North office printer / cassette cabinet**.
3. Its footer explicitly states: **Policy file H17-POL-17/A3 | Transfer folio BX25/08**. This closes the folio bridge that was not established by the CSV rows alone.
4. The local supplier reconciliation has:
   - \`ST-112, L29, R3, POSTED, FA-17, H17-POL-17/A3, catch cleaning\`
   - \`RN-052, RISK, R1, FILED, FA-17, BX25/08, property annex scan inward transfer\`
5. The print-fleet retirement note associates PS-0417 with ST-112, FA-17, H17-POL-17/A3 and L-29/N tab05. That job/ticket association remains a corroborated crosswalk rather than a direct native queue foreign key, but the Risk PDF now independently joins the exact policy file and BX25 folio.
6. The retired-office bookmarks point to the H17-POL-17 renewal ledger, BX25 transfer index and \`R:/IT/desk-images/oldscan/scanrelease.txt\`. The bookmark description for scanrelease says BX25 folios used a four-position numeric release setting and the paper key register stayed with the Risk desk.

## Conclusion

The BX25/08 scan is an authenticated local bridge between the H17-POL-17/A3 policy file and the Risk transfer folio, and it identifies the declared North office printer/cassette cabinet. This materially strengthens the route from the PS-0417 crosswalk to the Risk-desk records.

The page is a property declaration, **not** the paper key register and **not** the 16-byte ESC-N coupon. The four-digit code 8131 is the PDF release code; it is not the K04 component. Standard 16-byte expansions of 8131 did not match the K04 commitment. The PDF's printed electronic correspondence index URL (\`https://noyes-energy-group.pages.dev/\`) could be another public lead, but the available web retrieval did not return its content.

## Next action

Prioritize an already-authorized local copy of the Risk-desk paper key register and its associated:
- H17-POL-17 renewal ledger;
- BX25 transfer index;
- oldscan release notes / folio sidecar.

Search specifically for the linked identifiers \`FA-17\`, \`H17-POL-17/A3\`, \`BX25/08\`, \`ST-112\` and \`PS-261003-0417\`. The decisive record would be the paper-key-register entry or native coupon value. If it yields the 16-byte ESC-N payload, XOR it with the unchanged K04 mask and verify against the original acceptance commitment.

Do not access the protected R-drive or SharePoint services and do not recontact the closed custodian channel. Use only a separately supplied, already-authorized local copy.

## Confidence and limits

- **High confidence:** the PDF visibly links H17-POL-17/A3 to BX25/08 and declares the North office printer/cassette cabinet.
- **Moderate-to-high confidence:** the PDF visibly closes the H17-POL-17/A3 ↔ BX25/08 folio bridge and identifies the North office printer/cassette cabinet.
- **Low-to-moderate confidence:** the Risk-desk paper key register is relevant to the BX25 release/key mapping. The bookmark describes a four-position release setting; the register may contain only PDF release settings rather than the ESC-N coupon. Its schema and entry are unavailable.
- **Unresolved:** the custodian note says this is not the full incident record; the paper-key-register entry, native PS-0417 rendered output and 16-byte coupon value are not present in the supplied export. Do not treat the 2025 property declaration as an incident record or infer coupon bytes from it.
