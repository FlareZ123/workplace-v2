# Agent 15 memory

## Current incarnation

- Claimed identity agent15 at 2026-11-07T07:42:17Z (see `.lease.json`). Do not refresh the lease. At the latest checkpoint, elapsed age was about 41 minutes, below the 70-minute release threshold.
- Focused on new K08 book/locator evidence and on checking whether the missing K04 source could be recovered from repository history.

## Durable findings

### WN-14 suffix may be a page/word locator

- `resources/evidence/mail/06.eml` says David's standby WN-14 transcription has group D ending `5E67`, and that it “might help identify the book.” It explicitly distinguishes this standby transcription from the signed duty register. Do not substitute the standby value for the signed WN-14 groups or HMAC key.
- Hypothesis: split the hex suffix into bytes: `0x5E = 94`, `0x67 = 103`. This could mean printed page 94, word 103 in the map-bearing book.
- This is strengthened by ST-094 in the L-29/N ticket set and by the 1947 third edition of Robert Lloyd Praeger's *The Way That I Went*: the N ticket pages 81, 94, 99, 106, 112 all fall in *The Volcanic North* (starting p.62), while S pages 121, 130, 135, 142, 151 fall after the *Silurian Region* boundary at p.118. The 1997/1937 pagination has a different boundary, so the exact edition matters.
- This is only a hypothesis. MAIL-06 does not define a byte split or word-index convention. No page94/word103 token has been read from a physical scan.
- Agent35 previously tested `0x5E67 = 24,167` as one raw word offset in *The Riddle of the Sands* and found no HMAC match. That is a different interpretation and does not falsify page94/word103.
- The 1937 first edition of Praeger has a large folding map at rear, 394 pages; the 1947 third edition is 416 pages. NLI's 1997 reprint (originally 1937) is offsite. Google Books only exposed snippet view for the 1947 edition.
- A W. Eric Wilson 1934 guide to the Thames Estuary and Norfolk Broads is a weaker alternative by physical profile (yachtsmen's estuary guide, cloth, frontispiece, folding charts). No evidence confirms the 'Lieut. X--, R.N.' or 'Dollmann' details. Agent22 and Agent35 were told to treat it as an analogue, not an identification. Agent35's current crosswalk gives it a stronger physical-profile fit but keeps the Praeger page-set evidence distinct.
- Research note committed: `results/h17-k08-wN14-5e67-page-word-locator-20261107.md`.
- Messages sent to agents 22, 23, and 35 under `communications/agent{22,23,35}/20261107T0812*` and `20261107T0817*`. Read their replies before repeating this work.

### Physical K08 evidence locations

- `resources/evidence/mail/09.eml`: David's map-back book is in the TV room; a tea receipt is left inside as a bookmark.
- `resources/evidence/mail/14.eml`: Emily's desk notes are under the WN-14 folder, outside the controlled-copy sleeve; the folder was to be handed to the incoming watch after dinner.
- `resources/evidence/mail/23.eml` says final wording was in the margin beside a photograph and copied to the envelope. The local `noticeboard-and-desk-notes.txt` only has drafts/motif notes, not the final handwritten wording.
- Highest-value physical test: identify exact book/edition; photograph title and edition pages, map, p.94, word 103, ticket pages, margins, and receipt in place. Also retrieve the original WN-14 folder and loose desk notes. Preserve page layout and word-count convention.
- The current `results/h17-missing-evidence-request.md` already identifies the original desk notes, book/receipt, paper key register, and AX-7782 object as missing evidence. Avoid duplicating that general request.

### K04 and repository retrieval checks

- Tested CPython `random.Random` seeds made from N/S ticket page-number serializations, `5E67`, page94/word103, and book-title strings against all 132 known spool payloads at the established STARTS offsets. No full or meaningful byte matches.
- Also tested the same seed family as direct 16-byte outputs and XOR-mask outputs against the K04 SHA-256 commitment. No matches. Do not repeat these exact seed serializations.
- GitHub repository has only `main`, no tags or releases. Initial commit includes the supplied resources but no AX-7782 retained object. No PR-triggered workflow runs were found for the initial or current head commits. The missing object is not recoverable from a hidden branch/tag/release or those CI runs.
- No useful new inference came from trying to align node50 timestamps with the p951 stream: timestamp offsets are 0..399, and seq44 does not match `randrange(400)` at the adjacent candidate stages. The four-field metadata model also does not generalize to all records. Agent6's memory already covers the broader failure; do not retread.

### New book-candidate synthesis (2026-11-07 08:40Z)

- Cowper Sailing Tours Part I now has a particularly strong physical fingerprint: the PBFA listing for the 1892 red-cloth copy states that a previous owner's name is on the reverse of the frontispiece map. This parallels the Riddle of the Sands clue about a name on the back of the map. The actual name is not disclosed, so do not claim it is Dollmann.
- Cowper remains the strongest explanation for the L-29/N/S ticket-page crosswalk: N pages 81, 94, 99, 106, 112 fit Part I (168 pages); S pages 121, 130, 135, 142, 151 fit Part II (365 pages). The Riddle novel names the series, and PBO documents Childers's personal connection with Cowper.
- Ransome's We Didn't Mean to Go to Sea (1949 impression) is a strong alternate physical/map-back and N20 scene analogue. P.94 matches the all-night/sea/table scene, but body word 103 is 'shelf' (or 'took' with the heading) and printed-text HMAC searches found no phrase. Keep it separate from the Cowper ticket crosswalk.
- T.G. Cuthell's 1893 Sailing Guide to the Solent and Poole Harbour is a small guidebook analogue to the fictional Riddle prop, but its listed extent is about 100 pages plus ads, so it cannot explain S ticket pages 121-151 as one book.
- The 1985 Cowper facsimile record is a reprint of the 1909 third edition of a single part (Part II, 336 pages), not a combined five-volume edition. Keep Part I and Part II edition/pagination distinct.
- Agent2 asked for the Cowper Part I HathiTrust ID. I do not have the ID, OCLC number, or direct babel.hathitrust.org URL. Online Books Page lists HathiTrust page images but its browse page times out; HathiTrust catalog search did not surface an indexed record. Replied to Agent2 with this status and the PBFA map-verso detail.
- Broadcast sent: communications/broadcast/20261107T083933Z_agent15-cowper-ransome-candidate-separation.md. Direct updates sent to agents 22, 23, 35, and 2. Shared synthesis updated at results/h17-k08-wN14-5e67-page-word-locator-20261107.md.
### Final synthesis checkpoint

- Updated the K08 row in results/README.md to distinguish Cowper's ticket-page/map-verso evidence from Ransome's rear-map/N20 scene evidence. Commit 4408cafea0651ee2562797be07696b730b137acc.
- Sent Cowper map-verso evidence to agents 22, 23 and 35; sent HathiTrust-ID status to agent2; broadcast candidate separation to the whole swarm.
- No HathiTrust volume ID, OCLC number, or page scan was found despite targeted Online Books Page, HathiTrust, WorldCat, NLA, BL and Stanford catalogue searches. Do not repeat broad catalogue sweeps without a new identifier.
- User-facing next evidence request should prioritize the actual Cowper Part I/II copy, Part I map verso owner inscription, p.94 full page/margin, receipt bookmark, and Emily's WN-14 notes/envelope. Keep Ransome as a distinct alternative until the physical copy is inspected.
## Next high-value actions

1. Incorporate any replies from agents 22/23/35 on the page94/word103 interpretation and physical-book candidate.
2. If a physical scan or OCR becomes available, test word 103 on p.94 first, then the N ticket pages in source order; use S pages as a control. Do not infer the phrase before confirming edition and tokenization.
3. Prioritize the original WN-14 folder/desk notes and the actual receipt/book over further generic literary searches.
4. For K04, the highest-value missing evidence remains the original AX-7782 retained object or source-side print-host/SPL data. The current repo/history contains no copy.
