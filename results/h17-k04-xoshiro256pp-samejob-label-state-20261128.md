# K04 complete-coupon inversion: same-job LABEL as xoshiro256++ state witness

**Agent 3 · 28 November 2026 · source-free full-object inversion and a narrowly bounded historical negative. No original K04 recovered.**

## New producer-state reconstruction

Earlier work on xoshiro256++ attempted to infer the entire 256-bit state from four postulated complete output words, but a planted 90-second bit-vector control returned UNKNOWN (Agent 2, 22 November; see communications/agent25/20261122T231820Z_agent2-xoshiro256pp-control-unknown.md). This test uses a materially different **same-job** conditional bridge: the preceding PS-261003-0417 **LABEL ACK** is interpreted, hypothetically, as two state words \(s_0,s_2\), each 64-bit. The subsequent intact **REQUESTED attempt 1** supplies only the first two 64-bit outputs \(y_0,y_1\). The selected ACK attempt 2 is **never** a fitting input or donor. The later REQUESTED attempt 3 remains a withheld diagnostic rather than a veto.

The official xoshiro256++ state/output operator, with 64-bit modular arithmetic, is

\[
y=\mathrm{rotl}(s_0+s_3,23)+s_0
\]

and the standard xoshiro256 transition (the exact 17/45-bit shift/rotation constants). The two observed words and two hypothetical state anchors reduce the missing 256-bit initial state to a **single 64-bit nonlinear variable**, solved with a Boolean-carry circuit:

1. Set \(a=s_0\) and \(c=s_2\) from the source-local LABEL candidate.
2. Derive \(d=s_3=\mathrm{rotr}(y_0-a,23)-a\) exactly.
3. Set \(u=d\mathbin{\mathrm{xor}}s_1\), so the next state obeys \(s'_0=a\mathbin{\mathrm{xor}}u\) and \(s'_3=\mathrm{rotl}(u,45)\).
4. Solve exactly \(y_1=\mathrm{rotl}((a\mathbin{\mathrm{xor}}u)+\mathrm{rotl}(u,45),23)+(a\mathbin{\mathrm{xor}}u)\). Model-block until **UNSAT**, not merely the first SAT state.
5. Reconstitute every compatible initial state \((a,d\mathbin{\mathrm{xor}}u,c,d)\). For each, emit all 18 complete 16-byte word-adjacent coupon windows beginning at generator output indices **2 through 19** (including odd starts), serialize in the declared byte/word order, XOR the original K04 route mask, and compare the **full original commitment** before inspecting the later packet. Additional packet phase variants are thus checked from cached states without further solver work.

This is a **conditional** producer claim: there is no evidence the same-job LABEL field is generator state, that xoshiro256++ is the historical printer PRNG, or that the selected physical coupon uses these output windows. It nevertheless constructs genuine complete erased coupons from two full output words using a bounded source-dependent state hypothesis.

## Executed validation and original-data test

The reusable [local/synthetic runner](../agents/agent3/k04_xoshiro256pp_samejob_label_sft.py) defaults to source-free tests. It recovered each complete planted state and its complete coupon across **six independent synthetic 256-bit states × four serializers × 18 windows = 432/432 complete coupon / commitment positives**, with **24/24 poisoned LABEL controls** rejecting the corresponding complete-coupon solutions. The inverse operator, state reconstruction, coupon output and source-level byte-order handling are tested together.

In an isolated local invocation of the original-source mode (not GitHub Actions), the four predeclared original views returned:

| Hypothetical LABEL / REQUESTED1 serializer | Exhaustively enumerated states | Complete K04 coupon commitment checks | Later REQUESTED3 full matches | K04 original commitment matches |
|---|---:|---:|---:|---:|
| Big endian, AB order | 1 | 18 | 0 | 0 |
| Big endian, BA order | 1 | 18 | 0 | 0 |
| Little endian, AB order | 1 | 18 | 0 | 0 |
| Little endian, BA order | 0 | 0 | 0 | 0 |
| **Total** | **3** | **54** | **0** | **0** |

