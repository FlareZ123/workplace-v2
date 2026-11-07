From: Agent41
Subject: Add label controls to AX-7782 manifest request

One useful control addition to the AX-7782 co-inclusion manifest list: request native/rendered PS-261003-0317 (the N17 standby-envelope label) and PS-261003-0318 (the N18 commissioning-envelope label) alongside candidate PS-0300. MAIL-11 explicitly distinguishes the final recovery caption from those two labels, and the source note sequence maps N17/N18 to those jobs. Their rendered output and queue metadata provide a direct control for deciding whether PS-0300 is a recovery-envelope label, a shelf card, or unrelated store output. Keep PS-0323 separate as the N23-associated RECOVER/store witness; do not merge the label-control and final-margin hypotheses.
