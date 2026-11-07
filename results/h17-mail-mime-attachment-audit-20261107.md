# Supplied H-17 mail export: MIME attachment inventory

**Agent 36 · 7 November 2026**

## Question

Could any of the 20 supplied .eml files contain an embedded photo, caption sidecar, PDF, or other attachment that is not visible in the plain-text mail-body review?

## Method

Parsed every file under evidence/mail/*.eml in the supplied ZIP with Python's standard-library email.parser.BytesParser(policy=policy.default). Walked every MIME part and recorded part count, multipart status, content type, content disposition, filename, decoded payload size and SHA-256.

## Result

- Messages inspected: **20**
- Total MIME parts: **20**
- Every message is a single-part, non-multipart **text/plain** message.
- Attachment filenames: **0**
- Content-Disposition: attachment parts: **0**
- Image, HTML, PDF, spreadsheet or other non-text MIME parts: **0**

Therefore the supplied mail export contains no embedded photo, scan, caption sidecar or other attachment recoverable by MIME parsing. This is a bounded statement about the supplied 20-message export only. It does not establish that the original mail system never carried attachments or that a separate photo-caption archive did not exist.

## Reproduction

Use Python's standard library:
- Parse each file with BytesParser(policy=policy.default).
- Iterate list(message.walk()).
- Record get_content_type(), get_content_disposition(), get_filename(), and get_payload(decode=True).
- The supplied export yields exactly one text/plain part per message and no filenames or attachment dispositions.

## Consequence

Do not spend further effort searching the supplied .eml files for hidden image attachments. The K08 photograph/caption material and Emily's WN-14 desk-note stack must be sought as separate original records or in a historically preserved photo/profile archive. No exact K08 words were recovered, and no original candidate, verifier, route sheet or acceptance commitment was changed.
