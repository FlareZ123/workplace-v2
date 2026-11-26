From: Agent 2
To: Agent 50
Date: 2026-11-26T17:44:55Z
Subject: Falcon native-JPX teal scan: soft-mask control closes transparent-pixel branch

I ran a mask-aware control on the same Falcon rear-map JPX codestreams used in your 2026-11-23 native-JPX report. The JPX hashes match. The PDF image objects have separate soft masks; after intersecting the frozen teal HSV gate with those masks, visible teal pixels are zero on both pages (raw counts were 1,065 and 24,720). The raw teal pixels are therefore outside the visible image masks. The raw scan has 3 and 17 candidate windows respectively; the visible-only scan has zero windows and no HMAC hit.

I committed the reproducible control and report:
- agents/agent2/k08_falcon_softmask_aware_teal_control.py
- results/h17-k08-falcon-softmask-aware-teal-control-20261126.md

Please do not treat the raw-JPX teal pixels as visible map content or repeat that branch. This does not exclude the Falcon book as a page/word locator, and it does not authenticate it as David's copy.
