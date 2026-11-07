# K08 note-to-spool sequence crosswalk

**Status:** new structural association; no K08 words or archive-component bytes recovered.

## Question

Do the numbered crew notes have a source-visible association with the printer reconstruction sequence, and can that association identify a more precise original carrier for Emily's final envelope wording?

## Method

Parsed the two original files in the supplied archive:

- `evidence/crew/noticeboard-and-desk-notes.txt`
- `evidence/print/spool-reconstruction.log`

For each note N01–N24, tested the fixed mapping `PS-261003-(0300 + note number)`. Then checked uniqueness, attempt/state, and timestamp spacing. The complete check is reproducible with [the SFT](../work/note_spool_crosswalk_sft.py).

## Finding

The mapping is exact for all 24 notes:

- 24/24 note IDs N01–N24 exist.
- 24/24 corresponding job suffixes 0301–0324 exist exactly once.
- Every corresponding spool row is `ATTEMPT=1 STATE=ACK`.
- Timestamps run from 2026-10-03 07:05 UTC through 09:00 UTC at exactly 300-second intervals.
- Job 0300 is a separate 07:00 UTC prelude with no N00 note.

| Note | Author | Printer job | UTC | Class | Dest |
|---|---|---|---|---|---|
| N01 | Jason | 0301 | 07:05 | STORES | bench |
| N02 | Emily | 0302 | 07:10 | STORES | store |
| N03 | Zoey | 0303 | 07:15 | RECOVER | desk |
| N04 | David | 0304 | 07:20 | LABEL | store |
| N05 | Gabriel | 0305 | 07:25 | LABEL | store |
| N06 | Emily | 0306 | 07:30 | RECOVER | desk |
| N07 | Simon | 0307 | 07:35 | RECOVER | bench |
| N08 | Jason | 0308 | 07:40 | LABEL | bench |
| N09 | Zoey | 0309 | 07:45 | STORES | store |
| N10 | Emily | 0310 | 07:50 | STORES | store |
| N11 | David | 0311 | 07:55 | STORES | desk |
| N12 | Simon | 0312 | 08:00 | STORES | store |
| N13 | Emily | 0313 | 08:05 | STORES | store |
| N14 | Gabriel | 0314 | 08:10 | STORES | bench |
| N15 | Jason | 0315 | 08:15 | LABEL | bench |
| N16 | Zoey | 0316 | 08:20 | STORES | desk |
| N17 | Emily | 0317 | 08:25 | LABEL | store |
| N18 | Emily | 0318 | 08:30 | RECOVER | store |
| N19 | David | 0319 | 08:35 | RECOVER | desk |
| N20 | Emily | 0320 | 08:40 | RECOVER | bench |
| N21 | Zoey | 0321 | 08:45 | LABEL | bench |
| N22 | Simon | 0322 | 08:50 | LABEL | bench |
| N23 | Emily | 0323 | 08:55 | RECOVER | store |
| N24 | Gabriel | 0324 | 09:00 | LABEL | store |

The most useful K08 segment is:

| Note | Textual role | Matched job | Payload (16 bytes) |
|---|---|---|---|
| N06 | Emily's second desk draft | 0306 / RECOVER / desk | `06C460D95B853F7A348FFC454B715B6E` |
| N17 | standby envelope label | 0317 / LABEL / store | `5810C1B8C019ECCEFD4C989F711EF326` |
| N18 | commissioning envelope label | 0318 / RECOVER / store | `42D3EB66AF15924DF12166B6CD415819` |
| N20 | Emily's semantic line brief; explicitly says not to reuse the shorter standby label | 0320 / RECOVER / bench | `9B9D8D85D48AF325FF55556CE0AE7BF3` |
| N23 | Emily's final-margin/envelope note | 0323 / RECOVER / store | `1E51EFD2E5CA8F4E1FC8B49297B3D74F` |

N23 says the envelope remembers the words Emily finally put on it. Its matched job 0323 is a `RECOVER` row with `DEST=store`. N20's preceding line brief maps to job 0320, a `RECOVER` row with `DEST=bench`. N17 and N18 provide the explicit standby and commissioning controls. This makes **PS-261003-0323 the highest-value candidate final-envelope print record** in this sequence, with 0317, 0318, 0320 and 0306 as controls.


Source line anchors for the K08 segment:

| Note | Notes file line | Spool log line |
|---|---:|---:|
| N06 | 19 | 8 |
| N17 | 52 | 19 |
| N18 | 55 | 20 |
| N20 | 61 | 22 |
| N23 | 70 | 25 |

MAIL-20 also asks that the envelope label be preserved exactly as printed. That makes the original rendered output a materially stronger authority for the wording than a paraphrase or reconstruction from the semantic brief.

## What this does and does not establish

**Directly observed:** the exact 24-entry numbering and time alignment above.

**Inference:** the note/job pairs likely belong to one ordered print-and-notes sequence. The semantic correspondence of N17/N18/N20/N23 with the class/destination fields makes the N23→0323 association particularly worth following.

**Not established:** no retained source field explicitly states that Nxx maps to job 0300+N. The `DEST` values have not been independently tied to physical locations. A spool ACK establishes receipt of a job, not correctness of the reconstructed payload. The log header calls the entries retained fragments and says payload integrity is unverified. The 16-byte value for job 0323 is therefore a locator/token, not the recovered phrase or a verified K08 component.

A bounded comparison of the paired note text against common raw/normalized MD5, SHA-1, SHA-256 and BLAKE2s digests, plus HMACs under the available nonce/mask/component keys, produced no direct payload identity. That does not rule out a rendered-output, native spool, device-side, or other source-defined representation.


The queue semantics add an important limit. `evidence/transfers/queue-note.txt` says queue names are physical print destinations and that a handoff proves acceptance by the queue, not paper collection. The fleet return register maps only PS-261003-0417 → ESC-N/FA-17, PS-261003-0448 → ESC-S/LV-42, and PS-261003-0420 → WATCH-SPARE/ST-09. It does not map job 0323. Thus `DEST=store` makes 0323 a useful physical-destination locator, while its device, queue host and collection remain unknown. Do not infer that 0323 used FA-17 or that paper was collected merely from its ACK.

## Highest-value next evidence

If an authorized custody path or unsolicited source delivery becomes available, prioritize:

1. The complete original print object and rendered physical output for **PS-261003-0323**, preserving native job name, queue/host/device, attempt, class, destination, original payload, rendering, completion/media-eject record and custody.
2. The corresponding original objects for **PS-261003-0317** (standby label), **PS-261003-0318** (commissioning label), **PS-261003-0320** (line brief), and **PS-261003-0306** (desk draft), as controls.
3. The Bundle 06 manifest and trim/omission log, and the original N23 margin/envelope, WN-14 folder and separate photo/galley-caption material already identified in the existing acquisition request.

This narrows the existing K08 acquisition request; it is not a reason to reopen the closed 21 October custodian channel. Do not treat the 16-byte spool payload as correct without an independent original/copy witness.

## Reproduction

Run from the repository root:

```powershell
python work/note_spool_crosswalk_sft.py
```

By default the script reads the repository's extracted files under `resources/evidence/`. It also accepts an extracted evidence directory or the original ZIP as an optional path. It verifies the 24/24 mapping and 300-second intervals and prints the rows with their full note text and payloads. It uses only the Python standard library.
