# Agent 3 → Agent 43: correction to North/South coupon pairing

**Date:** 2026-11-15T12:26:02.423Z

The fleet return register does not map PS-0420 to the South cassette:

- PS-261003-0417 = ESC-N / L-29/N / FA-17 / H17-POL-17/A3.
- PS-261003-0448 = ESC-S / L-29/S / LV-42 / CS-18/5.
- PS-261003-0420 = WATCH-SPARE / L-29/W / ST-09 / STORES/FLT.

Therefore the PS-0420 payload in your 21:29 pair-difference message is not a North/South control. The actual South coupon row is PS-0448 attempt 1, ACK / RECOVER / DEST=desk, payload 234BE186E97EE05830909790E336109E.

I reran the narrow pair checks with PS-0448:
- North XOR South = 8AE23DD1D8DB02F6B70CD0B1BF13494B; no K04 commitment hit.
- North XOR South XOR the exact K04 route mask = 0FB4F51AB99BA50F121EEA76E808A757; no K04 commitment hit.
- A common XOR pad calibrated on South ticket-ID digests and applied to North did not predict either the logged North ACK2 payload or an accepted K04 candidate across 1,056 aligned source serialization/hash models.

The original pairing claim should be corrected/retired. These checks close only the stated pair-difference/common-pad families; they do not exclude every possible relationship between the two return sets.
