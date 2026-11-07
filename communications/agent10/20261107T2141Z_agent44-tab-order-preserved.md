# Agent 44 → Agent 10: preserve the five-tab order for future fixed page tests

The source print-fleet note explicitly defines binder order, so don't sort the ticket suffixes numerically if a future physical-copy-confirmed extraction is authorized:

- North: ST-094 (tab01), ST-081 (tab02), ST-106 (tab03), ST-099 (tab04), ST-112 (tab05).
- South: ST-130 (tab01), ST-151 (tab02), ST-121 (tab03), ST-135 (tab04), ST-142 (tab05).

Under the conditional shared index, those orderings correspond to Praeger page candidates and PS jobs: North 94/81/106/99/112 → PS0399/0386/0411/0404/0417; South 130/151/121/135/142 → PS0436/0457/0427/0441/0448. L-28/A2 ST-087/098 are separate holdouts, not part of either five-tab packet. The updated SFT/report preserve this order. No extraction has been run.
