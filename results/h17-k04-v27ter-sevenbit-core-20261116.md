# K04: ITU V.27ter seven-bit self-synchronizing core, 16 November 2026

**Agent 48. Original K04 full commitment: NO MATCH (512/512 complete candidates).** The six accepted components remain intact. K04 and K08 are missing, and combined REC8/1 is INCOMPLETE.

## Source and explicit model boundary

Original crew note N22 says the label printer was behaving "like a fax machine." This is an informal simile, not authenticated equipment documentation. The ITU-T V.27ter recommendation (§9) specifies a self-synchronizing scrambler/descrambler with generator polynomial **1 + x^-6 + x^-7**, plus guards against repeating transmitted patterns. This 7-bit core is a different finite mechanism from Agent6's 16 November V.17/V.29 23-bit **1 + x^-18 + x^-23** test and Agent18's separate additive 16-bit LFSR-keystream test.

Official historical standard: [CCITT Yellow Book, Volume VIII.1, Recommendation V.27ter, §9](https://search.itu.int/history/HistoryDigitalCollectionDocLibrary/4.258.43.en.1025.pdf) (printed page 155). The source documents a telephone-modem polynomial; **nothing in the H-17 export attests that ESC-N used the modem**.

Test the bounded hypothesis that the selected copied ESC-N 16-byte spool buffer is a 128-bit scrambled bitstream whose seven preceding bits were not retained. Keep the source-prescribed K04 XOR mask and original 256-bit acceptance commitment unchanged.

## Pinned source selection

- `resources/evidence/print/spool-reconstruction.log`: SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- `resources/evidence/recovery-routing.json`: SHA256 `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`.
- `resources/acceptance.json`: SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.
- `resources/evidence/crew/noticeboard-and-desk-notes.txt`: SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`.

Exact selected row: `2026-10-03T18:02:00Z JOB=PS-261003-0417 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=A9A9DC5731A5E2AE879C47215C2559D5 DEST=bench`.

Mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original K04 SHA256 commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Complete seven-bit core enumeration

For each received bit `s[n]`, the descrambler core is `d[n] = s[n] XOR s[n-6] XOR s[n-7]`. The forward scrambler core is `s[n] = d[n] XOR s[n-6] XOR s[n-7]`. Enumerate every possible seven-bit preceding `s` history, for either source byte bit serialization (most-significant bit first or least-significant bit first), and apply either direction. For each resulting **complete 16-byte candidate coupon**, XOR the full 16-byte official mask and compare the SHA256 of the resulting component with the complete original commitment.

| Model | 7-bit histories | Full candidate hashes | Original K04 matches |
| --- | ---: | ---: | ---: |
| MSB-first descramble | 128 | 128 | 0 |
| MSB-first scramble | 128 | 128 | 0 |
| LSB-first descramble | 128 | 128 | 0 |
| LSB-first scramble | 128 | 128 | 0 |
| **Total** | **512** | **512** | **0** |

All four original source fingerprints are asserted in the reproducer. Six direction/serialization/history round-trip controls passed. A synthetic full coupon based on an independently selected MSB-first descramble history 93 was recovered **exactly once** by the same full-SHA256 search. In the tested 135-bit windows (seven hypothesized preceding bits plus the entire 128-bit packet), no 45-bit period-9 or period-12 guard trigger appeared. This local check cannot model unknown earlier guard history and does not implement V.27ter's extra period-8 guard circuitry.

The executable source-pinned SFT is [`agents/agent48/k04_v27ter_scrambler_sft.py`](../agents/agent48/k04_v27ter_scrambler_sft.py); Python standard library only, read-only, accepts the original ZIP using `--archive`, or reads the repository's `resources/` by default.

## Interpretation

The selected copied payload does **not** yield the accepted K04 under the four specified **unguarded seven-bit V.27ter core** families. This new narrow exclusion neither recovers a physical coupon nor justifies a broad fax-standard scan. It does not cover guard effects dependent on pre-window history, bit framing shifts, corrupt source bytes, a different mask/export stage, or other producer architectures. As an informal source cue, N22 does not identify any real ESC-N transmission protocol.

No canonical candidate, acceptance commitment, route, source evidence or official verifier was modified. No new K04 selected bit or K08 final-caption word was authenticated.
