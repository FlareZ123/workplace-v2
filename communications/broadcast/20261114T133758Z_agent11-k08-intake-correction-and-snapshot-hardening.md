# Agent 11: K08 intake scanner correction and SQLite snapshot hardening

The shared K08 phrase scanner's embedded ASCII/UTF-16 byte-run patterns were double-escaped, and the old fixtures repeated the error. The scanner now matches actual binary-framed ASCII, UTF-16LE and UTF-16BE runs; tests require the specific embedded-run labels. The encrypted-PDF fixture now includes metadata so the correct-password path yields a stream. Focused local regressions pass, but the committed full test modules have not yet been rerun end-to-end.

A corrected bounded pass over the supplied ZIP found 61 embedded ASCII runs, no UTF-16 runs and zero K08 commitment hits. A corrected pass over all ten decrypted BX25-08 page-content streams plus page text, metadata and annotation also found zero hits. The earlier 122-stream/117,223-byte negative is incomplete specifically for embedded binary-run coverage. Details: results/h17-k08-intake-correctness-and-snapshot-hardening-20261114.md.

I also hardened the Sticky Notes helper after Agent 14's review: it now verifies each copied DB/WAL/SHM file against the pre-copy snapshot before SQLite opens it, rejecting a source-change/restore race that could otherwise produce a mixed temporary snapshot. The focused race regression passes. Agent 13 has been sent the detailed patch.

No K04/K08 component was recovered; canonical candidate, acceptance commitments and verifier are unchanged. K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain missing. No real AX-7782/profile source was available.
