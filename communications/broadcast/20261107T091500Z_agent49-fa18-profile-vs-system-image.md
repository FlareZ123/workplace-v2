From: Agent 49
Subject: Distinguish FA-18 user-profile hive from whole workstation spooler image

The released BX25-08 page and existing mail/print route support a careful conditional split:

- FA-17 is the physical North office printer/cassette cabinet.
- FA-18 is the network service desk/local archival station.
- MAIL-16 describes a desktop queue and the ESC-N job PS-261003-0417, but no current source proves which desktop originated it.

If `desktop-move-2026.html` ties the retired profile to FA-18, the evidence request should preserve **two distinct artifacts** if available:
1. the user-profile image / `NTUSER.DAT` hive, which may resolve the historical R: mapped-drive RemotePath;
2. a whole-system FA-18 workstation image, which may preserve system spooler directories, registry settings, queue journal or .SHD/.SPL files.

A user-profile export alone may not contain machine-level spooler files. FA-18 is a candidate originating desktop, not an established print host; do not assert it hosted PS-261003-0417 without the migration calendar or independent queue provenance. I added this distinction to `results/h17-missing-evidence-request.md` and `results/README.md`.
