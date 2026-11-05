# K08: original email quotation/forward transport provides no surviving final-caption literal pointer

**Agent48 | 5 November 2026 ~23:19 UTC | original-export structure, no K08 recovery.** This is a targeted check of the Critic's 23:07 proposed **missing quote/forward/version boundary** rather than another subjective phrase/HMAC enumeration. Original six individual slots remain PASS, K04 and K08 MISSING, REC8 combined INCOMPLETE.

## Question and source

The [original custodian note](../resources/evidence/records-custodian.txt) says repeated quoted replies were omitted from this *trimmed* export. The source's 20 plain-text email records describe several envelope phrases: Emily's original MAIL11 rejects commissioning and standby labels, her N02/N06 are drafts, her N13 is a detailed scene, and MAIL20 stresses the final margin wording. Could a surviving email **In-Reply-To / References chain, forwarded MIME part, or quoted-body excerpt** identify the original, actually inscribed final-caption message, instead of guessing its semantics?

The complete original email-transport scope is exactly `resources/evidence/mail/01.eml` through `20.eml`, with source crosschecks against the original `evidence/mail/INDEX.md`, `evidence/records-custodian.txt`, `evidence/crew/noticeboard-and-desk-notes.txt`, `evidence/mail/11.eml` and `20.eml`. SHA256 pins in the single-file SFT include custodian `786211e7be248e6ba31f017a071e038436782b8550b863f85d77a6c32e1d640a`, desk notes `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`, MAIL11 `f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29`, MAIL20 `e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71`, and mail index `3fe9b6f14cf23d0f8f0b6ea5ed02230242aaa6b9949c0d6845b57eb8aa85659b`.

## Executed original source observations

Parse every `.eml` with Python standard-library `email.parser.BytesParser(policy.default)`, preserve source record IDs, and inspect MIME structure, reply-chain headers and quoted/forwarding body markup:

| Original export transport property | Real count |
| --- | ---: |
| Original MIME email messages | **20** |
| Multipart MIME messages | 0 |
| `Content-Disposition` or `Content-ID` headers | 0 |
| `In-Reply-To` headers | 0 |
| `References` headers | 0 |
| Body lines beginning `>` (quoted reply convention) | 0 |
| Explicit forwarded-message markers | 0 |
| Subject lines using `Re:` | **2**, MAIL06 and MAIL17 |

The only visible reply **subjects** point to technical WN-14 / valve-gallery threads, not the final envelope caption, and neither carries a machine-readable `In-Reply-To` or `References` link. MAIL11 and MAIL20 are the caption-descriptive texts. Their wording describes rejected labels and an absent final inscription; neither supplies a traceable original final email message ID, quoted final phrase, MIME attachment, or forwarding pointer. Original Emily N23 likewise explicitly refers to words in the missing physical margin without transcribing them.

A direct equivalent original-source Python pilot executed successfully and checked every reported count. The [committed read-only source-pinned SFT](../agents/agent48/k08_mail_quote_version_transport_sft.py) checks exactly these original fields and the N23 references. It uses no K08 original SHA as an oracle and generates no conjectural candidate phrase.

## Scope and decision

**The surviving 20 exported email messages carry zero explicit quote/forward/MIME version pointer to the final desk margin.** This rejects a narrow hypothesis that the missing final sentence could be recovered by following a **preserved email reply-header, forwarding body or attachment reference** in this exact local export. A `Re:` in a subject alone cannot reconstruct deleted quotations.

It **does not prove the historical email lacked those elements**: the records team produced a trimmed, redacted export, explicitly omitted repeated quotes, and warned that unmarked gaps are possible. Quoted content and original MIME headers might have existed in unavailable original mailboxes. The final caption could have been handwritten without any email literal. No original author-final word or new K08 component was authenticated.

**Useful next discriminator:** look for an independently preserved *final inscription* or an original provenance-linked revision record. Searching a different “quote restoration” grammar against the same source without an actual quote/version witness is another lexical lottery. Leave original route, nonce, evidence, acceptance, verifier and candidate unchanged.
