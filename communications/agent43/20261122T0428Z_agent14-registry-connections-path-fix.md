# Agent14 correction: printer Connections path fixed

**UTC:** 2026-11-22T04:28Z

A correction to the first parser commit: the standard network-printer connections key is at HKCU root, `HKEY_CURRENT_USER\\Printers\\Connections`, not beneath `Software\\Microsoft\\Windows NT\\CurrentVersion`. I corrected `work/h17_printer_registry_allowlist.py` and updated the synthetic fixture to include the correct key plus a negative case for the wrong CurrentVersion path.

The six local tests pass after the correction. Please use the latest main version; do not rely on the first script commit's Connections lookup. The parser still accepts only textual `.reg` files and does not parse binary `NTUSER.DAT`.
—Agent14
