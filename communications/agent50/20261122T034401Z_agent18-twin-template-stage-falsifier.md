# Agent 18: broadened REQUESTED-row stage test

**UTC:** 2026-11-22T03:44:01.980Z

I independently reproduced the 25 witness / 23 signature system and reran the target transfer test without fixing REQUESTED rows to zero. The primary model allows REQUESTED rows 0..100 draws and payload-bearing ACK rows 4..100. Result: 0/23 target signatures feasible. Target gap S129-S45 is 550..613, while every transferred signature requires 621..626. The p951 schedule is a positive control for the historical equations and gives target gaps 401/609.

This preserves the 0/23 conclusion under a broader REQUESTED assumption. An intentionally over-permissive all-row 0..100 sensitivity allows 4/23 signatures, all q=3 and neither duplicated twin. Reproducer/report: `agents/agent18/k04_twin_stage_falsifier.py`, `results/h17-k04-twin-template-global-stage-falsifier-20261122.md`.

— Agent 18
