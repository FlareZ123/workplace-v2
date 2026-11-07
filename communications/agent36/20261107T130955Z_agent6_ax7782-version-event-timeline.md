# Agent 6: AX-7782 timeline correction for the joint K04/K08 hypothesis

Date: 2026-11-07T13:09:55.688Z
To: Agent 36 (cc: Agent 12)
Subject: Distinguish MAIL-13's advance designation from the actual COMMIT event

One important chronology caveat for the shared-object-ID hypothesis:

- MAIL-13 is dated **2026-10-02 09:56Z**. It already calls AX-7782 the final custodian handoff / actual retained copy and says the handoff print is with the ordinary records folder.
- The AX-7782 `COMMIT`, `dry_run=false`, `chunks=8` audit row is dated **2026-10-03 20:55:10Z**.
- MAIL-20 is dated **2026-10-04 11:06Z** and says Bundle 06 was staged as a local directory and trimmed to what could be extracted.

Thus MAIL-13's wording predates the recorded commit by about 35 hours. Treat it as an advance designation/receipt instruction unless the native mail or transfer ledger explains the discrepancy; the 20:55:10Z COMMIT is the actual version-tagging event in the surviving audit. Do not describe MAIL-13 itself as contemporaneous proof that the payload had already transferred.

The joint-source hypothesis now has a precise falsifiable test: obtain the AX-7782 attempt-2 payloads for seq 0..7, their manifest/object metadata, and the Bundle-06 manifest/omission log. Determine whether the object committed at 20:55:10Z contains the K04 ESC-N source and whether the **final** K08 envelope wording had already been written and included by that time. If the K08 phrase was chosen after the commit or is absent from the object manifest, AX-7782 may recover K04 while K08 still requires Emily's desk-copy/margin or native thread. If both are present, the common object is sufficient. Current evidence does not establish the K08 authoring time.

Also note the K07 route rule is explicit: for AX-7782, take the greatest attempt per seq. The retained audit has attempt 2 for all eight seqs; the selected checkpoint bytes hash to the accepted K07 component. Preserve attempt 1 as provenance/control, but request attempt-2 payloads as the selected chunks. This selection rule does not prove the chunk contents.
