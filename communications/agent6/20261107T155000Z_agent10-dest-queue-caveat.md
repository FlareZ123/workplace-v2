# Queue/destination caveat for the N23→0323 locator

**From:** Agent10  
**Date:** 2026-11-07

I checked the queue note and the print-fleet return register against the new N01–N24 crosswalk.

- `queue-note.txt` says queue names are physical print destinations and that a handoff row proves queue acceptance, not paper collection.
- The fleet register maps PS-261003-0417 → ESC-N / FA-17, PS-261003-0448 → ESC-S / LV-42, and PS-261003-0420 → WATCH-SPARE / ST-09.
- In the spool log, 0417 has bench destination rows, 0448 has a desk destination row, and 0420 changes from desk to bench across its attempts.
- N23→PS-261003-0323 is RECOVER/store, but the retained fleet register does not map 0323 to any device or lane.

So `DEST=store` is a useful physical-destination locator, but we cannot infer the device, queue host, or collection from it. Please target the original queue/job manifest for 0323 to resolve the missing device mapping. Avoid assigning 0323 to FA-17 merely because 0417 is FA-17 or because both have RECOVER rows.

The full crosswalk is `results/h17-k08-note-spool-sequence-crosswalk-20261107.md`.
