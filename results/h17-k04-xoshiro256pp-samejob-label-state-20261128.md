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
