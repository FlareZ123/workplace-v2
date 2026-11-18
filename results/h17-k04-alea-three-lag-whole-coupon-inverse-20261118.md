# K04: direct Alea/MWC3 missing-middle coupon reconstruction from original late printer flanks

**Agent 16 | 18 November 2026 | original source incompatible in the stated native-output model; K04 remains missing.**

## Why this was tested

The 128 ordinary printer buffer lines use UTC offsets of the form `+00:00`, while the five exceptional late entries use `Z` timestamps. This is compatible with separate text emitters and motivates one **exploratory** JavaScript-producer model. It is not evidence that the historical printer used JavaScript, or that the unusual suffix carries any coupon bytes.

Johannes Baagøe's **Alea** pseudorandom generator, distributed in David Bau's `seedrandom` JavaScript package, has an unusually useful exact inversion: four successive native 32-bit outputs suffice to recover the carry and generate all future output words. Unlike generic seed-list checks, this is **seed-free, exact, complete-state recovery** for its specified four-fullword packet representation.

## Exact erasure inversion

For Alea's three-lag multiply-with-carry recurrence let \(A=2{,}091{,}639\), \(Q=2^{32}\), and \(y_i\) be the full 32-bit output word at index \(i\). Then

\[
t_i=A\,y_{i-3}+c_i,\quad y_i=t_i\bmod Q,\quad c_{i+1}=\lfloor t_i/Q\rfloor .
\]

For the first four intact full words \(y_0,y_1,y_2,y_3\), the carry before the fourth output is uniquely determined by

\[
c_3=(y_3-Ay_0)\bmod Q.
\]

A valid Alea state requires \(0\leq c_3<A\), which is a rigorous source-only prerequisite. If it holds, calculate \(c_4=\lfloor(Ay_0+c_3)/Q\rfloor\), then recurse to produce the entire missing attempt-2 packet \(y_4,\dots,y_7\) and independently predict the attempt-3 packet \(y_8,\dots,y_{11}\). Each candidate coupon is XORed with the **unchanged** original K04 mask and its full SHA256 checked against the **unchanged** acceptance commitment.

The source serializer is uncertain, so enumerate all \(4!=24\) four-word permutations and all \(2^4=16\) independent per-word byte-endianness choices: **384 complete packet interpretations** for each original control. No source-derived seed, guessed state prefix, copied ACK2 bytes, or target-dependent pruning enters this test.

## End-to-end whole-packet positive

Create twelve actual Alea/MWC3 32-bit output words from the planted initial words `10203040,50607080,90A0B0C0` and carry `123456`. Serialize each consecutive four-word packet with permutation `(2,0,3,1)` and byte-flip mask `0b1010`. Hide the **entire selected middle 16-byte packet** before inversion. The first packet alone reconstructs the correct carry, missing whole coupon `838BAE8B7C03C265232B4E2AEBB73072` and all later words. The third heldout packet agrees exactly; the reconstructed middle packet also reproduces the planted synthetic SHA256 of its coupon-XOR-mask component.

This tests real erasure recovery and the downstream component check rather than replaying a known middle packet.

## Original-source result

Unmodified `resources/evidence/print/spool-reconstruction.log` SHA256:
`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

| Original independently selected full packet | Native Alea carry-consistent views / 384 |
| --- | ---: |
| PS-261003-0417 attempt 1 REQUESTED, 18:01 UTC | **0** |
| PS-261003-0417 attempt 3 REQUESTED, 18:03 UTC | 8 |
| PS-261003-0448 attempt 1 ACK, 18:24 UTC | **0** |
| PS-261003-0420 attempt 2 ACK, 18:25 UTC | **0** |

The eight views for attempt 3 are accidental compatible initial packets under the single carry test. They do not supply an earlier state or establish a producer. **The actual attempt-1 first packet has zero valid views**, so the native Alea model cannot reconstruct the intervening physical selected coupon from its historic same-job predecessor, even before comparing the independent third packet or K04 commitment. The copied selected `PS-261003-0417` attempt-2 `A9A9...` ACK payload was **excluded** from state fitting, as required by the original source's media-integrity warning.

**Original K04 component acceptance hits: 0.** K08 still lacks its exact Emily author-final envelope text; the canonical six PASS slots and combined incomplete status remain unchanged.

## Reproducer and boundary

[Portable source-pinned one-file SFT](../agents/agent16/k04_alea_native_middle_sft.py), Python standard library only. Run it from a repository checkout; it reads `resources/evidence/print/spool-reconstruction.log`. A local execution against the exact original ZIP-extracted file yielded the four counts above and passed the fully erased-middle positive. Reference algorithm: [David Bau's MIT-licensed `seedrandom/lib/alea.js`](https://github.com/davidbau/seedrandom/blob/released/lib/alea.js), derived from Johannes Baagøe's 2010 Alea.

This excludes the explicit **four consecutive full 32-bit Alea outputs per packet** model, across the declared 384 byte layouts. It does not exclude other producer families, **top-byte-of-16-draw** Alea serialization, per-event reseeding, altered packet staging, corruption of original REQUESTED copies, or a physically authentic ESC-N coupon outside this export. Extending this failed native-fullword model with speculative seed dictionaries would have no predictive advantage. An actual independent original selected ESC-N coupon or final desk-margin text remains a higher-value source than another arbitrary issuer model.

## Independently source-controlled Alea event-seed/byte-output branch (18 November)

The exact four-native-word inversion above does not cover **16 successive high-order bytes**, a common way to serialize a JavaScript generator. Agent16 implemented the actual published `seedrandom/lib/alea.js` Mash seed initializer (including floating-point updates), then tested this remaining issuer under concrete retained event metadata. For each of the two **intact late RECOVER ACK peer packets**, build the same 515 distinct metadata-derived seed strings from historical JOB ID, suffix, route, timestamp (native Z / ISO offset / epoch second / millisecond / condensed), ATTEMPT, STATE, CLASS and DEST fields. Test the first **512** offsets under five output views: sixteen consecutive high bytes or four 32-bit words (little/big endian, natural/reversed word order).

This yields **515 x 512 x 5 = 1,318,400** complete-packet comparisons **per peer**. Independently: 

| Original intact peer | First-four-byte matches | Complete 16-byte packet matches |
|---|---:|---:|
| PS-261003-0448 ACK/RECOVER 18:24Z | 0 | **0** |
| PS-261003-0420 ACK2/RECOVER 18:25Z | 0 | **0** |

The real historical `Alea("seed1")` published-word fixture passed. A separately planted **whole 16-byte packet**, generated from the source-shaped seed `PS-261003-0448|2026-10-03T18:24:00Z|1` at offset17 with reversed little-endian words, was recovered uniquely in a 64-offset positive-control search; its first-four-byte prefix occurred twice, but the full packet matched once. The selected disputed ACK2 copied content was never treated as a control. Hence this branch provides **no source-selected original K04 coupon**, and no K04 acceptance check was warranted. This is a finite **literal event-seed** negative; arbitrary unknown keyed or separately secret-seeded Alea byte emitters remain outside it.

[Source-pinned portable event-seed SFT](../agents/agent16/k04_alea_event_seed_sft.py). Two peer original-source jobs each checked 1,318,400 complete outputs locally, all zero; planted source-shaped producer recovered. Retain the distinction between the exact 384-view seed-free native fourword exclusion and this separate finite text-seeded high-byte hypothesis. Both are narrower than a claim that no historical Alea-based printer stage could exist.
