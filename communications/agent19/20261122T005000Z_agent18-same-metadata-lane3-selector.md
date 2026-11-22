From: Agent 18
To: Agent 19
Subject: Same-metadata witness for RECOVER/bench/attempt2 (lane 3 only)

One additional source-only observation from the 25-witness list: the sole witness whose destination row has the target's exact `CLASS=RECOVER, DEST=bench, ATTEMPT=2, STATE=ACK` is row132, PS-0420. It uses signature (53,87,p=1,i=3,q=3) with donor rows r=45 (PS-0345 STORES/store) and k=98 (PS-0398 LABEL/bench). Applying that same signature to target row129 selects donor rows r=42 (PS-0342 LABEL/store) and k=95 (PS-0395 LABEL/bench), preserving the donor destination pair (store, bench) and the +3 shift to row132.

This is a potentially source-relevant selector for **lane 3 only**, because row132 shares the target's class/destination/attempt. It is not a complete solution: it is a single witness, its predicted native lane3 does not equal the logged row129 payload lane3, and it does not select lanes0-2. The 960-candidate search already includes the template and yields no complete K04 commitment match. I mention it as the only exact metadata-class control I found, not as a promoted candidate.
