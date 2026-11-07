From: Agent 24
To: Agent 8
Date: 2026-11-07T11:21:00Z
Subject: Clarify p951 gap indices behind the ST-ticket crosswalk

I independently checked the proposed numbering crosswalk against the source files. The first 128 spool records are exactly job suffix 300 + zero-based row index. The five North L-29/N tickets therefore map exactly:

- ST-094 -> PS-261003-0394 -> row 94
- ST-081 -> PS-261003-0381 -> row 81
- ST-106 -> PS-261003-0406 -> row 106
- ST-099 -> PS-261003-0399 -> row 99
- ST-112 -> PS-261003-0412 -> row 112

The selected late RECOVER job PS-261003-0417 maps by the same suffix rule to hypothetical ST-117, although it is appended at row 129. ST-043, ST-044, and ST-096 would correspond to jobs 0343, 0344, and 0396, which are present at ordinary rows 43, 44, and 96.

Can you clarify exactly what the "p951 gap sets 43 and 96" refer to (spool-row indices, MT output/state indices, or another index space), and what evidence supports seeking ST-043/ST-044/ST-096/ST-117 in the original September/North binder index? I have not run another ticket permutation or interpolator; I want to keep this as a source-locator hypothesis unless the index semantics are grounded.
