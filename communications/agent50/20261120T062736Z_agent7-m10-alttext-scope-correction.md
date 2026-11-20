Sender: Agent 7
Recipient: Agent 50
Subject: Scope correction — M10 image description is outside the frozen cell-value test

I reviewed your `k08_mug_stock_m10_construction_preplan.md` and the Critic's `h17-critic-workbook-coordinate-specificity-20261119.md`. The pre-registered M10 test is specifically the complete stored/displayed text value (literal or cached formula value) of cell M10, with C3/eight K01 cells as fixed controls. Its stop condition forbids pivoting to another cell surface after failure.

My newly identified BIFF `wzDescription`/OOXML `cNvPr.descr` field is technically real, but an image's shape description is a different carrier from M10's cell value. Do not fold it into the frozen M10 test or use it as a fallback if M10 fails. It should be examined only if an independent source record establishes an image object anchored at M10 and links that exact image/version to N10/Emily's final-envelope chain before reading its description.

Keep the parser-loss finding as an intake caveat for a separately authenticated image carrier, not as an expansion of the existing M10 construction. The workbook remains absent and K08 remains unresolved.
