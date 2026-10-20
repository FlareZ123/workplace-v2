# H-17 REC8/1: evidence-derived recovery state

As of 20 October 2026, from the supplied surviving export and original `verify.py`/`acceptance.json`. Independent tests reproduce **six individual PASS commitments**. The combined SHA-256 is untestable until all eight slots are correct.

## Accepted component reductions

* **K01**: signed ink WN-14 A=`049AAB2E`, B=`1CDE7A82`, C=`CD7C6023`, D=`4303C91A` per mails 03/06/14. Join A,B,C,D: `049AAB2E1CDE7A82CD7C60234303C91A`. PASS.
* **K02**: telemetry LT-204/DIAG_WORD, acquisition UTC [2026-10-03 21:13:40,21:13:48). GOOD/HOLD only, greatest revision per seq 0..7. Chosen unsigned u16 big endian block `E1A5E474BAD7E853A2E8C71D3317D507`. SHA256(block)[:16]=`0D7E3AB56FB75DA3EB0E2E06786D239E`. PASS. Source uses `state`, not `phase`; honor mixed UTC offsets.
* **K03**: PTW-417 bay B,D,A,C, only highest revision of signed CLOSED AS_LEFT records. Serials `SG-D7DAD6BC|SG-9714519B|SG-7DAD0AD4|SG-BE8E87FD`. SHA256(ASCII)[:16]=`1384AF96E25D6ADA666209CB55E062FA`. PASS.
* **K05**: TRP2 header 16 bytes; 88 little-endian 24-byte records, CRC32 each; node=49 event=82, timestamps [21:14:00,21:14:08) UTC. Latest valid record per latch gives word 0=`FF8B7820`, 1=`0A56E858`, 2=`6DCDA00E`, 3=`F01E4572`. The four words are opaque byte sequences. K05=`FF8B78200A56E8586DCDA00EF01E4572`. PASS.
* **K06**: issued RC-17 revision C. Cabinet SERVICE_ORDER is DRAIN `5DBF40EE`, ISOLATE `52FAAED9`, PURGE `A536D332`, VERIFY `6CF0D95A`. K06=`5DBF40EE52FAAED9A536D3326CF0D95A`. PASS.
* **K07**: Gabriel's mail 13 confirms AX-7782 (not later AX-7783). Valid COMMIT with `dry_run=false`. The highest-attempt checkpoints for seq 0..7 concatenate to `8947CEDCB9CC73BAB7E87BE63302C5C9`. SHA256(raw)[:16]=`93495F5E425AB8E592123DABAEB68545`. PASS.

## K04: *unverified recovered buffer*

* Exact logical route at incident date: `ESC-N=PS-261003-0417` (September label mapping). Mask: `8556C8CB6140A7F9A5123AC7571BEE1C`.
* The job at 18:02Z, `ATTEMPT=2 STATE=ACK CLASS=RECOVER`, supplies `A9A9DC5731A5E2AE879C47215C2559D5`. The later attempt 3 was REQUESTED. An earlier 16:45Z ACK was `CLASS=LABEL`.
* XOR(mask, ACK payload)=`2CFF149C50E54557228E7DE60B3EB7C9`, but the K04 SHA-256 commitment rejects it. Email 16 and the custodian note explicitly warn that spool ACK does not prove media payload integrity. Do not relabel this as correct without evidence.
* **Prior-art correction (20 Oct 05:05 UTC):** The earlier local test covered <=4 bit flips, one/two arbitrary-byte replacements, and three *consecutive* arbitrary-byte replacements, but the related [workplace-v1 exhaustive original-target result](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md) had already tested **all 560 nonconsecutive/consecutive three-byte position triples, 9,285,570,000 exact three-byte candidate values**, with two independent controlled implementations and zero matches. Consequently at least **four differing byte positions** are required relative to the retained XOR output; this is a mathematical baseline-relative bound, not a physical printer corruption finding. The duplicate v2 brute source and manual workflow were retired; no more 3-byte CI is warranted. See [cross-repository prior-art evidence map](h17-v1-prior-art-gate.md).
* Supplemental provenance: `print-fleet-retirement-note.txt` and `supplier-reconciliation-L29.csv` join printer job 0417 to L-29/N, FA-17, H17-POL-17/A3, BX25/08. The encrypted `BX25-08.pdf` is openable with its four-digit release code `8131` (verified locally); it confirms the historic printer asset and identifies the otherwise redacted company as Noyes Energy Group. The folio includes a public correspondence-index URL `https://noyes-energy-group.pages.dev/`. The public site is accessible through a manually triggered GitHub Actions read-only public-web workflow but has a separate authenticated partner portal. No privileged account records have been accessed; do not treat an outside portal as proof of an authentic archive key.

## K08: *exact phrase missing*

* Normalize candidate to lowercase ASCII letters/digits/whitespace with punctuation replaced by spaces, collapse whitespace, trim. HMAC-SHA256(key=`5F933DA6A1BD03C32DA5CBC25344F497` decoded as hex, msg=normalized UTF-8), first 16 bytes; then check the K08 commitment.
* Emily's N02/N06 drafts; N10/N13/N20/N23 writing notes; mail 11 and 20 all indicate a personal scene with the sea outside, end of a long watch, lamp at the window, and voices/mugs/room at the table. Explicit nonanswers: the older standby and commissioning labels (`Leave the light on for the next watch`, `Back before the first boat`).
* No exact final caption has been found in the exported source. Normalized literal individual crew-board captions were tested and did not meet the commitment. Tone-matched paraphrase is not adequate for a keyed hash.
* Useful next steps: retrieve a preserved authenticated final-caption document, inked envelope image or independent print spool with provenance. Pure unrestricted guessing of natural language has no reproducible completeness guarantee.

## Offline acceptance

Populate `candidate.json` with the six values and `null` for K04/K08. Then run the unmodified `resources/verify.py` against `resources/acceptance.json`; expected result: K01,K02,K03,K05,K06,K07 PASS; K04,K08 MISSING; combined INCOMPLETE; accepted=false.

Do not infer plant operating authority from any recovered process-adjacent historical record.
