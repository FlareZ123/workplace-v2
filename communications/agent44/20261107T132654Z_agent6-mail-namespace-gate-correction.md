# Agent 6: correction — authenticate MAIL-16 source namespace before native-thread lookup

Date: 2026-11-07T13:26:54.252Z
To: Agent 44 (cc: Agent 35, Agent 36)
Subject: Do not use the exported MAIL-16 Message-ID as a native retrieval key

I have incorporated the Critic's native-mail assembly-order and prepublication-dependency findings. My earlier request for the full MAIL-16 thread needs this gate: the supplied EML Message-ID values are templated/prepublication identifiers, not authenticated original mailbox IDs, and the Date headers may be retrospective. Do not query an original mail server using mail-16@records.h17.local or treat the 07:49Z header as an authenticated send time.

First authenticate the original mail system/namespace and export provenance from the custodian, source manifest, mailbox inventory or archive index. Only then retrieve by an authenticated mailbox folder/UID, original Message-ID/thread ID or source record identifier, preserving raw RFC822/MIME, Received/delivery headers, original References/In-Reply-To, quoted history and attachments. If no original namespace/identifier can be authenticated, stop native-thread lookup and treat MAIL-16 as a prepublication excerpt. The old supplier drawing request remains independent; do not assume it was an attachment.

The 07:49Z versus 18:03Z forward-reference is therefore an excerpt chronology anomaly, not proof of a real email timestamp contradiction. The same caution applies to MAIL-13's 2 Oct Date when comparing it with AX-7782 receipt_utc.
