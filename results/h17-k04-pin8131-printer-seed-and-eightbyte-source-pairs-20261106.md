# H-17: scanner-release PIN seeded printer issuer and archive-pair source search

**Agent 10 | 6 November 2026 | Original six slots PASS; K04 and K08 still missing.**

## Two new source-cued attempts

1. **An otherwise unavailable printer emitter seed might survive as the four-digit office-scanner release setting.** The original supplementary November 2025 BX25/08 PDF is encrypted, and independent previous research recovered local user password `8131` using the documented four-position numeric release setting; see [original PIN and decoded folio report](h17-encrypted-bx25-public-correspondence-index-20261103.md). This experiment asks whether that surviving original physical-office *setting* seeded a later **shared CPython MT19937 printer payload stream**. A common source seed and a CPython printer implementation are both hypothetical. The PDF code originally concerns a scanner, not a printer; model portability is unproved.

2. **Could a wholly independent future printer-stream two-word pair have survived verbatim elsewhere in the original archive?** This would supply a source witness for a shared, hypothetical MT state in addition to prior one-word coincidences. We tested contiguous original raw-byte / hex-string carriers in each of the other 45 ZIP members, excluding the printer spool source itself, against *every* consecutive pair of fully printer-source-determined standard-tempered MT words in the p951 symbolic model. This is a source-only original-object acquisition test, not a coupon prediction.

## Executed tests

### PIN-based original-source packet discriminator

The frozen original spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The 133 physical-spool records contain 132 **unselected** original 16-byte copied packets, four native 32-bit words each. Exclude the disputed selected `row129` completely. In 132 retained packets, attempt both word orders and both 32bit byte orders, yielding 528 full comparison presentations (all distinct).

Freeze seven direct ways of interpreting **originally released PIN 8131** as a CPython `random.Random` seed: integer 8131, ASCII `8131`, binary little/big-endian representations, SHA256(`8131`) integer, and PIN/BX25 folio string in both orders. For each independently initialized native stream, generate 100,003 32-bit words and test all first 100,000 sliding **four-consecutive-word** windows against **all 528 complete original source packets**.

| Source-derived PIN seed variant | Sliding whole-packet windows | Source word matches | Intact full-packet matches |
| --- | ---: | ---: | ---: |
| Integer PIN | 100,000 | 0 | **0** |
| ASCII PIN | 100,000 | 0 | **0** |
| Binary PIN, little endian | 100,000 | 0 | **0** |
| Binary PIN, big endian | 100,000 | 0 | **0** |
| SHA256-derived PIN integer | 100,000 | 0 | **0** |
| PIN then BX25/08 folio label | 100,000 | 0 | **0** |
| BX25/08 folio label then PIN | 100,000 | 0 | **0** |
| **Total** | **700,000** | **0** | **0** |

A genuinely generated native fourword packet at artificial draw offset67 was recovered uniquely from the same seeded CPython stream. This is a full-packet source test with no original K04 hash or copied ACK consulted. [Portable original-source SFT](../agents/agent10/k04_scanner_pin_prng_source_sft.py); executed locally from the supplied original ZIP. The lack of a single 32-bit source word match is descriptive and not, on its own, a valid global RNG exclusion.

### Different preserved-source location: independent consecutive MT pair

Original ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. Using [Agent49's preexisting p951 symbolic printer-source model](../agents/agent49/k04_p951_symbolic_basis.py), fitted to 132 intact unselected spool records at exact original rank15,365, standard temper projection identifies **991** wholly source-determined original/native MT words among stages -1100..1040 and **706** stages where two consecutive words are both fully known. For the 45 other source members, test every contiguous eight raw bytes and every 16-nibble ASCII hex run in both nibble phases, against both word orders and both consistent word endiannesses of every pair.

| Measurement | Executed count |
| --- | ---: |
| Eightbyte raw source windows | 100,650 |
| Hex-carrier eightbyte interpretations | 1,127 |
| Source-derived two-word layout presentations | 2,824 |
| **Eightbyte matches** | **0** |

Earlier source experiments already identified isolated individual 32-bit matches against nonprinter source values, including PTW/recorder/withdrawn RC17 fields. This new whole-pair search finds **no additional intact adjacent pair witness** in the original decompressed ZIP members. The SFT used read-only exact symbolic source and enumerated complete bytes. It has not independently proven the p951 producer historically correct. Local exploratory source script `/mnt/data/h17-research/k04_archive_mt_eightbyte_anchor_sft.py` performed the second count; no standalone repository script is published for that audit.

## Implication and boundary

**Neither mechanism supplies an original full K04 coupon or authenticated selected physical bit**. The PIN issuer model is rejected in its exact direct CPython seed/output/candidate windows by the intact source packet check. Alternate hardware secrets, much larger phase, different serializers, or any separate generator remain possible. The source-pair negative limits one original witness-location route but does not show that 2026 paper or missing final caption cannot survive somewhere outside the supplied export.

Do not infer a K04 component from the selected disputed spool copy. K08 terminal caption remains absent; the original HMAC/SHA commitment is unchanged. Original combined REC8 is still `accepted=false` / incomplete.