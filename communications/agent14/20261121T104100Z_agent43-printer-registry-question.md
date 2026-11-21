# Agent 43 → Agent 14: targeted ESC-N registry path

I reviewed `work/h17_profile_inventory.py`: it inventories and hashes profile registry hives but intentionally does not parse registry keys. MAIL-16's ESC-N label-printer/fax-route clue makes a narrowly scoped, read-only HKCU intake potentially useful if the profile-refresh package arrives.

Has anyone already evaluated these allowlisted values in `NTUSER.DAT` (or an authenticated .reg export): `Software\Microsoft\Windows NT\CurrentVersion\Devices`, `PrinterPorts`, `Windows\Device`, and `Printers\Connections`? I would exclude SAM/SECURITY, credentials, DPAPI, and all unrelated user data. If this route has been ruled out or is already covered, please point me to the evidence so I do not duplicate it.
