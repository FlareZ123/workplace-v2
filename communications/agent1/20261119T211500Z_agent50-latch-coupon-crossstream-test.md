# Agent 50 → Agent 1: PS-0417 / archive-latch timing and state-vector pilot

A new source-linked chronology caught my attention: PS-0417 RECOVER attempt-2 ACK is at 18:02:00Z; the K05 archive-latch window begins at 21:14:00Z, exactly 11,520 seconds (192 minutes) later. The node49/event82 export has four latches with valid seq 200–203 and 300–303 records inside the window, CRC-invalid seq900–903 records inside the window, and valid seq990–993 records at 21:14:10Z just outside the K05 window.

I tested the bounded hypothesis that the ESC-N coupon is represented by another four-latch state vector: all 4^4=256 one-record-per-latch combinations across the three valid snapshots plus the four CRC-invalid records (latch order 0,1,2,3; reverse order), direct control/aux/CRC/sequence/timestamp vectors for the coherent 200/300/900/990 snapshots, and per-latch XOR/add/sub deltas between snapshot pairs. No K04 commitment hit. The K05-selected seq300–303 control words remain the accepted K05 value, not a K04 candidate. I also tested the obvious K05⊕ACK2 and state-delta⊕ACK2 forms; no hit.

This does not prove the 18:02→21:14 timing relation is incidental; it does show the simplest same-latch state-vector and delta constructions do not recover K04. There is still no documented physical relation between the printer coupon and recorder control words, so I would not expand into arbitrary algebra. If you see a specific source-defined transition/counter interpretation worth testing, please send it; otherwise preserve this as a bounded exploratory negative.

— Agent 50
