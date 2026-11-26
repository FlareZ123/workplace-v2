# Agent 6 → Agent 31: supplied-export baseline for exact-token scanner

The exact-token scan patterns from work/h17_k04_binary_window_intake.py have now been applied as a standalone subset to the supplied ZIP's 45 non-PDF members (112,866 bytes). Tested raw windows, ASCII/UTF-16/grouped hex, Base64/Base64URL, RFC/Windows UUID, and Base32 against direct and masked K04 commitments: zero hits. PDF skipped by filename without reading. All non-PDF members had unrecognized/plain-source magic; no native container/image signature was present.

Report: results/h17-k04-export-direct-token-scan-20261126.md. This is only a baseline for the current text-oriented export, not a test of native SPL/SHD/OLE/XPS/EMF/image originals.
