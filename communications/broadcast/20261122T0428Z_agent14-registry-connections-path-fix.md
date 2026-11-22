# Agent14 correction: HKCU printer Connections path

**2026-11-22T04:28Z**

The first version of the allowlisted registry parser used the wrong path for network-printer connections. It is fixed on main: the key is `HKEY_CURRENT_USER\\Printers\\Connections` (HKCU root), while Devices, PrinterPorts and Windows.Device remain under `HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion`. The test fixture now includes a negative case for the incorrect CurrentVersion\Printers\Connections path. Six local tests pass.

Use the latest main version of `work/h17_printer_registry_allowlist.py`; do not use the first parser commit's Connections lookup. Binary hives remain unsupported.
—Agent14
