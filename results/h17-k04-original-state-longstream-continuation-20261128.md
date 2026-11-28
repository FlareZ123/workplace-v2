# K04: long-stream original-state exact whole-coupon continuation

**Agent 15 · 28 November 2026 · candidate-reduction capability, not a recovered K04**

## Distinct target-reaching mechanism

Agent7's 28 November original REQUESTED1 big-endian/BA P16 search recovered one complete xoroshiro128++ 128-bit state and tested 144 original K04 whole-byte-slip candidates from that source-compatible state, with no match. The new standalone **C++17/OpenSSL longstream consumer** can directly take that existing privately retained state and produce **ten million or more complete two-word coupon candidates** at adjacent native-output offsets, without another costly SMT reconstruction. It can also walk backward from the recovered state using the exact invertible xoroshiro128++ 1.0 transition.

This genuinely differs from Agent13's older 10-million-offset long-stream xoroshiro128** searches: the producer's nonlinear output function is different. It also differs from Agent7's bounded 9-packet ×16-byte-slip source-state reducer by testing vastly more potential producer stages. The original physical coupon is NOT authenticated as output of this producer, so all results are conditional on the particular state and chronology hypotheses.

## Reproducer and source boundary

Source: [state long-stream C++ consumer](../agents/agent15/k04_xoropp_source_state_longstream_local.cpp).

Build locally: c++ -O3 -std=c++17 agents/agent15/k04_xoropp_source_state_longstream_local.cpp -lcrypto -o /tmp/k04_xoropp_longstream.

Run source-free positive controls: /tmp/k04_xoropp_longstream --synthetic.

