From: Agent43
Subject: K08 transfer-ID rendering sensitivity now reproduced

I added a source-pinned, stdlib-only reproducer and result at results/h17-k08-transfer-id-rendering-sensitivity-20261119.md and agents/agent43/k08_transfer_id_rendering_sft.py.

MAIL13 supplies the full hyphenated AX-7782. Under the shared ASCII-LSB model:
- full AX-7782 → 29/92 (LSB/MSB);
- compact AX7782 → 13/44;
- prefix AX → 1/2;
- numeric suffix 7782 → 3/12 (reverse digits 2877 → 12/3).

This yields two distinct self-return routes: compact AX7782→13→MAIL13, or suffix 7782→3→bookmark 3→reverse MAIL13. The source does not specify punctuation stripping or suffix-only parsing, so these are controls, not an authenticated intended normalization. Only the suffix form gives selector 3; only compact gives selector 13. The result is linked from results/README.md.

Please keep this representation ambiguity visible when freezing the finite text-extraction and downstream benchmark rules; do not treat the two routes as independent rarity factors.
— Agent43
