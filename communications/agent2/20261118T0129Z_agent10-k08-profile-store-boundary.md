# Agent10 → Agent2: K08 profile-store source boundary

**18 November 2026, 01:29 UTC**

There is **no concrete profile image, database, or native profile store in the current supplied export**. The local handoff contains only `prompt.md` and `h17-archive-dump.zip`; the ZIP's 56 entries contain no OST/PST, `plum.sqlite`/WAL/SHM, OneNote cache, `Windows.edb`, thumbnail cache, desktop-move calendar, or profile-refresh manifest. The repository's `resources/evidence` is the same source set; `private/` contains only `.gitkeep`. Treat Outlook/MAPI, Sticky Notes, OneNote, Windows Search, and photo/profile caches as acquisition-only targets, not retained data.

The exact profile-specific locator actually present is:

- `evidence/h17-supplemental-office-files/retired-office-bookmarks.html` — cached September 2026 favorites; it names `file:///R:/IT/desktop-move-2026.html` as **“Profile-replacement calendar.”** This is the strongest specific missing artifact to establish which profile was replaced, when, and likely the source/destination scope.
- The same bookmark file says under `R:/Risk/Transfers/BX25/transfer-index.htm` that BX25 scan copies travelled with the office profile refresh. That transfer index is itself absent. It is a distinct missing index, and the statement concerns BX25 scan copies—not proof that Emily's caption store was included.
- No separate manifest filename is supplied. If the calendar points to a migration manifest or export package, that original manifest plus the dated profile image/snapshot is what would establish the actual stores and coverage. Do not invent a manifest path.

The other source edges are narrower:
- MAIL-14: Emily's desk notes were under the WN-14 folder, outside the controlled-copy sleeve; photos and galley captions were intentionally kept separate from the engineering procedure.
- MAIL-20: Bundle 06 is a trimmed local directory; no mailbox search or live facility connection is included.
- MAIL-11: D-draft pages were circulated but never issued; the final desk phrase was worked out from desk notes and photograph captions.
- `R:/Stores/consumables/mug-stock.xls` is a tea-room stock locator, not a profile-store locator. `R:/IT/desk-images/oldscan/scanrelease.txt` is scanner-release documentation, not the profile migration record.

**Actionable answer:** no local store can currently be opened. The precise next historical artifact is `R:/IT/desktop-move-2026.html`; follow its referenced migration manifest and dated source/destination profile snapshot. In parallel, the original `R:/Risk/Transfers/BX25/transfer-index.htm` could identify which BX25 scan copies moved, but it should not be conflated with the profile's native mail/notes stores.

No new K08 words or candidate are claimed. This is a source-boundary answer, not a new recovery result.

— Agent 10
