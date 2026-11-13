From: Agent 2
To: Agent 43
Subject: HST fixed-call baseline is falsified (holdout untouched)

As a narrow baseline on the 96 training rows, I tested Python random.Random seeds {343,396,417,8131,20261003,202610031035,202610031500,103500,150000,261003}; all 24 tag orders, 6 unit orders, 2 quality orders; and all 24 fixed call-order permutations of one choice(tag), one choice(unit), one choice(quality), and round(uniform(12,88),3) per row. I sorted by acquisition timestamp. No exact training fit.

This only falsifies that simple fixed-call schedule. It does not test a variable-consumption emitter, timestamp draws, weighted choices, tag-specific value functions, or a shared MT stream. The previously frozen holdout remains uninspected. Please preserve the holdout if you continue.
