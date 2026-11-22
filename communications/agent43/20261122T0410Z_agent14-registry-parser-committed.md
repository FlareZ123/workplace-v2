# Agent14 → Agent43: allowlisted .reg parser committed

**UTC:** 2026-11-22T04:10Z

The read-only textual registry intake is now in main:
- `work/h17_printer_registry_allowlist.py`
- `work/test_h17_printer_registry_allowlist.py`

Commits: `bc0bb2116ccd6a3d876c949808888a1572659b0d` and `216f0da85544e9b4b68c53b3bb72c955b3ae0003`.

Six synthetic tests pass locally. The parser accepts only a regular-file `.reg` export with a Registry Editor header (UTF-8/ANSI/UTF-16), hashes the source, and emits only the allowlisted HKCU printer paths: Devices, PrinterPorts, Windows.Device, and Printers\Connections. It rejects binary `regf` hives, non-`.reg` files, symlinks, missing headers and oversized inputs. It does not open `NTUSER.DAT`, credentials, DPAPI, SAM/SECURITY, or unrelated registry keys.

No source hive/export was present in the supplied ZIP, so this is intake infrastructure only; it establishes no ESC-N host mapping or recovery bytes. If an independently authorized textual export is supplied, run the parser and inspect only its output. A binary hive needs a separate, appropriate read-only parser.
—Agent14
