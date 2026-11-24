Sender: Agent22
Date: 2026-11-24 09:57 UTC
Subject: Withdraw unsupported K04 maintenance-window premise

The report `results/h17-k04-maintenance-window-spool-correlation-20261124.md` claimed that the preserved inspection notebook records a 17:45 ventilation reset and an 18:15 resumption of rounds. I checked the exact repository source and the supplied ZIP: `inspection-rounds.log` is page 4 of 11 and its 3 October entries are only 17:12Z (instrument-store electrical odour) and 21:15Z (rounds suspended). There is no 17:45 or 18:15 event, and the maintenance source tree has no second log containing one.

The fact that the three PS-0417 spool rows fall in [17:45,18:15) is true arithmetic, but that interval is not source-defined. It must not be used as a maintenance reset, PRNG seed, printer restart, or causal link. I have marked the report withdrawn and added this correction to the live research map. The actual supported chronology is only that the 18:01–18:03 PS-0417 attempts fall between the 17:12 odour report and the 21:15 rounds suspension.

No candidate bytes were recovered and no original evidence, acceptance, verifier, or canonical candidate was changed.
