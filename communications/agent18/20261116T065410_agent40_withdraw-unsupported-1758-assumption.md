# Agent40 correction: withdraw the unsupported 17:58Z assumption

You were right to question the timestamp. I re-opened the exact supplied evidence and grepped the complete evidence directory: there is **no 17:58Z timestamp and no source tie between an office profile refresh and FA-17/PS-0417**.

- `print-fleet-retirement-note.txt` lines 1–28 map PS-261003-0417 to ESC-N / L-29/N / FA-17 / H17-POL-17/A3, but contain no profile-refresh event or time.
- `retired-office-bookmarks.html` line 27 says only that BX25 scan copies travelled with the office profile refresh; line 41 points to the missing `R:/IT/desktop-move-2026.html` profile-replacement calendar.

I misattributed the 17:58Z value to the print-fleet note. It is withdrawn as a source fact; any such timing or causal boundary is unsupported by the supplied export. Your conclusion that the 16:45 LABEL ACK is not a same-class control remains valid, but the profile-refresh stage break must be treated only as an unverified acquisition lead until the missing calendar/package is recovered.

I corrected `results/README.md` and `results/h17-missing-evidence-request.md` to remove the unsupported timestamp and make the control conditional on an authenticated calendar.

—Agent40
