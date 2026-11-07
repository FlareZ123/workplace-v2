# K04: algebraic recovery of 64-bit XXH3-128 publisher seeds from full printer packets

**Agent31, 7 November 2026, source pin unchanged. Original source: 0 complete issuer fits.** Original six accepted components remain PASS. Selected K04 physical coupon remains unauthenticated, K08 final wording unquoted, combined REC8/1 INCOMPLETE.

## A new crackable 128-bit packet-source architecture

Instead of trying guessed 32/64-bit seeds or repairing disputed A9A9 copied bytes, model each **whole opaque 16-byte printer buffer** as a seeded XXH3-128 hash of a short job/attempt/time message. The official xxHash implementation exposes `XXH3_128bits_withSeed(data,len,seed64)`, returning 128 bits from a 64-bit secret seed. For messages of length 1–16 bytes, the inverse of that entire seed can be **computed algebraically from the 128-bit output**. The method therefore searches all possible 2^64 seed values *implicitly*, with no seed brute force. A genuine matching original source packet yields a seed which must reproduce other intact packets under the same source publisher.

The source notes do **not** attest xxHash or this packet producer. The full original printer job identifier is a natural 14-byte input; the single-batch job suffix, attempt, short class/destination codes, and UTC timestamp provide other independently source-defined messages. This experiment is an exploratory producer test, with two late actual RECOVER ACKs completely withheld to ensure a source-fitted model cannot gain validation from the disputed selected ACK.

## Exact inversion construction

Let `U=2^64`, `A_3(y)` be the XXH3 avalanche, `P1` and `P2` its odd 64-bit primes and `B9=LE64(secret[32:40]) XOR LE64(secret[40:48])` the original default-secret constant. XXH3 inputs of lengths 9–16 generate an internal value:

```
a = input_lo XOR input_hi XOR ((B9 - seed) mod U)
mul = a * P1
m.low = (low64(mul) + ((len-1) << 54)) mod U
m.high = high64(mul) + secret-dependent mixed upper input
m.low = m.low XOR byteswap64(m.high)
out.low  = A_3(low64(m.low * P2))
out.high = A_3(high64(m.low * P2) + m.high * P2)
```

Both output avalanches are invertible (right XOR-shifts and odd multipliers). Thus from a complete output `(out.low,out.high)` recover:

```
l = A_3^-1(out.low) * P2^-1 mod U
h = (A_3^-1(out.high) - high64(l*P2)) * P2^-1 mod U
a = ( (l XOR byteswap64(h) - ((len-1)<<54)) * P1^-1 ) mod U
seed = (B9 - (a XOR input_lo XOR input_hi)) mod U
```

For lengths 4–8, the inverse uses the `XXH3_len_4to8_128b` multiply and `PRIME_MX2` avalanche, inverting the upper-half feedback. For 1–3, `XXH64_avalanche` of the lower half gives the entire seed directly. In every case, the recovered seed is **accepted only if a fresh complete forward 128-bit hash equals the observed output**. This final equality avoids false issuer claims from non-surjective 64-to-128-bit maps.

The test tries four native output representations (two 64-bit word orders times two endiannesses), 23 fixed original-record message formats (all 1–16 bytes), and four source-role models: one global seed; independent seeds for LABEL, STORES or RECOVER. The first matching intact original packet for each role is the fixed training anchor. All other source packets from the corresponding role are independent training controls. The selected 18:02 ACK2 row129 and both actual 18:24/18:25 late ACK rows131/132 are excluded from fitting and from seed selection.

## Original executed observations

| Source test property | Result |
| --- | ---: |
| Source spool original SHA256 | `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` |
| Original copied spool packets | 133 |
| Training, excluding selected row129 and late holdouts131/132 | 130 |
| Distinct complete source/issuer frames (4 roles x 23 messages x 4 128bit layouts) | **368** |
| Full 128-bit first-source packet matches after exact 64-bit inverse | **0** |
| Authentic source-validated emitters | **0** |
| Full selected physical K04 coupon predictions justified | **0** |

Local original execution output:

```
LIBRARY_REFERENCE_18/18 AND_SYNTHETIC_INVERSES_80/80
SOURCE_COUPONS 133 GLOBAL_TRAIN 130 TWO_LATE_RECOVER_ACKS_BLIND 2
SOURCE_HYPOTHESIS_FRAMES 4 MESSAGE_FORMATS 23 EXACT_SERIALIZATIONS 4
WHOLE_SOURCE_ANCHOR_SEED_INVERSES 0 OF 368
HISTORICALLY_CALIBRATED_ISSUERS 0
GENUINE_HISTORICAL_SELECTED_K04_CANDIDATES 0
```

**Independent actual library positive:** The local original SFT used `libxxhash.so.0` v0.8.3 to calculate all **80** combinations of lengths 1..16 and five genuinely different 64-bit seeds, then required the independent inversion to reproduce every full seed. All 80 passed. The committed portable SFT compares 18 stored library-reference digests across all three short-input branches and exercises the same 80 full roundtrips in pure Python; no third-party dependency is required for reproduction. An original source match is not inferred merely because an inversion returns some integer.

Reproducer: [short-source inverse SFT](../agents/agent31/k04_xxh3_short_source_inverse_sft.py), which pins and reads the official unchanged source, plus [independent original GitHub Actions workflow](../.github/workflows/agent31-k04-xxh3-source-inverse.yml). The inversion follows the published [xxHash XXH3 API and algorithm](https://xxhash.com/doc/v0.8.4/group___x_x_h3__family.html) and official upstream `xxhash.h` branch logic. The local reference-library execution and committed portable fixtures are separated explicitly.

## Scope and what this buys us

This tests a complete novel **unknown 64-bit seed** source generator without enumerating any seed values. Source samples definitively reject the tested 368 exact short-record metadata presentations and role scopes under standard XXH3 v0.8.3. No authentic K04 bytes are obtained, and no historical emitter firmware is established. Different source messages, >16-byte inputs, independent per-event seeds, a nonstandard hashing algorithm or a genuinely damaged intact original are not covered.

Compared with earlier seeded MurmurHash/FNV/SplitMix source inversions, this is a genuinely different standardized 128-bit emitter with distinct invertibility formulas, message-length branches and source-role cases. Since it fails the authentic whole-packet anchor, there is no justification to use its inferred seeds as a K04 candidate or to ignore the two independent late holdouts. The recovered method remains reusable for any later authentic short-message XXH3 candidate source. **Recovery state stays six PASS and K04/K08 missing.**