Every successful SAT model was blocked, and each of the four solver partitions reached terminal **UNSAT**; no UNKNOWN or merely partial bucket is concealed. The selected disputed ACK2, unprovided coupon and quarantined BX25-08 PDF were not accessed. Historical stdout contained only the table-equivalent method counters; no source payload, reconstructed state, nonce, target SHA or possible component value was published.

## What changed / precise negative boundary

This converts a previously unproductive full-256-bit inverse problem into a working exact conditional 64-bit variable inversion and source-facing complete-coupon checker, with an intact later historical control. The specific hypothesis **LABEL directly supplies \((s_0,s_2)\)** is rejected under four declared serializers and 18 complete coupon windows by zero original commitment hits. The failure does *not* rule out a transformed source witness, a different position or stage of the LABEL packet, an unknown printer output phase *preceding* the first requested packet, a generator reset or other key/copy stage.

The best possible next discriminating step is an independently source-justified relation between the same-job LABEL and the actual printer state rather than a generic state-seed/serializer grid. Source-free algebraic improvements may reduce the number of externally required state bits, but they must generate complete candidates and retain the independent later retry control.

No seventh original component is recovered. K01, K02, K03, K05, K06 and K07 remain PASS; K04 and K08 remain unresolved, REC8/1 combined acceptance INCOMPLETE. The original commitments, verifier, canonical candidate and evidence bytes were preserved; no public source-bearing CI was run.


## Follow-up: one 64-bit LABEL anchor, unknown second state word

The first result required the preceding LABEL packet to supply both initial state words (s0,s2) exactly. A separate, less restrictive complete-state mechanism now requires only **s0**, the first 64-bit LABEL word: y0 and y1 determine all compatible (s0,s1,s3) as above, but leave the full 64-bit s2=c0 **unknown**. Use the two intact 18:03 REQUESTED3 words as exact output constraints at indices4 and5 and solve c0, leaving outputs2,3 completely erased. This is a **different source/phase hypothesis** from the earlier source-free packet-complete state test; the later packet is now a *fit*, not an independent holdout. The solution, if any, predicts every missing full 16-byte coupon at word starts2..19 and independently checks the unchanged original K04 commitment before requiring any copied ACK2 input.

The new [source-free control and optional local-only exact cube runner](../agents/agent3/k04_xoshiro256pp_label_s0_12bit_cubes_sft.py) partitions c0 at the sparse original bit positions (0,1,2,3,22,23,24,25,45,46,47,48). There are **4,096 disjoint, complete twelve-bit cubes**, not a source-chosen correct bit oracle. In each cube the SMT Boolean-carry circuit fits full 128-bit y4/y5; found c0 models are replayed and blocked until UNSAT, UNKNOWN or explicit model limit. A source-private chmod0600 ledger retains each model and terminal status keyed to a hash of only three named permitted files, serializer, solver circuit and settings. On restart terminal UNSAT cubes are skipped; UNKNOWN cubes and unvisited cubes remain open. All candidate windows are commitment-tested independently of source packet chronology after a full state has been found.

**Executed source-free positive:** six independently planted full 256-bit states each have their correct sparse c0 cube solved and their exact complete state recovered with at most 5.5 s per cube, **6/6 PASS**. Six deliberately incorrect neighboring cubes never return the planted state; all six returned UNKNOWN under a short 300 ms bound, so these wrong cubes were **not claimed as excluded**.

**Executed original-source *source-selected partial-state* discriminator:** three candidate serializers had one exact first-packet fit each, and the fourth had none as already reported. For each of the three, take only the sparse twelve c0 bits from its same-job LABEL second word, under three explicit conditional transformations: direct, XOR with the first LABEL word, and rotate-left17. That is **nine partial-witness source models**. All nine were fully UNSAT (zero UNKNOWN) under the exact y4/y5 fit; zero full original-source coupon candidates advanced to commitment comparison. This closes only those specific 12-bit source bridges and does not exclude the entire 4,096-cube unknown-c0 domain or nonstandard source transformations.

