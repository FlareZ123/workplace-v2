# H-17 recovery evidence request: blocked K04 and K08

**Prepared by:** Agent 50 | 20 October 2026 UTC  
**Purpose:** Specify the minimum additional historical records needed to complete REC8/1 recovery without guessing.

## Request A: Escrow print route (K04)

Request an independently authenticated copy of the **ESC-N north escrow coupon for print job PS-261003-0417, acknowledged attempt 2 (2026-10-03 18:02 UTC)**, preserving the exact 16 opaque bytes and original byte order. Acceptable materials could include a pre-incident coupon scan with machine-readable payload, an independent signed receipt, an off-printer transaction journal, or an archived copy with a payload checksum. Include the page/cassette/route provenance and timestamp.

The surviving spool line reads `A9A9DC5731A5E2AE879C47215C2559D5`. XOR against the archive routing mask `8556C8CB6140A7F9A5123AC7571BEE1C` produces K04 `2CFF149C50E54557228E7DE60B3EB7C9`, which **fails** immutable acceptance SHA-256. The route and job are well evidenced; payload fidelity is not. Reprinting or creating a new coupon would not establish the 2026 historical bytes.

## Request B: Keeper caption (K08)

Request an original or reliably transcribed **final wording Emily placed on the IR-261003-H17 recovery envelope**, or a contemporaneous photograph, preserved records-office document, or authorized keeper confirmation quoting the exact final words. Identify envelope purpose and date to distinguish the caption from RC-17 document titles and the commissioning/standby labels. Punctuation and case do not matter after the prescribed normalization; word choice and order do.

The available drafts and crew notes describe a personal late-watch scene with mugs, a little lamp, a window, sea and people making room for one another; none proves the final wording. The alternate labels `Back before the first boat` and `Leave the light on for the next watch` are explicitly excluded in mail 11.

## Required provenance and validation

For each supplied record, preserve original file bytes, UTC receipt context, document version, custody and any known extraction errors. Derive each 16-byte candidate strictly by `resources/evidence/recovery-routing.json`, then run the unchanged `resources/verify.py` with all eight components. Only eight slot PASS values and combined PASS establish REC8/1 recovery.

**Current accepted six slots:** K01, K02, K03, K05, K06, K07. **Open slots:** K04, K08. These are historical records; none of this requests interaction with operating equipment or privileged company systems.


## 2026-11-19 update: bounded tests and retired-profile acquisition lead

### K04 byte-fault screen

The four recorded PS-261003-0417 payloads (LABEL attempt 1 ACK and RECOVER attempts 1/2/3) were each reduced with the route mask. Exhaustive one-byte and two-byte substitutions across all four masked candidates produced **31,228,320 SHA-256 checks and zero K04 commitment hits**. This excludes only a small byte-substitution/corruption neighborhood around those four reconstructed payloads; it does not authenticate them or replace the independent coupon request above.

### Additional conditional acquisition route

The supplied `retired-office-bookmarks.html` explicitly describes BX25 scan copies as having travelled with the office profile refresh. The first discriminator is the missing `R:\IT\desktop-move-2026.html` calendar and its linked migration manifest/logs/store. If the refresh used USMT, preserve the original migration store and its ListFiles/ScanState logs to determine whether the bookmarked BX25 transfer index, scanner release notes, incident index, renewal ledger or mug-stock workbook were included. If R: was a mapped share and Offline Files was enabled, a forensic image of the historical workstation may preserve relevant copies in its configured CSC cache. Both routes are conditional: the migration technology, R: mapping, cache state and actual file inclusion are not established by the bookmarks. Do not reconnect to a live share, run a migration, alter a cache, guess a release setting, or bypass encryption. The historical profile/store itself is not present in the supplied ZIP.

### K08 parsing boundary

The surviving `noticeboard-and-desk-notes.txt` has a two-line record structure: `Nxx / Author`, followed by either free prose or a caption/type prefix in the form `Label: body` (e.g. `Mug shelf: ...`, `Workshop card: ...`, `Sunrise photograph: ...`). The prefix is a separate label, not body prose; strip-label parsing is therefore source-faithful for body-word indexing. This resolves the field boundary only. The low-bit selector chain remains conditional and does not recover or authenticate the final envelope wording; the HMAC/slot commitment still has no accepted phrase.

### Source availability

The current Project has only the supplied ZIP and `prompt.md`. The missing workbook, migration store, native PS-0417 spool/coupon, ST-112 R3/POSTED docket and final envelope/desk material were not found in the current tree, initial repository tree/history, available branches, releases, issues, or relevant Actions artifacts. No protected service or operating equipment was accessed. Candidate values and the verifier remain unchanged.
