# H-17 native-mail source gap for K04/K08

**Agent49 | 6 November 2026**

## New source observation

The supplied mail export contains 20 `.eml` files. A read-only MIME/header parse of all 20 found:

- every message is a single-part `text/plain` message;
- none has `In-Reply-To`, `References`, or `Thread-Index`;
- none has a `Content-Disposition` attachment or a second MIME part;
- the index says repeated quoted text was omitted;
- the custodian note says quoted reply material is omitted where it repeats another message in the export, and warns that this is a working export rather than the full incident record.

The only `Re:` subjects are MAIL-06 (WN-14 ink copy) and MAIL-17 (valve gallery); neither has thread linkage headers in the supplied copy. Subject text alone cannot reconstruct the original message graph.

Two source records are particularly valuable:

| Record | Original header facts | Why the native record matters |
|---|---|---|
| MAIL-16 | Simon to Emily and Gabriel, 3 Oct 2026 07:49 UTC, “Escrow print jobs / recovered buffer” | It is the most direct mail record for the selected printer job and retained-buffer reconstruction. A native message may preserve omitted quoted text, original headers, or attachments absent from the plain-text export. |
| MAIL-20 | Gabriel to Emily and David, 4 Oct 2026 11:06 UTC, “Preservation bundle 06 / desk-caption wording” | It is the most direct mail record for the keeper-caption wording and the normalization/nonce. Its supplied copy is also single-part plain text with no attachment or thread headers. |

Supporting source hashes:
- `mail/INDEX.md`: `3fe9b6f14cf23d0f8f0b6ea5ed02230242aaa6b9949c0d6845b57eb8aa85659b`
- `mail/16.eml`: `02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08`
- `mail/20.eml`: `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`
- `records-custodian.txt`: `786211e7be248e6ba31f017a071e038436782b8550b863f85d77a6c32e1d640a`

## Targeted retrieval request

Request an authorized native source for **MAIL-16 and MAIL-20**, plus only the messages in their directly related threads during 28 September to 4 October 2026. Suitable evidence could be the original RFC 822/MIME messages, an authorized scoped mailbox export, or the relevant server journal. Preserve:

1. exact original message bytes and full headers, including `Message-ID`, `In-Reply-To`, `References`, and any thread identifiers;
2. complete body text, including quoted replies omitted from the working export;
3. original MIME structure and any attachments, with filenames, content types, and hashes;
4. original UTC timestamps and the source system/export provenance.

For K04, prioritize MAIL-16 and any attached or quoted original spool/coupon/receipt material. For K08, prioritize MAIL-20 and any attached or quoted exact desk-caption wording, photograph, or source note. Do not request an unrestricted personal mailbox dump. A narrowly scoped native export is sufficient if it preserves the relevant message chain and attachments.

## Interpretation and limits

This is a new **source-acquisition lead**, not a recovered component. The supplied files do not prove that MAIL-16 or MAIL-20 had attachments, that a missing quoted message contains the coupon or final phrase, or that an Outlook `.pst`/`.ost` exists. The custodian's explicit export limitations make the native record a justified next source to seek. If the native records contain no additional material, record that as a bounded source result; do not infer target bytes or words.

The WN-14 folder and physical desk-margin evidence remain the primary direct K08 witnesses. The native-mail route is complementary and could also improve K04 provenance. No equipment access, account bypass, verifier modification, or guessed credentials are involved.

**Recovery accounting is unchanged:** six components PASS; K04 and K08 remain MISSING; combined recovery remains INCOMPLETE.
