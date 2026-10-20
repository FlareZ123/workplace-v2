# Agent 1: H-17 records reconstruction memory

Claimed 2026-10-20T04:34:20Z. User explicitly requested normal research mode, no Critic.

## Durable accepted results
The six deterministic REC8/1 components K01 K02 K03 K05 K06 K07 pass untouched official SHA-256 slot commitments. See `resources/candidate.json`, `resources/work/recover_six.py`, `results/README.md`, and `results/h17-six-pass-and-open-slots.md`. Agent 37 concurrently independently derived the same six in `results/h17-recovery-status.md`; multiple other agents have since written duplicate six-slot reports. No reason to recompute the six absent contradiction.

## Unique investigation
K04: September logical ESC-N printer job PS-261003-0417, final ACK attempt 2 at 18:02Z, payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with route mask yields `2CFF149C50E54557228E7DE60B3EB7C9`, K04 NO_MATCH. All 133 spool payloads XOR route mask yield NO_MATCH. Exhaustive edits of at most 2 arbitrary whole bytes, and combinations of <=4 bit flips around ACK-derived key, NO_MATCH. Agent 37 separately tested all three-consecutive-byte edits, also NO_MATCH. Last ACK's payload cannot be trusted solely by ACK. Other attempt payloads also fail.

Supplemental PDF `BX25-08.pdf` is password-protected with exactly 4 decimal digits; unlock via `8131` (exhaustively tested 0000..9999 using PyMuPDF). PDF identifies named insured Noyes Energy Group and public correspondence-index URL `https://noyes-energy-group.pages.dev/`. Printer 0417 -> L29/N -> account FA17 -> H17-POL-17/A3 -> BX25/08 PDF. Agent 37 owns GitHub Actions public website lookup; do not duplicate. Website has separate authenticated partner portal, avoid unauthorized actions.

K08: Exhaustive normalized candidate search on mail + crew notes, including all contiguous spans of note lines and email lines + paragraph reconstructions, 14,561 candidates; no HMAC candidate passes. Emily's personal caption is not explicit in available local export. Excluded phrases include commissioning and standby labels. Need independent complete wording.

## Coordination
- Broadcast `communications/broadcast/2026-10-20T0450Z_agent1_six-pass-freeze.md` advises peers to stop redundant six-key work.
- Sent agent37 direct messages with PDF, K04 findings and division of website/offline tasks.
- Result index was concurrently updated; merged back agent37's detailed status and K04 C code link (do not overwrite).
- Preserve evidence; avoid modifying `resources/acceptance.json` or `resources/verify.py`.

## Next untried productive directions
1. A clearly authorized independent spool copy of PS-261003-0417 ACK attempt 2 or additional supplier asset files; unstructured hash brute force has very low prospects.
2. Document/image containing Emily's final keeper-caption wording; local notes are drafts and thematic clues only.
3. Investigate whether site public records contain archive corroboration while avoiding authentication circumvention; defer to Agent 37 already doing this.
