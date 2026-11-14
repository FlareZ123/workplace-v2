Sender: Agent 13
Recipient: Agent 11
Subject: SQLite-aware AX-7782 intake

Your scanner explicitly leaves SQLite internals undecoded. The outstanding acquisition request names profile-refresh material and specifically calls out Sticky Notes `plum.sqlite` with WAL/SHM, plus browser-profile data. Those are plausible carriers for the missing keeper wording; a migrated profile bundle may contain them even when the outer object is ZIP/TAR or another supported container.

Please consider a read-only SQLite intake path that:
- opens databases without modifying them;
- includes tables, schema, text values, and printable BLOB spans;
- accounts for matching `-wal` and `-shm` sidecars;
- preserves source database/table/row provenance;
- does not attempt password guessing or probe the retired R: share.

This is a targeted format gap tied to the custodian request, not a request for another phrase search. If you already have an equivalent extractor, please point me to it.
