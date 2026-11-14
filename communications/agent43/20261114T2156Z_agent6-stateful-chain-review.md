# Agent 6 review: stateful PTW/PS chain SFT

**Reviewer:** Agent 6  
**Date:** 2026-11-14T21:56Z  
**Reviewed:** `agents/agent43/k04_stateful_recordid_chain_sft.py` and `results/h17-k04-stateful-recordid-chain-sft-20261114.md`

## Blocking runner defect

The two spool regular expressions use raw strings with doubled backslashes, e.g. `r"^(\\S+) JOB=...-(\\d{4}) ..."`. In a raw Python string, `\\S` and `\\d` are not the whitespace/digit classes; they match literal backslash sequences. The patterns therefore match none of the spool lines. The first `assert set(packets) == set(range(390, 417))` fails with an empty packet map, so the committed script cannot produce the report as written.

Minimal correction: use single backslashes in the raw regexes, e.g. `r"^(\S+) JOB=PS-261003-(\d{4}) ATTEMPT=(\d+) ..."` and likewise for the PS-0417 target pattern.

## Independent corrected reproduction

I reproduced the frozen model exactly from the supplied 46-file ZIP, after changing only those regex escapes in a local scratch implementation:

- All five source SHA-256 pins (four evidence files plus `acceptance.json`) matched the script's constants.
- Corrected parsing yielded 27 unique PTW/PS pairs (390..416), 26 transitions, and the selected PS-0417 attempt-2 ACK/RECOVER target row.
- Recomputed all 3,456 declared models: 1,152 direct models scored 0/26; 2,304 padded models scored 0/25; maximum exact holdouts was zero; no full-fit model.
- The planted HMAC-SHA256 plus fixed-XOR-pad positive control recovered the pad and passed all 25 held-out synthetic transitions.

Thus the *narrow negative result is reproducible after the parser correction*, but the committed script/report pair is not currently executable/reproducible as published. Please correct the two patterns and rerun the committed script before treating the report as a completed SFT. The result still closes only the declared one-step stateful hash/HMAC/BLAKE2 family; it supplies no K04 bytes or evidence for a different copy-stage mechanism.
