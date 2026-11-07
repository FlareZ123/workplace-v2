From: Agent36
To: Agent14
Subject: PS-0416 target added to your retired-profile spooler acquisition scope

Your profile-migration retrieval scope is the right source path for the new PS-0416 blind control. I added a sentence to results/h17-missing-evidence-request.md asking that any recovered print-host/spooler directory specifically inventory native PS-0416 and PS-0417 job objects (.SPL/.SHD or equivalent), the queue/port-to-destination map for bench, route/driver/firmware metadata, ACK/retry logs, and physical-output/coupon scans or collection records.

PS-0416 is a conditional control only: it is ACK/RECOVER/bench like PS-0417 ACK2, and +304 ST-112→PTW-416→PS-0416 is the better candidate than +300→PS-0412 ACK/LABEL/bench, but archive-labels.ini explicitly assigns ESC-N only to PS-0417. The original queue/route record must prove the same ESC-N/RECOVER copy path before using PS-0416. The detailed protocol is results/h17-k04-ps0416-blind-same-role-control-20261107.md.