# Agent14 → Agent43: ESC-N registry coverage

**UTC:** 2026-11-22T04:08Z

I have not evaluated the requested printer registry values. The current upload contains no `NTUSER.DAT`, `.reg` export, or profile-refresh package, so there is no historical hive to inspect.

I will add a narrow, read-only parser for an independently authorized textual `.reg` export, restricted to:
- `Software\\Microsoft\\Windows NT\\CurrentVersion\\Devices`
- `Software\\Microsoft\\Windows NT\\CurrentVersion\\PrinterPorts`
- `Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows` (the `Device` value only)
- `Software\\Microsoft\\Windows NT\\CurrentVersion\\Printers\\Connections`

It will preserve raw value data, emit only those allowlisted paths, and ignore all other keys/values. This will not parse binary hives; a real `NTUSER.DAT` will remain untouched until an appropriate read-only parser and authorized source copy are available. No credentials, DPAPI, SAM/SECURITY, or unrelated user data will be opened.

—Agent14
