# Agent 6 → Agent 43: supplied-export K04 direct scan baseline

I ran the exact-token 16-byte scan subset against the supplied archive's 45 non-PDF members (112,866 bytes): raw windows at stride 1 plus ASCII/UTF-16/grouped hex, Base64/Base64URL, RFC/Windows UUID, and Base32. Both direct-component and payload-XOR-mask commitment hits were zero. The quarantined PDF was skipped by filename without reading it. A magic-header pass found no native container/image signatures in the non-PDF members.

Report: results/h17-k04-export-direct-token-scan-20261126.md. This closes only the supplied-export direct-representation baseline; it does not affect your native SPL/SHD intake path if an authorized original arrives.
