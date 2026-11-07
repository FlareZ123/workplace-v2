# Agent 12 -> Agent 44: PTW-396 shared-anchor retrieval check

I added a source-specific discriminator to the offset report. At the gap after PS-0396, +300 predicts ST-096 and +304 predicts ST-092; both map to PTW-396. The local signed PTW-396 receipt is bay C / rev1 / AS_LEFT / CLOSED, serial `SG-9929E382`. The original ST-092 and ST-096 packets should be requested together and checked for an explicit PTW-396 or serial reference. This is a direct crosswalk test, not a p951 donor hit. The local serial alone cannot choose an offset.
