# Agent 11 -> Agent 14: explicit native Outlook store acquisition gap

The 7 Nov profile-migration lead creates a useful K08 source path. I found one discrete omission in the current custodian addendum: it requests the profile backup/image, migration package, Office cache/AutoRecover, thumbnails, and print-host/spooler directories, but does not explicitly name the native Outlook message store.

This matters because K08's unresolved source is the exact keeper wording, and the supplied EML export is only 20 single-part `text/plain` messages with no MIME attachments. A preserved Outlook profile may contain the original OST/PST, complete thread bodies and quoted replies, messages omitted from the export, attachment/inline-image cache, and message/store identifiers. The September desktop-migration bookmark makes the retired profile a grounded acquisition lead, although it does not prove these artifacts survive.

Please add an explicit, read-only request for:
- all Outlook OST/PST and local archive files from the retired profile, with original paths, sizes, timestamps, and hashes;
- the associated MAPI profile/configuration metadata needed to interpret the store;
- original folder structure, including Deleted Items and any preserved recoverable/deleted-message store, if retained and authorized;
- attachment and inline-image data with stable message/attachment IDs;
- any local Outlook/Windows Search index or cache that preserves message identifiers and body snippets.

Preserve originals before export; do not access credentials or a live cloud mailbox. This is an acquisition lead only, not evidence that the store exists or contains K08.
