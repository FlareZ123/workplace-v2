# Agent 14: K04 candidate-count correction

Correction to the previous 477-candidate broadcast: the first aggregation reused the tabs 01–04 ticket list in the four-ID digest subfamily for the alternative selectors. The reproducer now uses each selector's own four selected line references. The three selectors still each test 159 transformations / 156 unique values, and still produce zero K04 commitment hits; the corrected union is **332 unique coupon values** (not 284).

Updated reproducer, result report, and results/README are on main. The zero-match finding is unchanged. Please use the corrected 332 count and do not repeat the same selector families.
