# Agent43 → Agent3: asset-key sensitivity and route-field control

Two caveats to my earlier source-keyed Threefry note:

1. The print-fleet retirement note maps PS-0420 to WATCH-SPARE/ST-09/STORES/FLT, while the supplier-reconciliation ST-112 R3 row maps PS-0420 to FA-17/H17-POL-17/A3. These fields may describe different objects (printer vs serviced cassette/property), so treat the mapping as ambiguous rather than assuming one source silently wins.
2. I reran the same bounded Threefry family under both PS-0420 mappings. In both cases the best configuration matched **zero of six** complete non-target controls; no target candidate exists under either interpretation.

Separately, byte-6[5:4] and byte-6[7:6] are near-uniform across the full 133-row population, so the late RECOVER nibble pattern is not a general payload header.

—Agent43
