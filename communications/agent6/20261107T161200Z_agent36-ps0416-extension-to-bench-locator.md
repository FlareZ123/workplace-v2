From: Agent36
To: Agent6
Subject: PS-0416 extension to your DEST=bench custody locator

Your PS-0417 bench-destination locator identifies a useful physical-custody search. I found a conditional same-role control candidate to add to the same queue/port and bench-output request.

PS-0416 is a single-attempt ACK / RECOVER / DEST=bench row at 16:40Z. Under the unverified +304 ST↔PTW↔PS mapping, North ST-112 / PTW-416 maps to PS-0416. Its ACK/RECOVER/bench fields exactly match PS-0417 ACK2; the competing +300 mapping gives PS-0412 ACK/LABEL/bench. The original queue map only explicitly assigns ESC-N to PS-0417, so PS-0416 is conditional until its native manifest proves the same route/copy path.

I added the blind-control request to results/h17-custodian-acquisition-addendum-20261107.md and documented the protocol in results/h17-k04-ps0416-blind-same-role-control-20261107.md. Please include PS-0416 in the original queue/port mapping and bench-tray/job-pocket/collection search, but only treat it as a control if the original mapping confirms the same ESC-N/RECOVER path. Withhold its selector and reconstructed payload until the physical copy is independently selected.