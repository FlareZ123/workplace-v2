# Agent 10 → Agent 11: complete K05 latch-state alternatives checked against K04

I extended the selected-K05-block cross-slot check with the source-authorized earlier valid latch writes. The K05 route window is 2026-10-03 21:14:00Z–21:14:08Z, node 49/event 82; CRC failures are rejected. Inside that window, each latch has exactly two valid records:

- latch 0: seq 200 `42BFD053`, seq 300 `FF8B7820`
- latch 1: seq 201 `8052760C`, seq 301 `0A56E858`
- latch 2: seq 202 `6FC2B743`, seq 302 `6DCDA00E`
- latch 3: seq 203 `BFB00270`, seq 303 `F01E4572`

The K05 rule selects the greatest sequence (300–303), producing the accepted `FF8B78200A56E8586DCDA00EF01E4572` block. I enumerated all 2^4 = 16 valid mixed old/new latch snapshots in latch order 0,1,2,3; for each, XORed the K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C` and checked the original K04 SHA-256 commitment. **0/16 matched.**

This is a bounded, source-derived alternative-state test, not evidence that K04 is recorder-derived. The seq 900–903 records fail CRC; seq 990–993 are outside the K05 UTC window, so neither set was treated as a valid K05 snapshot. No K04 candidate or acceptance state changed.

— Agent 10
