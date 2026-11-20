# BIFF8 OfficeArt shape-description reader — conditional intake capability

**Status:** parser implemented; synthetic and real-BIFF control tests passed locally. No incident workbook was available, no real source description was extracted, and no K08 candidate was generated or tested.

## Question

Can a legacy BIFF8 `.xls` retain a shape name/description and worksheet anchor that a later LibreOffice conversion no longer exposes?

## Implementation

`work/h17_biff_officeart.py` is a bounded, read-only parser for the original OLE Compound File / BIFF8 stream. It:

1. reads the CFB `Workbook` or `Book` stream, supporting regular and mini-stream allocation;
2. follows BIFF `BOUNDSHEET` offsets and concatenates worksheet `MSODRAWING` payload fragments (including intervening `OBJ` records);
3. traverses OfficeArt drawing/group/shape containers;
4. reads the shape id/type, `OfficeArtClientAnchorSheet` top-left and bottom-right cells, and complex `wzName` (FOPT property 0x0380) / `wzDescription` (0x0381) Unicode strings.

The code is deliberately separate from the frozen M10 cell-value test and from the K08 candidate-generation pipeline. It is an intake capability only; it must not be used as a fallback after the frozen cell-value test fails.

## Validation

Run from the repository root:

```bash
PYTHONPATH=work python -m unittest -v work.test_h17_biff_officeart
```

Six local tests passed in the authoring runtime. The existing Office/SQLite intake regression also passed on GitHub Actions run [44689341273](https://github.com/FlareZ123/workplace-v2/actions/runs/44689341273), with the parser module compiled and its test module included in the existing suite:

- synthetic BIFF/CFB regular-stream positive control for a picture shape, M10 anchor, name and description;
- the same positive control through a CFB mini stream;
- no-drawing workbook returns no shapes;
- malformed/non-CFB input fails closed;
- oversized input fails closed;
- a real LibreOffice-generated BIFF8 workbook containing a picture anchored at M10 is parsed as a picture (shape type 75, shape id 1025, anchor M10, name `Image 1`).

The real LibreOffice-generated control has no `wzDescription`; LibreOffice's XLSX-to-XLS conversion does not preserve the source OOXML description in this fixture. The synthetic description test validates the parser's field decoding only; it is not a source-derived phrase and is not evidence that the H-17 workbook contained one.

## Evidence and limitations

The Microsoft format definitions support the parsing boundaries: [MS-XLS MsoDrawing](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xls/1b0b0ea3-5e1d-41ce-8e79-e27f1041331e), [MS-XLS OfficeArtClientAnchorSheet](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xls/fd656a2c-d5ee-4171-8f65-17a08b9f2262), [MS-ODRAW OfficeArtSpContainer](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-odraw/16194cb9-b4b0-476c-9678-a6ac1f06b034), and [MS-ODRAW OfficeArtFOPT](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-odraw/2841bed9-1ff1-4981-807e-ffb9592c046d). The OfficeArt description property is a complex null-terminated Unicode string under property id 0x0381; the name property is 0x0380 ([MS-ODRAW specification, sections 2.3.4.1–2.3.4.4](https://officeprotocoldoc.z19.web.core.windows.net/files/MS-ODRAW/%5BMS-ODRAW%5D-241112.pdf)).

The supplied `h17-archive-dump.zip` has no `.xls` member, and the repository's `resources/evidence/` tree has no original `mug-stock.xls`. The normal-agent `private/` directory contains only its placeholder. Therefore the parser has not been run on the H-17 workbook.

**Hard scope gate:** Agent 7's 20 November scope correction is controlling for this lead. Do not read or test a description field unless an independent source record first establishes the exact image object/version, its M10 anchor, and its link to N10/Emily's final-envelope chain. Do not conflate the shape description with the frozen stored/displayed cell-M10 value. Even if a future description is extracted, it remains a separate source field and requires its own source-lineage assessment before any K08 HMAC check.

## Next action

If an independently authorized original workbook and its source/version link become available, run this parser as a separate intake, preserve the original bytes and extracted shape metadata, and compare the exact shape/version against the independent source record. Until then, this result is tooling validation only: K08 remains unresolved.
