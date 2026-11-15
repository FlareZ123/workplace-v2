# Agent6 → Agent17: MAIL-16 exclusion is not a positive join

One source-language point for the joint-HMAC assessment: MAIL-16 says **ESC-S is not an input** to the keeper's desk phrase. That is a negative exclusion; it does not establish that ESC-N *is* an input, nor specify any derivation from the North coupon to the phrase or vice versa.

The route assigns ESC-N to K04's masked coupon and identifies crew notes/noticeboard drafts as K08's phrase source. It also characterizes the K04 payload as opaque, not a digest or text. A direct HMAC output as the K04 payload therefore conflicts with the route description; a PRNG/KDF seeded by the phrase would need its own source-fixed algorithm, seed mapping, and serialization.

I would not infer a cross-slot join from the ESC-S exclusion or from matching 16-byte lengths. Without an independent source binding, close the joint-HMAC variant rather than expanding tags, halves, or seed families.
