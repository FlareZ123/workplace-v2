# K08 exact-source screen: complete email spans and direct printer-packet identity

**Agent 44 | 7 November 2026 | source-derived test | no K08 component recovered.**

## Question

Two finite, source-grounded direct-carrier paths had not been closed together:

1. Could the exact normalized final K08 wording already occur as a contiguous phrase in any surviving email subject or body?
2. Could the K08 16-byte HMAC component itself appear verbatim as one of the intact 16-byte printer packets, including a LABEL packet?

The first path is a direct literal retrieval from the supplied mail corpus. The second tests exact component identity, not an invented packet transformation.

## Frozen source and method

The executable standard-library reproducer is [\`agents/agent44/k08_email_packet_identity_sft.py\`](../agents/agent44/k08_email_packet_identity_sft.py).

Pinned original inputs:

- \`acceptance.json\`: \`681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f\`
- \`recovery-routing.json\`: \`f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5\`
- \`spool-reconstruction.log\`: \`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083\`
- Sorted 20-message EML manifest (filename, NUL, original bytes): \`a96c73a0913e518af06afea06324dd4479e89fa41c753f9b93c81df1db89b3e1\`

The original K08 normalization and HMAC-SHA256 key/nonce are read from the unmodified route file. Every candidate component is reduced to the first 16 HMAC bytes, then compared through the full unchanged K08 SHA-256 commitment.

### Email corpus

- Parsed all 20 original \`evidence/mail/*.eml\` records.
- Each is one \`text/plain\` body, with no MIME attachment or multipart alternative in the supplied export.
- Enumerated every contiguous word span of every subject and body, from one word through the full segment length.
- 40 subject/body segments; **153,525 span occurrences** and **151,443 distinct normalized spans**.
- **Zero** complete K08 commitment matches.

### Printer packet corpus

- Selected the disputed K04 event using header fields only: \`PS-261003-0417 / ATTEMPT=2 / ACK / RECOVER\`.
- Excluded record index 129 (source line index 130) before reading its \`PAYLOAD\`.
- Compared SHA-256 of each of the **132 intact 16-byte payloads** directly with the K08 component commitment.
- The set contains 52 \`CLASS=LABEL\` packets and 132 distinct payloads.
- **Zero** direct K08 component matches.

### Positive controls

- A planted phrase in a synthetic email segment is recovered through the same normalization, HMAC16 and full-commitment path.
- A planted 16-byte component in the synthetic packet list is recovered by the same direct-identity loop.

Both controls pass. The selected K04 payload, K04 mask and K04 commitment are not used.

## Interpretation

The supplied 20-message EML corpus does not contain the final K08 phrase as any contiguous normalized subject/body span. The 132 intact spool payloads do not contain the K08 component by exact 16-byte identity.

This is a bounded negative result. It does not exclude:

- quoted material omitted from the export, original \`References\`/\`In-Reply-To\` history, native mail attachments, or a different original mailbox rendition;
- Emily's original envelope, N23 margin, WN-14 under-folder notes, separate photographs/galley captions, or the physical shelf card;
- an edited/noncontiguous phrase assembled from multiple source objects;
- a printer or envelope representation that transforms the K08 component.

The email scan is distinct from the earlier test that searched for known crew-note phrases quoted in emails: this test starts from every contiguous phrase in the email corpus and asks whether it passes the final K08 commitment. The packet test is likewise a direct K08 component identity check, not a shared-mask or pairwise transform.

## Next useful source action

Do not repeat contiguous email-span or direct packet-identity searches against the same export. The next useful evidence is the authenticated native mail/export source (including omitted quoted history and attachments), the original H17-IR-261003 envelope, Emily's original N23 margin and WN-14 desk-note stack, and the separate photo/galley-caption material. Authenticate the original mail namespace before native-thread lookup; the exported Message-IDs are not proven native retrieval identifiers.

**Recovery accounting is unchanged:** K01/K02/K03/K05/K06/K07 PASS; K04 and K08 MISSING; combined recovery INCOMPLETE.
