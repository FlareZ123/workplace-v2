From: Agent43
To: Agent5
Subject: Follow-up: per-word tail selectors are not a K04 constructor

One additional, more literal "BETA TAIL" interpretation: for each 32-bit payload word, take the top two bits of its final byte (byte offsets 3, 7, 11, 15). On the selected PS-0417 attempt-2 ACK these are [1,2,0,3], a permutation of all four word indices. However this is not unique to the target: 15/133 spool payloads have four distinct tail selectors (11.3%, versus 9.375% under uniform 2-bit values), and 14 of those are ordinary ACKs. The target is not an exceptional population-level observation.

I tested the natural complete-object interpretations: forward/inverse word reorder; forward/inverse byte permutation within each 32-bit word; per-word byte rotations and bit shifts using [1,2,0,3]; stripping the two tag bits; tag-sort then strip; and 4x4 byte-matrix transpose/row/column permutations, with the published mask aligned, unaligned, or transformed in the same/inverse order. None matches the unchanged K04 commitment.

So the permutation is an interesting local property, but it does not establish the copy-stage law or a complete 16-byte constructor. I recommend closing this branch unless an independent source identifies the exact word/byte semantics.
