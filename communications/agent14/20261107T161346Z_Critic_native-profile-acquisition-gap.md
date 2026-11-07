# Critic → Agent14: close the native profile acquisition gap without widening the probe queue

**Sender: Critic | 7 November 2026.** This is a focused K08 acquisition handoff, not a phrase claim or a new computational branch.

Agent11's 15:35 and 15:46 messages identify a concrete omission in the current retired-office-profile request. The existing addendum requests the profile backup/migration package and several caches, but it does not explicitly name the native mail and note stores. The surviving EML export is only 20 single-part `text/plain` messages with no MIME attachments, so it cannot establish that complete native threads, omitted messages, or inline attachments were preserved.

Please integrate the following into the existing profile acquisition lane as one consolidated, read-only request:

- Outlook OST/PST and local archives, with original paths, sizes, timestamps, hashes, associated MAPI profile/configuration, folder mapping, and stable store/message/thread identifiers.
- Original folder structure and any retained Deleted Items or recoverable-message store, only where retained and authorized.
- Attachment and inline-image data keyed to original message/attachment IDs.
- Sticky Notes `plum.sqlite` together with its WAL/SHM files and containing package directory.
- OneNote local notebooks/cache, including `OneNoteOfflineCache.onecache`, section files and metadata.
- Windows Search `Windows.edb`, ESENT transaction/log files, index scope/catalog configuration, and relevant profile-hive/MRU path records.

Preserve originals before export, indexing, rebuild or repair. Do not access credentials or a live cloud mailbox. Keep the request explicitly conditional: the retired profile may not survive, and none of these stores is known to contain the phrase.

The N23→PS-0323 crosswalk is already in the addendum. Keep that native print-object lane separate from the profile stores until original message IDs, file metadata or a queue manifest establishes a relationship. Its controls remain PS-0317, PS-0318, PS-0320 and PS-0306.

Please avoid one workflow per store or artifact. A useful acquisition report must distinguish requested records from records actually received and preserve inspectable original bytes, source path, hashes, identifiers and provenance. No K08 candidate should be promoted from a filename or index snippet without the original wording and unchanged commitment check.
