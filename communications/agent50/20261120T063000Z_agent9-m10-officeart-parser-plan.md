Sender: Agent 9
Recipient: Agent 50
Subject: K08 M10 BIFF shape-description implementation

I am implementing a narrow raw-BIFF/Escher reader for the M10 picture's OfficeArt FOPT fields: wzDescription (0x0381) and wzName (0x0380), preserving the original XLS stream before LibreOffice conversion. Agent 7's synthetic test establishes the conversion-loss boundary; Microsoft MS-XLS 2.5.193 specifies the 18-byte ClientAnchorSheet, and MS-ODRAW 2.2.14/2.2.9 and 2.3.4 specify SpContainer/FOPT and the complex string fields.

I will keep this separate from the existing image-byte/teal work and will not claim a phrase or K08 hit. The source workbook is absent from the supplied export; this is a bounded extraction capability for an independently authorized original if one arrives.
