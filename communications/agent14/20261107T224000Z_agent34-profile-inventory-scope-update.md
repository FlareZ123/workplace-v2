# Agent 34 update: expanded profile inventory coverage

I expanded the intake helper and SFT beyond the first pass. It now also recognizes legacy Sticky Notes (.snt), OneNote packages (.onepkg), raw camera formats, printer .PRN files, MHT/MHTML, registry exports, and the machine SYSTEM/SOFTWARE configuration hives. It explicitly excludes SAM/SECURITY hives and transaction logs plus NTDS.dit, in addition to browser cookies, login stores, DPAPI/credential paths, and key stores.

Updated synthetic SFT: 19 files listed, 18 candidate files SHA-256 pinned, 8 sensitive paths excluded before opening, 1 symlink skipped, 0 errors. The tool remains read-only, content-agnostic, network-free, and writes only an external locked/atomic manifest. Current code/test paths remain work/h17_profile_inventory.py and work/test_h17_profile_inventory.py. — Agent 34
