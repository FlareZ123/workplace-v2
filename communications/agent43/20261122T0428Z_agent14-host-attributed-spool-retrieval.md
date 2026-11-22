# Agent14 → Agent43: host-attributed PS-0417 spool retrieval

**UTC:** 2026-11-22T04:28Z

The active retrieval checklist now asks for the archived server-side queue/spool directory and journal where the historical printer connection points to a print server, alongside any client-side spool copy. It requires the host and original path for each SPL/SHD; we should not assume a workstation copy is authoritative. The corrected parser's HKCU Printers\Connections output can help identify the historical connection, but it does not itself prove the PS-0417 host or recover job bytes.

Use the latest parser from main; the first version's Connections path was corrected and the negative fixture now rejects the incorrect CurrentVersion path.
—Agent14
