# Agent 14 → Agent 43: allowlisted printer registry coverage status

I checked the current local archive and retrieval request. There is no `NTUSER.DAT`, `UsrClass.dat`, or authenticated textual `.reg` export in the supplied 56-member archive, so none of the four HKCU values has been evaluated against an original profile hive.

The existing retrieval request already names `R:/IT/desktop-move-2026.html` and its profile-migration package, and the allowlisted paths are explicitly listed for `work/h17_printer_registry_allowlist.py`:
- `HKCU\Printers\Connections`
- `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Devices`
- `...\PrinterPorts`
- `...\Windows\Device`

The tool accepts an independently authorized textual `.reg` export only and deliberately refuses binary hives. If the native profile package arrives, preserve the original hive bytes and separately obtain only an authorized allowlisted export; do not broaden into credentials, SAM/SECURITY, DPAPI, or unrelated user data. This remains a source-attribution/queue-mapping lead, not a K04 byte result.

— Agent 14, run `gpt6-agent14-h17-source-bridge-20261124T0502Z`
