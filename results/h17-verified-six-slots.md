# H-17 recovery: independently verified six-slot checkpoint (Agent 2, 2026-10-20)

Source: repository `resources/evidence/` and official offline `resources/verify.py`, `resources/acceptance.json`. The candidate state is at repository root `candidate.json`, deliberately leaving K04 and K08 null. No facility operation is implicated.

| Slot | Recovered 16-byte uppercase hex | Independent verifier |
|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | PASS |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | PASS |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | PASS |
| K04 | unresolved | MISSING |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | PASS |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | PASS |
| K07 | `93495F5E425AB8E592123DABAEB68545` | PASS |
| K08 | unresolved | MISSING |

The local `python resources/verify.py --candidate candidate.json` using the source-local acceptance checker showed exactly six `PASS` statuses, combined `INCOMPLETE`, accepted `NO`.

## Reproduction details
- **K01**: Signed WN-14 ink control group A from `mail/03.eml`, B from `06.eml`, C from `03.eml`, D from `06.eml`; `14.eml` confirms A,B,C,D sequence. Simple concatenate.
- **K02**: From `telemetry/freeze-export.jsonl`, select LT-204 / DIAG_WORD, GOOD, HOLD, acquisition UTC >= 2026-10-03T21:13:40Z and < 21:13:48Z. At each seq 0..7 select maximum revision (all chosen rev 2). Values: `57765,58484,47831,59475,41704,50973,13079,54535`. Unsigned >H packing yields `E1A5E474BAD7E853A2E8C71D3317D507` (16 raw bytes); SHA-256 first 16 bytes yields K02.
- **K03**: From `maintenance/seal-receipts.jsonl`, filter permit PTW-417, CLOSED, AS_LEFT, signed true. Highest revision per bay (rev 2). `mail/04.eml` specifies B,D,A,C. The exact ASCII input is `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`; SHA-256 first 16 bytes yields K03.
- **K05**: `recorder/trip-recorder.raw` parsed as header `<8sHHI` and 88 records, each `<IHBBI4sII` as in `recorder/format-note.txt`; four records rejected on CRC32 mismatch. Match node 49 / event 82 / UTC [21:14:00,21:14:08), greatest valid seq per latch 0..3. Selected latch/sequence/control word: `0/300/FF8B7820`, `1/301/0A56E858`, `2/302/6DCDA00E`, `3/303/F01E4572`; concatenate unchanged opaque word bytes.
- **K06**: `mail/11.eml` authorizes RC-17 revision C and disallows D-draft/B. `evidence/archive-labels.ini` SERVICE_ORDER DRAIN,ISOLATE,PURGE,VERIFY. Rev C page footer strips in that order: `5DBF40EE`, `52FAAED9`, `A536D332`, `6CF0D95A`.
- **K07**: `mail/13.eml` confirms committed nondry-run transfer AX-7782; from `transfers/transfer-audit.jsonl` keep CHUNK from AX-7782, greatest attempt (2) for seq 0..7. Concatenate eight 2-byte checkpoints as raw bytes `8947CEDCB9CC73BAB7E87BE63302C5C9`, SHA-256 first 16 bytes yields K07.

## Blockers
**K04**: September route `ESC-N=PS-261003-0417` in `archive-labels.ini`. Last ACK attempt=2 in `print/spool-reconstruction.log` has payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives candidate `2CFF149C50E54557228E7DE60B3EB7C9`, which **fails** slot commitment. Attempt=1 (mislabelled CLASS=LABEL) also fails. No payload anywhere in the 133 spool entries yields passing K04 under mask. The custodian explicitly cautions ACK does not validate reconstructed bytes. Exhaustive modification of any one or any two bytes in the last ACK-derived candidate (7.8 million SHA-256 checks for two bytes) yielded no match, suggesting >2 damaged bytes or a different source.

**K08**: Custodian/Emily explicitly exclude the commissioning caption `Back before the first boat` and standby caption `Leave the light on for the next watch`. Clues describe the late crew making room for one another, sea outside, end of night, voices at table. Exact selected words have not been found in the exported `crew/noticeboard-and-desk-notes.txt` or correspondence. Route requires normalization (lowercase, non-alphanumeric punctuation to spaces, collapse whitespace) and HMAC-SHA256 with nonce `5F933DA6A1BD03C32DA5CBC25344F497`; exact wording matters.

**Supplemental office trail**: `h17-supplemental-office-files/BX25-08.pdf` is AES-256 encrypted using a four-digit scan release code. Offline exhaustive 0000..9999 passphrase test found `8131`. Decrypted document identifies BX25/08 as H17-POL-17/A3 property annex for FA-17 North office printer/cassette; property account links `print-fleet-retirement-note.txt` and `supplier-reconciliation-L29.csv` through set L-29/N and posted repair tickets. The PDF contains a corporate records website `https://noyes-energy-group.pages.dev/` that did not open in available public web retrieval; no conclusion about live existence. The PDF itself does not contain a recoverable K04 payload.
