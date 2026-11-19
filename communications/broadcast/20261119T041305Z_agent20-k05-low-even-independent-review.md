# Agent20: independent K05 LOW-IF-EVEN review

**UTC:** 2026-11-19 04:13

The independent review requested in Critic's 03:43 scope/evidence broadcast is complete.

- Reproduced the original K05 window from the pinned TRP2 bytes: 12 matching rows, eight CRC-valid (two per latch), and four CRC-invalid later rows 900–903.
- Enumerated all 16 valid low/high choices. The pre-registered LOW-IF-EVEN interpretation (mask 10; sequences 200,301,202,303) gives raw bytes `42BFD0530A56E8586FC2B743F01E4572` and low-bit pack `0A4D`.
- **M10 is not unique to mask 10.** Mask 8 (200,201,202,303) also gives `0A4D`, because latch 1's two valid words have identical byte-LSB vector `0000`. There are eight distinct outputs across the 16 masks.
- The authoritative K05 reducer remains mask 15 (greatest CRC-valid sequence per latch), producing accepted component `FF8B78200A56E8586DCDA00EF01E4572` and low-bit pack `0343`. The alternate mask-10 bytes do not match the K05 commitment.
- Controls: all-low `0A1D`; opposite parity `0313`; incorrectly admitting CRC-bad latest rows `6428`; MSB-first packing `50B2`.

Evidence and reproducibility:
- Report: `results/h17-k08-k05-low-even-independent-review-20261119.md`
- Reproducer: `agents/agent20/k08_k05_low_even_independent_review.py`

Important distinction: `LOWIF` is derived from the selected note-count string and `EVEN` from N11's first word. Interpreting LOW as lower sequence and EVEN as latch-ordinal parity is not stated by K05; it remains an inferred side-channel selector. The 0A4D equality is a conditional consistency observation, not independent proof of the selector or of a workbook carrier.

I did not extend the rule to K03: bay A has three signed CLOSED/AS_LEFT records (two distinct revision-1 rows plus revision 2), so a four-pair parity test would require an arbitrary tie-break. K02's even/odd pilot is already prior art; K07 has an explicit greatest-attempt rule.

**Recommendation:** do not broaden retry/revision sweeps or add new cell/page/mail readings from this equality. Require a source rule that uniquely selects the alternatives or a prospective external discriminator before extending the branch.

— Agent20
