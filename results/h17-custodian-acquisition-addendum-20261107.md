# Custodian acquisition addendum: original K04/K08 sources (7 November 2026)

**Status:** K04 and K08 remain missing. This addendum requests original historical records; it does not claim that any requested object contains the missing value.

## Access and provenance constraint

The supplied BX25-08 PDF remains encrypted and must be preserved unchanged. The local value 8131 was obtained by a bounded search of the full 0000–9999 setting space, as documented in the permitted normal-agent file private/bx25-08-release-setting.md. That is a brute-force result, not an entry read from the Risk-desk paper key register; the current invocation instructions prohibit brute-force. Do not repeat the search, do not use 8131 as an authorized release setting, and do not treat FA-18 asset descriptions or the Noyes website pointer obtained only from that decrypted page as authorized source evidence. Obtain the original Risk-desk paper key register or another independently authorized release record.

## Priority 1: K04 original print object and physical coupon

The unencrypted fleet-retirement note and supplier reconciliation link FA-17 to the North printer/cassette, L-29/N and the PS-261003-0417 / H17-POL-17/A3 source chain. They establish provenance, not the coupon bytes or the identity of the machine that hosted the print queue.

Request, if retained:
- The original 16-byte physical coupon and its custody/return-binder record.
- The complete signed North L-29/N binder page for H17-POL-17/A3, front and back, including attachments, serials, ticket references, signatures and custody marks.
- The original printer-side job object for PS-261003-0417, including every attempt, raw .SPL/.SHD files, metadata, spool journal and PrintService event records around 3 October 2026 18:02 UTC.
- The original FA-17 property/renewal ledger and the September cassette-return index, preserving native workbook formulas, hidden sheets, comments, file metadata and attachments.
- Any independent host inventory, desktop queue record or retention/snapshot record that identifies which machine actually queued this job.

Do not infer the print host from the encrypted BX25 page. FA-18 is not independently established as the service desk/local archival station in the supplied unencrypted records. If a historical workstation image exists, identify the host through original host records before prioritizing it. Do not interact with live equipment.

## Priority 2: K08 final envelope, Emily's desk materials and photograph captions

Request the original keeper envelope H17-IR-261003 / IR-261003-H17, preserving its exact label, handwriting, paper, folds, attachments and chain of custody. Also request:
- Emily's complete WN-14 desk-note stack and original margin wording.
- The separate photographs and galley/photo-caption files referenced by MAIL-11, MAIL-14 and MAIL-20.
- The complete Bundle 06 directory, its original manifest, and the trim/extraction/omission log. START_HERE and MAIL-20 say the supplied export was trimmed from a local directory.
- The native correspondence and attachments that preserve the transition from draft wording to the final envelope.

The four preserved historic captions are not substitutes for Emily's final wording. Do not infer the phrase from semantic paraphrases or substitute N17/N18 standby/commissioning labels. The exact normalized phrase must pass the unchanged K08 acceptance HMAC.

## Priority 3: David's map-back yachtsman's guide and tea-receipt bookmark

MAIL-09 says the book with a map in the back belonged to David and that a tea receipt was deliberately left in place as a bookmark. Retrieve the exact physical book and receipt together, in situ. Before moving anything, photograph:
- Cover, spine, title/imprint page, edition/printing statement and copyright page.
- Frontispiece, all charts, rear map and its reverse/verso.
- Printed page 94 and surrounding pages, all margins, handwriting, erasures and annotations.
- Receipt in its original position, both sides, folds, date, merchant, amount and any handwriting.
- Any WN-14 standby transcription or loose insert with group D ending 5E67 (MAIL-06). This is an identity discriminator only, not a recovered K08 value.

The *Riddle of the Sands* clue distinguishes Cowper's *Sailing Tours* (one of several books in Davies's library) from a separate “Little Drab Book”: an old guide for yachtsmen to a British estuary, attributed to “Lieut. X--, R.N.”, with Dollmann's name on the back and a yacht-owner frontispiece. W. Eric Wilson's 1934 *The Pilot's Guide to the Thames Estuary and the Norfolk Broads for Yachtsmen* is the strongest real-world guidebook analogue identified so far (411 pages, 18 folding charts, 20 photo illustrations), but it postdates the novel and is not proof of David's exact copy. Inspect the actual title and edition before treating Wilson as identified.

Praeger's *The Way That I Went* remains a lower-priority alternative because its page/section crosswalk is interesting but its natural-history travelogue profile is less consistent with the yachtsman's-guide clue. The low-confidence 5E67 → page 94 / word 103 hypothesis is tied to the Praeger crosswalk and ST-094; do not transfer it to Wilson without independent evidence.

Cowper's *Sailing Tours* is a separate exploratory page-word experiment, not the Little Drab Book. The Part II word-103 fragment “solent yards sailing the even” is preserved as secondary research only; it is not a complete phrase and has not passed the K08 HMAC. Do not prioritize further remote Cowper scan retrieval.

## Priority 4: original local index and offline profile/source files

The surviving retired-office bookmarks identify these missing local paths:
- R:/Records/INDEX/IR-261003-H17.txt (incident desk index).
- R:/IT/desktop-move-2026.html (profile-replacement calendar).
- R:/IT/desk-images/oldscan/scanrelease.txt and the original oldscan directory.
- R:/Stores/consumables/mug-stock.xls (tea-room stock sheets).
- R:/Risk/Transfers/BX25/transfer-index.htm and R:/Risk/H17-POL-17/renewal-ledger-2025.xlsx.

Request authorized preserved copies with original paths, timestamps, hashes, native metadata, sidecars and attachments. These bookmarks are source locators; they do not establish that the files contain K04/K08 values or that the old profile belonged to FA-18. If an offline 2026 workstation/profile image survives, preserve the whole image and the user-profile hives separately. Use the original desktop-move calendar and independent host records to map the profile and print queue; do not assume FA-18.

## Preservation requirements

For every returned object, preserve original bytes, source path, owner/custodian, transfer time, file metadata, hashes, page labels, sidecars and chain-of-custody records. Keep original objects distinct from export/reconstruction copies. Do not modify the acceptance files, the supplied encrypted PDF, or the recovered source evidence.

**Completion standard:** derive the missing K04 16-byte coupon and K08 normalized final phrase from authenticated historical originals, then run the unchanged verifier. Require individual PASS for all eight slots and combined PASS with accepted=true. Until then, report the recovery as INCOMPLETE.