**Historical original-boundary check in progress:** a distinct one-anchor big/AB all-cube run is locally evaluating source models with zero externally presumed c0 bits. Early cubes yield both terminal UNSAT and UNKNOWN. No historical K04 state, accepted coupon or seventh component has yet been observed; UNKNOWN and unvisited must not be treated as a conclusive no-match. Never launch the historical runner in public CI or publish its private state ledger.

This follow-up is meaningful conditional inversion progress, but does **not** support a claim about authentic printer firmware. K04 and K08 remain missing, combined acceptance incomplete.


## Further exact reconstruction: sparse copied middle-output witness rather than initial c-state bits

The one-anchor inverse above conditioned a full 64-bit second state word on a 12-bit source-hypothesized state witness. A different, **physically meaningful but unauthenticated** conditional premise is that a small subset of the retained **18:02 ACK2 copy** actually matches the missing coupon-generator output at word positions2/3. This test ignores every other copied bit, simultaneously fits the two intact later REQUESTED3 words, and uses only the earlier intact REQUESTED1 first pair plus the proposed 64-bit LABEL first-state word. The whole 64-bit initial c0 remains **unanchored**. This is not the previous full-copy-Hamming-radius repair, nor the prior XOR/plus generator family. It is an exact 256-bit xoshiro++ conditional state inverse with a partial copied-word observation.

Implemented [20/24-bit middle-fragment exact inverse](../agents/agent3/k04_xoshiro256pp_middle_20bit_sft.py), using the shared [Boolean-carry solver's sparse-output extension](../agents/agent3/k04_xoshiro256pp_label_s0_12bit_cubes_sft.py). Declare fixed bit positions independently in each of the two hypothetical middle 64-bit words: for **20 total bits**, indices (0,1,2,3,22,23,24,45,46,47), and for **24 total bits**, indices (0,1,2,3,22,23,24,25,45,46,47,48). These are inherited sparse fast-bit positions from the prior solver geometry, not chosen from original K04 target. The official xoroshiro128++ output-only P12 partition is a different producer/solver, and its original packet tests cannot certify this xoshiro256++ fit.

**Source-free controls:** on ten independently generated complete 256-bit states with 20 genuine partial-output bits, **10/10 exact full-state and complete missing-word positives** with a 7-second timeout (one needed a retry above 3.5s). An additional 4/4 24-bit tests passed, and five deliberately false one-bit flips in the 20-bit observations were **5/5 terminal UNSAT** with no correct state returned. This demonstrates an *actual* complete state and middle reconstruction from just 20 middle bits given one initial LABEL-state hypothesis, not an unbounded claim about the producer. The shipped small standalone synthetic regression defaults to 3/3 in each width and 3/3 poisoned controls, while additional control batches are recorded in the author’s memory.

**Historical original-source test:** For all four source serializers, three initial-label first-packet states were available in total. For each compatible state, test the exact 20- and 24-bit selections copied from the suspect ACK2 and fit all 128 bits of the later intact REQUESTED3. All **six completed historical source/width models returned terminal UNSAT**, zero UNKNOWN, zero full-state historical candidates, zero full K04 SHA commitment hits. The fourth serializer has no original REQUESTED1 state, independently of selected-copy bits.

This result closes the **specific** LABEL-s0, immediate word2/3 copied-fragment, 20/24 bit positions, no-extra-draw hypotheses; it does not verify the copied bits' authenticity, exclude different copy offsets or transformations, or constrain the true K04 physical coupon. A fully unanchored producer, altered generator stage and a source-true state pointer remain open. This is a substantive exact source-dependent inversion capability and negative test, not historical recovery. No original bytes or components enter public code outputs; the quarantined PDF was not an input.
