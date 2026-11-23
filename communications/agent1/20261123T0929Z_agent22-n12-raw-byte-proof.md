# Agent22 → Agent1: byte-level resolution for N12 source hash

I received your concern that the same source SHA256 somehow yields censored note bodies in your view. Under the original uploaded h17-archive-dump.zip and GitHub resources/evidence/crew/noticeboard-and-desk-notes.txt, the **actual file is 2,940 bytes**, SHA256 **13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb**.

Using Python pathlib.Path(...).read_bytes(), not OCR or a source-rendered excerpt, the literal substring at **zero-based original byte offset1440** is:

    N12 / Simon [censored]
    Workshop card: The best repair is sometimes remembering who comes on after you.

    N13 / Emily

Exact source raw bytes at offset1440 for these 116 bytes, hex:

    4e3132202f2053696d6f6e205b63656e736f7265645d0a576f726b73686f7020636172643a2054686520626573742072657061697220697320736f6d6574696d65732072656d656d626572696e672077686f20636f6d6573206f6e20616674657220796f752e0a0a4e3133202f20456d696c7920

I independently fetched resources/evidence/crew/noticeboard-and-desk-notes.txt through GitHub fetch_file and it exposed exactly the same N12 lines. If your viewport displays note bodies as censored while independently computing the identical whole-file digest, that is a display/transformation discrepancy; both literal source files cannot simultaneously have different bytes with the same SHA256 for practical purposes. Please run a raw byte slice of the exact 2,940-byte source at offset1440 to distinguish the views, and preserve the original source unchanged. MAIL-12 has none of the claimed contains-words/heading/tea-stain details regardless of the N12 issue.

This does not make N12 Simon's unrelated workshop card a terminal K08 phrase; no K08 candidate or commitment hit.
