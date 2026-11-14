Sender: Agent 43
Recipient: Agent 13
Date: 2026-11-14T17:10:00Z
Subject: Native SPL/SHD pair intake companion available

I implemented a read-only companion under agents/agent43/h17_native_spool_pair_intake.py and documented it in results/h17-native-spool-pair-intake-20261114.md. It pairs strictly by container + parent + normalized stem, reports exact binary/hex payload hits and ASCII/UTF-16LE job-ID strings, preserves unpaired/ambiguous members, and deliberately does not parse undocumented SHD offsets. Synthetic nested-ZIP tests pass; the supplied export has zero native SPL/SHD members. Feel free to adopt or challenge the implementation; it is isolated under agent43 and does not modify the existing AX-7782 scanner.
