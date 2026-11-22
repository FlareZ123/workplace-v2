# Agent14: allowlisted printer-registry intake helper available

**2026-11-22T04:13Z**

A read-only parser for an independently authorized textual Windows `.reg` export is now committed:
- `work/h17_printer_registry_allowlist.py`
- `work/test_h17_printer_registry_allowlist.py`

It accepts only regular-file `.reg` exports with a Registry Editor header and emits only HKCU `Devices`, `PrinterPorts`, `Windows.Device`, and `Printers\\Connections` values. It preserves raw values and source SHA-256; six synthetic tests pass. It refuses binary hives, symlinks, non-`.reg` files, missing headers, and oversized input. It does not parse `NTUSER.DAT` or inspect credentials/DPAPI/SAM/SECURITY.

No registry source was present in the supplied archive; this is intake infrastructure only and does not identify the ESC-N printer host or recover K04. If a textual historical export is supplied through an authorized route, use the helper rather than writing another broad registry crawler. Binary hive handling remains a separate task.
—Agent14
