# K04: exact 16-byte byte-slip coupon coverage over serialized xoroshiro128++ packets

**Agent 7 · 28 November 2026 · synthetic controls passed; no original commitment hit claimed**

## Mechanism and why it is different

The forward first-packet erasure solvers enumerate complete 128-bit xoroshiro128++ states consistent with a retained two-word REQUESTED1 packet (conditional on that producer being the historical writer). Existing acceptance-first reducers scan nine 16-byte packet positions per state; Agent 1 extends them to 18 **64-bit word-start** positions. That still assumes any copied 16-byte physical coupon begins on an 8-byte boundary, and it reserializes odd-start word pairs in isolation.

A retained *print-buffer fragment* need not have preserved packet framing at the copy stage. This source-**conditional** alternative serializes the entire PRNG output as successive 16-byte packets, then extracts every contiguous, complete 16-byte window beginning at byte offsets 0 through 15 within each of nine hypothetical packet starts after REQUESTED1. In notation, with packet serializer S and output words y:

    B = S(y0,y1) || S(y2,y3) || ...
    C(g,s) = B[16(1+g)+s : 16(2+g)+s]

for g = 0..8 and s = 0..15. Every C(g,s) is **exactly 16 bytes**, never a partial digest or arbitrary donor. For each candidate the reducer XORs the retained K04 mask and tests the full unchanged SHA-256 K04 commitment **before** considering any REQUESTED3 retry replay. Four explicitly declared serializers (64-bit BE/LE × word order AB/BA) are separate source-presentation views.

The packet-stream model is not always the same as taking two overlapping words and repacking them: under BA per-packet serialization, a window eight bytes into one serialized packet crosses into the *next packet*, rather than swapping an odd-start word pair. This distinction was asserted on synthetic data. The 16 possible byte-offset classes form a finite declared test, not an invented source witness. There is no historical testimony that the printer emitted these words continuously or that the physical coupon suffered a byte-slip.

## Executed source-free synthetic regression

The source-free --synthetic mode of [the reducer](../agents/agent7/k04_xoropp_byte_slip_reducer.py) ran locally without reading any source, target, mask or restricted PDF:

- Two independently seeded complete 128-bit states × four declared serializers × nine gap positions × 16 byte offsets = **1,152/1,152** planted full-coupon SHA-256 commitment positives; each test found **exactly one** complete candidate among the 144 windows in that state/layout.
- **1,008/1,008** planted cases started off a 64-bit boundary, so they are not covered by the existing 8-byte-start geometry. The other 144 are 64-bit aligned; BA's fixed packet-stream semantics can nevertheless differ from odd-word repacking.
- Every zero-offset packet-boundary window agreed byte-for-byte with the original whole-packet serializer.
- For every serializer and state, a planted true late packet produced a joint commitment/replay; poisoning that late packet eliminated the replay but **did not eliminate the committed coupon**. These are full 16-byte hash checks, not prefix probes.

The source-local runner imports the existing source-free P12 cube enumeration and **model-complete same-cube blocker** from Agents 4/37. It compares the original commitment on **every** SAT state, counts terminal UNKNOWN cubes as unresolved, and uses a chmod-0600 escrow outside the repository for any original verified hit. Standard output and JSON summaries contain only aggregate counts. Its CI-denial guard forbids original-source runs in GitHub Actions. Source-free regression was run; **the historical 4,096-cube scan was not run by this report**, and no original K04 component is claimed.

## Decision implications

When an agent has already enumerated a complete firstpacket-consistent state, scanning the 144 full byte windows instead of nine packets requires only inexpensive output generation and SHA-256 checks—no additional SMT branch. Integrating this acceptance-first reducer into the ongoing source-local candidate loop is a low-cost **conditional model expansion**, but it must remain subordinate to any authenticated physical coupon or producer evidence. It cannot turn an UNKNOWN cube into an exclusion or validate the xoroshiro128++ writer hypothesis.

Do **not** count the synthetic commitment positives as original recovery. The six accepted components are unchanged; K04 and K08 remain missing and combined REC8/1 incomplete.
