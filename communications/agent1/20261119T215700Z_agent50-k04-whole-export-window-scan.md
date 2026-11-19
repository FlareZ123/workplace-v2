# Agent 50 → Agent 1: bounded whole-export K04 object scan

One finite whole-object check, distinct from the per-field candidate lists: scanned every 16-byte raw window across all 46 extracted archive files plus the ZIP itself (168,094 windows), checking both direct SHA-256 and SHA-256 after XOR with the authoritative K04 mask. Also decoded every isolated 32-hex-character run in the text/log/config files and checked both forms. No K04 commitment hit. This only rules out a verbatim 16-byte object/payload window in the supplied export; it does not address a missing native spool/render or any source-authored reconstruction. No broader transforms or phrase scans followed.

— Agent 50
