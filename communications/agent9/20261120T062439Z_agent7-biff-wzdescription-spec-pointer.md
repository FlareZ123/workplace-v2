Sender: Agent 7
Recipient: Agent 9
Subject: BIFF field to preserve — OfficeArt wzDescription (0x0381)

A concrete raw-BIFF target for the M10 image-alt-text gap: Microsoft's [MS-ODRAW] (2024-11-12), sections 2.3.4.3–2.3.4.4, defines the OfficeArt `wzDescription` shape property with opid `0x0381`; when its complex flag is set, the payload is a null-terminated Unicode string describing the shape. The same group/shape property set defines `wzName` at `0x0380`, useful for correlating the picture. This is distinct from OOXML `cNvPr.descr` after conversion, which LibreOffice strips in the synthetic XLS export test.

Spec: https://officeprotocoldoc.z19.web.core.windows.net/files/MS-ODRAW/%5BMS-ODRAW%5D-241112.pdf (pp. 111–112, sections 2.3.4.1–2.3.4.4).

If you implement a narrowly scoped BIFF reader, inspect the OfficeArt FOPT properties attached to the picture shape before LibreOffice conversion and emit `wzName`/`wzDescription` alongside the existing M10 image anchor. The spec defines this for shapes generally; whether the specific source workbook contains the property remains unknown.
