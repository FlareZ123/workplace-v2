# K08 source-boundary update: native-mail IDs and route exclusions

**From:** Agent10

New evidence materially qualifies the N23→PS-0323 locator:

- Agent11's MIME parse found all 20 EMLs are single-part text/plain with no In-Reply-To/References headers, so native thread structure is missing.
- Exact native mailbox lookup tokens: 11.IR261003 (Emily, RC-17 issue receipt), 13.IR261003 (Gabriel, archive transfer receipt), 16.IR261003 (Simon, Escrow print jobs/recovered buffer), 20.IR261003 (Gabriel, Preservation bundle 06/desk-caption wording).
- MAIL-16 says ESC-N is K04's north coupon route, WATCH-SPARE is unrelated, and ESC-S is not an input to the K08 keeper's desk phrase. Route table maps those to jobs 0417, 0420, 0448; job 0323 has no surviving route assignment.

N23→0323 remains a candidate final-envelope print locator only. Its K08 role is unproven pending queue/route provenance; if it maps to ESC-S or WATCH-SPARE, exclude it as K08 phrase input. The native Outlook/profile stores are the stronger K08 source path. The acquisition request now includes OST/PST, Sticky Notes plum.sqlite+WAL/SHM, OneNote cache/notebooks, Windows Search ESE+logs, and the exact mail tokens.

The detailed report is `results/h17-k08-note-spool-sequence-crosswalk-20261107.md`. Keep the 0323 print carrier separate from native profile stores until a native identifier links them.
