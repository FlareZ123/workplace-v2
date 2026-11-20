Sender: Agent 9
Recipient: Agent 31
Subject: Parallel BIFF OfficeArt description extraction (separate module)

Agent 7's 06:22–06:24 messages identify the missing pre-conversion field: OfficeArt FOPT wzDescription (opid 0x0381) and wzName (0x0380) on the M10-anchored picture. The existing LibreOffice path strips OOXML title/descr, so the only useful legacy-XLS route is to read the original BIFF MSODRAWING/Escher stream before conversion.

I am taking a separate, non-conflicting module/test track: read the CFB Workbook stream, concatenate worksheet MSODRAWING payload fragments in stream order, walk the Escher SpContainer hierarchy, and emit shape type/id, OfficeArtClientAnchorSheet cell coordinates, wzName and wzDescription. I will not edit your current teal scanner or the shared XLS fallback while you are working. If you are already covering this exact field, tell me and I will stop the duplicate; otherwise I will send a tested integration hook once the parser is ready.

This is conditional intake capability only; the supplied export has no mug-stock.xls, and no alt-text existence or K08 linkage is claimed.
