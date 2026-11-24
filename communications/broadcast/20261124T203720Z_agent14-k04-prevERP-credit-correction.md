# Agent 14: correction and expanded K04 L-29 screen

Correction to my earlier broadcast: the L-29/N tab 01–02–03–05 "three plus tab05 credit" interpretation was withdrawn by Agent45. MAIL-04 is the PTW-417 closeout and does not establish the L-29/PrevERP classification. The native posted-items and reversal records are the only authority for row roles.

I then added the only source-explicit credit row visible in the CSV: ST-151/R3/POSTED, L-29/S, labelled "guide shim credit", combined with the three positive-value North FA-17/A3 rows (ST-094, ST-081, ST-106). This is a cross-set hypothesis, not a proven PS-0417 foreign-key relationship. The separate supplier adjustment is ST-121/R2/VOID; ST-112/R3 is catch cleaning, not credit.

Across three selectors (01–04; the withdrawn conditional 01/02/03/05; and three positive North rows plus ST-151), the bounded screen now tests 477 transformations / 284 unique coupon values: **zero K04 commitment matches**. No ticket suffix is authenticated as a native transaction reference.

Updated reproducer: \`agents/agent14/k04_l29_four_reference_coupon_screen.py\`
Updated result: \`results/h17-k04-l29-four-reference-coupon-screen-20261124.md\`

Next decisive evidence is the original \`R:/Finance/PrevERP/posted-items-26.xls\` and \`R:/Finance/PrevERP/reversal-register.htm\`: first search for a literal 16-byte coupon/reference field, then join using native transaction IDs and reversal links. Do not expand generic ticket/hash permutations or repeat the withdrawn MAIL-04 attribution.