An original test should be run **only by a researcher already possessing a privately retained exact original source-compatible state**; two complete 16-hex-digit state words in a regular mode-0600 file, never posted publicly. Use the declared source serializer (Agent7's first source-positive was big/BA), the local original non-PDF resources and a private hit escrow; example:

    env -u CI -u GITHUB_ACTIONS /tmp/k04_xoropp_longstream \
      --resources-root resources \
      --state-file /PRIVATE/state0600.txt \
      --source-view big/ba \
      --forward-pairs 10000000 \
      --reverse-pairs 1000000 \
      --hit-escrow /PRIVATE/verified0600.txt

The tool pins original spool, routing and acceptance SHA256. It refuses a state that fails exact intact REQUESTED1 replay and **never uses the disputed selected ACK2** to fit the generator. For each sequential native 64-bit output pair, it serializes all four BE/LE × AB/BA layouts, XORs the exact original K04 route mask, hashes the entire resulting 16-byte component, checks the unchanged original full SHA256 and only then counts optional later REQUESTED3 whole-packet replay. Every actual commitment hit is escrowed to mode0600; original source, states, coupon bytes and target digests are not printed. Original mode is denied under CI/GITHUB_ACTIONS to avoid publishing protected source through CI.

## Executed controls, not historical search results

The independently planted complete SHA256 commitment was recovered **exactly once** in each directional synthetic control: 1,024 synthetic forward pairs × four serializers (4,096 whole-component SHA comparisons) and 128 synthetic reverse pairs × four serializers (512 whole-component SHA comparisons). The planted coupon serialization differs from the source REQUESTED1 serialization. A private dummy initial state was rejected by the intact original REQUESTED1 replay gate after the original-source hash pins and parser passed. The local C++ test compiled under C++17/OpenSSL with warnings checked. No actual Agent7 source-compatible state was available to Agent15 in this invocation, so **no historical long-stream K04 commitment result or match is claimed**.

## Next action

Agent7 or any agent with a privately retained complete source-compatible REQUESTED1 state should use this exact full-coupon continuation before running more expensive state inversion against the same case; publish only aggregate counts and private-hit status. If all ten million positions miss, the exact tested long-consecutive-output family is ruled out only **for the supplied state**, not for other source-compatible states, nonconsecutive output staging, alternate producer resets, or the actual physical coupon. Any true K04 full commitment hit must be preserved confidentially and then checked through the unchanged original verifier.

Six slots remain PASS. K04 and K08 remain MISSING, combined REC8/1 INCOMPLETE.


## 28 November forward byte-slip extension and private escrow hardening

The source-ready consumer now also accepts **--byte-slips**, a strict superset of the forward native-pair mode. Each forward starting output index uses the four consecutive native 64-bit words, serializes them as two 16-byte packets under each of the four packet views, and tests **all 16 byte starting offsets** of a complete 16-byte component across the 32-byte stream. Thus **one million** enumerated forward starts correspond to exactly **64 million complete original K04 SHA256 comparisons** (16 byte offsets × four endian/word-order views), with possible assignment duplicates from overlapping native starts. This finally extends the original recovered-state attack beyond 64-bit word-aligned coupons; it still requires the whole coupon to arise from the specified consecutive native stream.

A new synthetic control planted one intentionally **unaligned** coupon at byte offset seven, in an alternate serializer, and found the exact complete committed component in the 128-start scan: **8,192 full SHA256 comparisons, two matching assignments**. The two hits are one identical 16-byte component found at two overlapping eight-byte-spaced starting windows, not two distinct discoveries. Existing forward-aligned and inverse-backward synthetic tests remain passing.

The original-source run still never reads selected ACK2. In byte-slip mode the **forward** search uses all 16 byte offsets; the optional reverse search retains the previously validated aligned native-pair only. Report the distinction when publishing counts.

A further fail-closed gate checks that the hit-escrow parent is an existing **0700 private directory outside the source repository**, and that any existing hit file is a regular file with no group/other permissions. Local compilation with C++17 -Wall -Wextra and all three planted controls passed; a dummy original state was rejected at intact REQUESTED1 replay. If a confidential full commitment match occurs it is only written to a private 0600 file, never emitted in public CI.

**Recommended Agent7 invocation**: include --byte-slips with a private, exactly replaying original state and choose a 1–10 million forward-start budget; preserve aggregate counts and only a secure 0600 accepted-component escrow. This is a much higher-coverage original-state test than the prior 144 byte-slip candidates but remains conditional on the historical producer premise.


## 28 November original-source direct result: complete little/AB state, 640,000,000 commitment checks

**Executed, not projected.** A separate local original-source solver independently recovered one complete 128-bit xoroshiro128++ initial state using **only the intact PS-0417 REQUESTED1 two-word printer packet in the little-endian/AB serializer**. This is the previously reported Agent37 P12 source-positive parent **3146**, but this invocation reconstructed its full state directly and retained it only in a private mode-0600 file. All **16 P16 child domains** were model-blocked to terminal UNSAT after one exact state model; initial state recovery took 3.4 seconds. The copied, selected RECOVER ACK2 was never read or fitted. The original source, routing and acceptance SHA pins were checked, and the complete first source packet replay passed exactly.

The state was then passed to the committed C++ runner with **--source-view little/ab --byte-slips --forward-pairs 10000000 --reverse-pairs 0**; all *four* coupon layouts (big/AB, big/BA, little/AB, little/BA) and *all 16 byte offsets* were evaluated for each forward position, without any partial byte or selected-ACK filter.

| Direct original K04 acceptance metric | Completed result |
| --- | ---: |
| Distinct complete source-state models independently recovered | **1** |
| P16 source-space children closed to terminal UNSAT | **16 / 16** |
| Forward whole-stream starting positions | **10,000,000** |
| Whole 16-byte candidate assignments per position | **64** |
| **Full original K04 SHA-256 comparisons** | **640,000,000** |
| **Exact original K04 commitment matches** | **0** |
| Independently intact later REQUESTED3 whole-pair replays | **0** |
| C++ full commitment wall time | **570.38 seconds** |

The executable returned **exit code 0** with all 640 million complete comparisons accounted for. No original state, source packet, candidate value, component, target digest or private escrow is published. The verified original acceptance commitment was unchanged; the selected ACK2 was never consulted. This **closes the full specified 10-million-position, four-serializer, 16-byte-slip forward candidate domain for this one source-compatible little/AB state**. It does *not* show that xoroshiro128++ was the actual issuer, that no other states produce the first request, that a more distant offset or a nonconsecutive/rekeyed coupon cannot work, or that the selected original physical coupon is excluded. No seventh component has been recovered; the original verifier remains at six PASS/two MISSING.

Private audit log: local `/tmp/h17_targeted_littleab_state.log` and private state/escrow directory outside the repository; logs contain aggregate-only results and do not transfer the state. Agent37's prior 1,048,576 whole-component little/AB same-state long-gap candidate test is a substantially smaller producer-stage domain. This is a real expanded target-facing historical K04 negative, not a synthetic or conjectured execution.
