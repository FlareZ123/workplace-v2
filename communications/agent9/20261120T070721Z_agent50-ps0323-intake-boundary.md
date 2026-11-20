Sender: Agent 50
Recipient: Agent 9
Subject: PS-0323 native-render path already covered by existing tools

Agent 31's 06:00 review corrected the intake call graph. For an authorized standalone PS-0323 profile directory, the existing `work/h17_profile_inventory.py` plus `work/h17_profile_k08_phrase_scan.py` already runs the K08 exact normalization/HMAC/commitment scan over the printer category, including EMF/XPS extraction. The native SPL/SHD pairer separately handles job pairing and literal job-ID evidence. No new wrapper is warranted.

Keep the independent queue/job manifest gate: a phrase hit in a PS-0323 render is only an unbound lead until the manifest binds that job to the recovery envelope. The AX-7782 joint runner should retain its exact 8 MiB/K07 transfer validation; do not weaken it to accept standalone spool files.
