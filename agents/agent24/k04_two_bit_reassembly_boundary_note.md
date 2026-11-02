# 2 November boundary clarification

The two-bit reassembly enumerator's `insert1` expression performs a 128-bit left shift when inserting at destination bit 127. Such a shift exceeds the C++ unsigned-128-bit range. Replace the high-half expression with a conditional returning zero whenever the insertion index is 127. All other indices retain their original behavior.

A corrected, targeted re-execution restricted to destination second insertion `b=127` passed its synthetic control, checked exactly **4,129,024** complete original K04 constructions, and found **zero** original commitment matches. This closes the only undefined-shift boundary and leaves the earlier reported overall NO_MATCH unchanged within the defined bit-reassembly model. Original sources and acceptance commitments remain unchanged.
