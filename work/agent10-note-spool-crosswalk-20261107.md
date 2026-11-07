# Agent10 work log: K08 note-to-spool crosswalk (7 November 2026)

## Inputs and scope

Used the supplied 46-member H-17 archive, specifically:

- `evidence/crew/noticeboard-and-desk-notes.txt`
- `evidence/print/spool-reconstruction.log`
- `evidence/records-custodian.txt`
- `evidence/mail/11.eml` and `evidence/mail/20.eml`

This was a historical-records investigation only. No equipment or facility systems were accessed.

## Structural test

Parsed all note IDs and spool rows. For each N01–N24, tested the fixed source-derived candidate mapping to `PS-261003-(0300 + N)`.

Observed:
- 24 notes and 24 corresponding jobs, all unique.
- All mapped jobs are ATTEMPT=1 / STATE=ACK.
- Their timestamps are exactly 300 seconds apart, 07:05–09:00 UTC on 3 October.
- Job 0300 is a separate 07:00 UTC prelude.
- The eight Emily notes map to 0302, 0306, 0310, 0313, 0317, 0318, 0320 and 0323.

K08-relevant segment:
- N17 standby envelope label → 0317, LABEL/store.
- N18 commissioning envelope label → 0318, RECOVER/store.
- N20 semantic line brief → 0320, RECOVER/bench.
- N23 final-margin/envelope note → 0323, RECOVER/store.
- N06 second desk draft → 0306, RECOVER/desk.

The most useful locator is PS-261003-0323, because N23 explicitly describes the final words on the envelope. This is a structural association, not an authenticated note-to-job foreign key.

## Bounded payload checks

The paired note text was checked against direct raw/normalized digest identities (MD5, SHA-1, SHA-256, BLAKE2s), tested HMAC identities under the available nonce/mask/component keys, and selected text encodings. No direct identity was found.

Additional exploratory checks did not decode the payloads: common XOR-pad and hash-chain relationships, a CPython stream seeded by the 0300 prelude, a GF(2) LFSR fitted on early blocks and held out on later blocks, AES-ECB/CTR with available keys and job-derived IVs, and BIP39 mnemonics of Emily's paired job payloads. These are bounded negative tests, not proof of randomness or proof that the records are unrelated. Do not repeat the same parameter families without a new source basis.

A further source-defined extraction test used the four bench-destination notes N01/N08/N14/N20. It searched 8,144,124 ordered combinations of 1–4-word contiguous spans per note (7–12 words total) under the K08 HMAC commitment. No hit. This excludes that exact four-note grammar only.

## Interpretation

The exact numbering and temporal alignment is strong enough to prioritize the paired original print objects. N23→0323 is the best K08 candidate final-envelope output. N20→0320 is the preceding semantic brief. N17 and N18 are explicit standby/commissioning controls. The spool log says its 16-byte payloads are retained fragments with unverified integrity, and the custodian says ACK proves receipt only. Do not claim that the 0323 payload is the phrase or a verified K08 component.

## Preserved artifacts and next actions

- Human-readable result: `results/h17-k08-note-spool-sequence-crosswalk-20261107.md`
- Research map: `results/README.md`
- Existing acquisition request narrowed with job IDs: `results/h17-missing-evidence-request.md`
- Reproducer: `work/note_spool_crosswalk_sft.py`

Next useful evidence is the complete native and rendered output for PS-261003-0323, with 0317/0318/0320/0306 as controls, plus the native queue/job manifest that authenticates the mapping. Integrate this into the existing Bundle 06/K08 acquisition scope. The 21 October custodian channel remains closed.


## Additional bounded source-grammar checks

- The four bench-destination/photo/brief notes N01/N08/N14/N20 were searched as ordered concatenations of contiguous 1–4-word spans, with total phrase lengths 7–12 words: 8,144,124 candidates, no K08 commitment hit.
- The eight Emily-note final words were searched across all 40,320 permutations, then with one inserted word from a 28-word source-semantic/function-word list at all nine positions: 10,160,640 additional candidates, no hit. For N20, the semantic brief's first sentence ends at "table"; the following instruction about the shorter standby label is not treated as phrase text.
- The repeated cross-component metadata pair was noted: N20→PS-261003-0320 and selected K04 PS-261003-0417 are both RECOVER/bench. This is a queue/destination hypothesis only; no physical-location or K04/K08 linkage is established.
- Verified the SFT against three layouts: repository-style extracted `resources/evidence/` (default), the extracted archive directory, and the original ZIP. Each run returned 24 notes, 24 jobs, and 300-second intervals.


## Queue/device mapping constraint

Read `evidence/transfers/queue-note.txt` and the print-fleet return register. The queue note says queue names are physical print destinations, and handoff proves queue acceptance rather than paper collection. The fleet register maps only 0417→ESC-N/FA-17, 0448→ESC-S/LV-42, and 0420→WATCH-SPARE/ST-09. It does not map 0323. The spool rows for 0417, 0448 and 0420 have different or changing DEST values, so do not infer a device for 0323 from DEST=store or from the shared RECOVER class. Original queue/job manifest is the missing join.
