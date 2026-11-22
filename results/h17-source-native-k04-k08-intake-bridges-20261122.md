# H-17 native media: two complete-candidate intake gaps closed

**Agent 22 | 22 November 2026 | Implemented and regression-tested; original K04 and K08 unresolved**

## Distinct failure mechanisms addressed

**K04: OLE/CFB input silently lost its entire candidate surface.** In `work/h17_k04_binary_window_intake.py`, an OLE-compound file was classified as a container and excluded from raw scanning, while the walker had branches only for ZIP, TAR and GZIP. Consequently every original 16-byte coupon present in the raw bytes of a native OLE/CFB spool/workbook would have been invisible to this scanner. It now treats such files as raw scannable sources. The same scanner can recognize exact 16-byte coupons represented as ASCII hex, UTF-16LE/BE hex, 16 two-digit hex groups with ordinary separators, or canonical padded Base64, as well as raw 16-byte windows. Every representation is checked against both original K04 SHA-256 reduction paths: direct component and source payload XOR published route mask. No altered commitment, guessed producer, or state extrapolation is involved.

**K08: original workbook picture and caption fields were disconnected from the exact phrase test.** The source bookmark references `R:/Stores/consumables/mug-stock.xls`; source-stage K08 research has identified M10 as a *conditional* image/caption coordinate, while it has not authenticated a particular original workbook or photo. The decoder in `work/h17_ax7782_k08_phrase_intake.py` already checked every normalized contiguous phrase against the original HMAC/SHA-256 commitment, and existing helpers already decoded BIFF8 OfficeArt shapes, BLIPs and LibreOffice-converted workbook images. However, neither original native M10 shape names/descriptions and embedded BLIP image bytes nor converted M10 image bytes reached that phrase checker.

The dispatcher now admits only the exact named `mug-stock.xls` and the original M10 anchor. It yields original OfficeArt `wz_name`/`wz_description` strings, SHA-256-verified native image bytes referenced by an M10 shape, and, where necessary, SHA-256-verified LibreOffice-converted M10 images. Original image bytes take precedence; matching converted image bytes are deduplicated. Image metadata and optional OCR then feed the unchanged K08 normalized-phrase HMAC comparison. The direct OfficeArt route also works when the converter is unavailable. Neither the source workbook nor acceptance files are modified.

## Reproduction and coverage

- `work/h17_k04_binary_window_intake.py --self-test`: planted direct and masked coupons, raw OLE/CFB source, UTF-16LE/BE hex, grouped hex and Base64, all exact matches.
- `work.test_h17_ax7782_k08_phrase_intake`: synthetic M10 native OfficeArt BLIP image and shape description recover without conversion; PNG metadata supplies a planted complete phrase that passes a synthetic K08 HMAC commitment. A non-M10 original shape is excluded. The converted-image branch and unrelated workbooks also have positive/negative controls.
- `work.test_h17_xls_lo_fallback`: a real LibreOffice-generated synthetic BIFF8 workbook contains an M10 image that reaches the shared phrase dispatcher unchanged; its SHA-256 matches the original generated PNG.
- Existing OfficeArt/BLIP regression fixtures were repaired to respect the CFB 4096-byte regular-stream cutoff; a separate unrelated synthetic PDF password test was corrected to use the password written by its own fixture.

The combined existing Office/SQLite regression and both added paths passed in [GitHub Actions run 45009933577](https://github.com/FlareZ123/workplace-v2/actions/runs/45009933577), against commit `c419756a0f90079f914bcd310063ae324bcca940`. The earlier source-native M10 path separately passed in [run 45009484009](https://github.com/FlareZ123/workplace-v2/actions/runs/45009484009).

## Recovery boundary and next direct test

The supplied preservation ZIP has 46 files and **no original `mug-stock.xls`, native `.SPL`/`.SHD`, or complete AX-7782 object**. These new decoders therefore demonstrate *successful positive controls* and correct source representation, not recovery of an actual H-17 candidate. An original recovered workbook/photo also requires independent linkage to Emily's final version before claiming historical authenticity. Selected K04 ACK copy `A9A9DC5731A5E2AE879C47215C2559D5` still fails its commitment; K08's exact final wording remains absent. Original REC8/1 status is unchanged: K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined INCOMPLETE.

The next meaningful input is an independently recovered native printer artifact from `PS-261003-0417` or the actual `mug-stock.xls`/original M10 media, respectively. Test original complete candidate outputs immediately against the unchanged verifier. References: [BIFF8 OfficeArt parser](h17-officeart-biff-metadata-intake-20261120.md), [M10 coordinate construction](h17-k08-n20-m10-t11-transition-20261119.md), [current recovery map](README.md).
