# H-17 archive recovery: six verified components (Agent 50)

## Proven status

The supplied `resources/verify.py` and unmodified `resources/acceptance.json` independently verify all six recovered components. Candidate is in repository root `candidate.json`; K04 and K08 remain null because neither has passed its commitment.

| Slot | 16-byte hex | Status | Evidence |
|---|---|---|---|
| K01 | `049AAB2E1CDE7A82CD7C60234303C91A` | PASS | `mail/03.eml`, `mail/06.eml`, `mail/14.eml`: WN-14 signed ink A/B/C/D |
| K02 | `0D7E3AB56FB75DA3EB0E2E06786D239E` | PASS | `telemetry/freeze-export.jsonl`: LT-204 GOOD HOLD DIAG_WORD, UTC [21:13:40,21:13:48), highest revision per seq 0–7, u16 big endian -> SHA-256[:16] |
| K03 | `1384AF96E25D6ADA666209CB55E062FA` | PASS | `maintenance/seal-receipts.jsonl`, `mail/04.eml`: highest signed CLOSED AS_LEFT by bay, order B/D/A/C; serial string `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`, ASCII SHA-256[:16] |
| K05 | `FF8B78200A56E8586DCDA00EF01E4572` | PASS | `recorder/trip-recorder.raw` 24-byte records, validated CRC32, node 49, event 82, 21:14:00..08 UTC, highest sequence for latches 0..3, opaque words |
| K06 | `5DBF40EE52FAAED9A536D3326CF0D95A` | PASS | `procedures/RC-17-scans.txt`, `mail/11.eml`, `archive-labels.ini`: authorized Rev C, SERVICE_ORDER DRAIN/ISOLATE/PURGE/VERIFY |
| K07 | `93495F5E425AB8E592123DABAEB68545` | PASS | `transfers/transfer-audit.jsonl`, `mail/13.eml`: AX-7782 non-dry COMMIT; latest attempts per seq 0..7: `8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9`, SHA-256[:16] |

## Open investigation

**K04:** `ESC-N -> PS-261003-0417` per `archive-labels.ini`, confirmed `mail/16.eml`. Last ACK RECOVER is attempt 2, payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with mask `8556C8CB6140A7F9A5123AC7571BEE1C` yields `2CFF149C50E54557228E7DE60B3EB7C9`, which is **NO_MATCH**. We checked all 133 spool payloads against the K04 commitment and tested every single- and double-byte change of the direct ACK2-derived value (7,868,416 total candidates), with no match. Thus ACK proves dispatch, but export's opaque payload remains unverified. The extra `h17-supplemental-office-files` tie L-29/N, FA-17, H17-POL-17/A3 to the north route. `BX25-08.pdf` has a four-digit local release setting and can be opened offline (number recovered during testing), but is a property schedule, not a payload source. It contains an apparent public correspondence index URL, `https://noyes-energy-group.pages.dev/`. Access via current browsing tools has not been confirmed; do not assume its contents.

**K08:** `mail/11.eml`, `mail/20.eml` and crew-note N10/N13/N20/N23 describe a remembered final caption involving late-watch companionship, night, sea and mugs. N17 and N18 expressly belong to other envelopes; 43 direct draft/quote variants tested and none pass. It is a 16-byte prefix of HMAC-SHA256(key = supplied desk nonce, message = normalized phrase). The exact wording is not present as an unambiguous final quotation in the surviving text. Do not infer that a plausible paraphrase is accepted.

## Replication

Run `python work/h17_recover6.py` from the repository root (Python standard library). Then run `python resources/verify.py --candidate candidate.json --json` to check slot commitments. The script also computes and rejects the straightforward K04 spool fragment rather than writing it to the candidate. Evidence has not been modified.

No live plant operation or changes are involved.
