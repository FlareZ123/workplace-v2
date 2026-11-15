# K04 North return-set Merkle/XOR commitment: bounded negative

**Agent 5 — 15 November 2026**

## Question

The print-fleet register maps `PS-261003-0417` to logical route `ESC-N`, return set `L-29/N`, account `FA-17`, and filing reference `H17-POL-17/A3`. Its binder index enumerates five tabs, and the supplier reconciliation contains one matching `R3/POSTED` row for each ticket. Could the 16-byte escrow coupon be a 128-bit commitment to that five-ticket set?

This is a source-linked hypothesis, not a rule stated by the surviving records.

## Method

The read-only script `work/h17_k04_north_ticket_merkle.py` reconstructs both five-ticket sets from the original fleet note and supplier CSV. It tests six consistent leaf encodings:

1. ticket ID;
2. full CSV row, pipe-delimited;
3. ticket ID, amount, description;
4. tab, ticket ID, part, return;
5. tab, ticket ID, part, return, amount, description;
6. canonical JSON of the joined record.

For each encoding it tests SHA-256, MD5, BLAKE2s-128 and BLAKE2b-128 leaves, with duplicate-last, promote-last, zero-pad and RFC 6962 tree shapes. SHA-256 roots are tested as first and last 16-byte halves; 16-byte roots are tested whole. It also tests XOR accumulation of per-ticket digests (first/last halves where applicable). Every North coupon is checked both directly and after the prescribed K04 route-mask XOR against the unchanged full slot commitment.

The parallel `L-29/S` set and its `PS-261003-0448` RECOVER ACK payload are used as a holdout/control. The K04 mask is applied to this control only as a diagnostic; no South-route mask is asserted. A planted synthetic coupon passes the same masked SHA-256 checker.

## Result

- North set: 90 distinct Merkle coupons and 30 distinct XOR-digest coupons; 240 direct/masked K04 component checks; **zero K04 commitment hits**.
- South holdout: zero matches to the exact RECOVER ACK payload under the same bounded Merkle/XOR coupon family, direct or with the K04 mask.
- Synthetic masked-commitment positive control: **PASS**.
- No candidate, acceptance commitment, verifier, or CI workflow was modified.

## Interpretation and limit

The computation excludes only these conventional ticket-set Merkle/XOR commitment presentations. It does **not** establish that the historical coupon was generated from the five tickets, nor does it exclude keyed/vendor-specific constructions or a source-native printer process. The surviving records establish the North job/set association, but do not attest a Merkle or XOR-set coupon algorithm. Do not expand serialization/tree permutations without a new source clue.

The useful next discriminator remains the original `PS-261003-0417` native spool/queue journal or independent physical coupon witness.
