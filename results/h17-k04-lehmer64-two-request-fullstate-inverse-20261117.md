# H-17 K04: invert the complete 128-bit Lehmer64 state from two 64-bit retry outputs

**Agent 18 | 17 November 2026 | source-conditioned whole-coupon reconstruction hypothesis, excluded within the stated one-million-output window.** Six original slots remain PASS, K04 and K08 remain MISSING, and combined REC8/1 remains INCOMPLETE.

## Distinct complete-candidate mechanism

The supplied original printer reconstruction has the same PS-261003-0417 job's 18:01 UTC attempt-1 REQUESTED and 18:03 attempt-3 REQUESTED, each containing 16 retained payload bytes. The selected 18:02 attempt-2 ACK payload has unverified copy integrity and is withheld completely while fitting. No record establishes that these two REQUESTED payloads were genuine consecutive outputs of a Lehmer PRNG, so this is an exploratory emitter test.

Model a 128-bit multiplicative Lehmer64 state:

```text
M = 2^128, B = 2^64
A = 0xDA942042E4DD58B5   (the standard 64-bit Lehmer multiplier)
X[i+1] = A * X[i] modulo M
Y[i] = floor(X[i] / B)     (top 64 bits emitted)
```

A printer payload is two consecutive outputs Y[i],Y[i+1], packed as two raw 64-bit words. Test big/little endian and both whole-half orders (four original packet views).

Unlike a generic 128-bit state search, two consecutive observed 64-bit outputs **invert the entire state exactly**. Given Y0=H and Y1=J, let `D = (J - A*H) mod B`. The unknown 64-bit low half L of X0 must satisfy

```text
D = floor(A*L/B)
0 <= L < B
ceil(D*B/A) <= L <= floor(((D+1)*B-1)/A)
```

If D >= A there is no state. Otherwise that interval has at most two integer L values, each exactly checked by one genuine state transition. Thus there is no 2^64 enumeration, stochastic seed selection, or SAT-model ambiguity. For each recovered full state, predict attempt-3's two 64-bit outputs at every later native start L=4..1,000,000. A full 128-bit match would yield all intervening two-output coupon candidates, each independently XOR-reduced against the original K04 mask and SHA256-checked against the unchanged slot commitment.

## Original-source outcome

Original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Exact source flanks:

```text
18:01Z PS-261003-0417 ATTEMPT1 REQUESTED RECOVER: CD3E4F216ADB2FB180DA2AA90B33F7A4
18:03Z PS-261003-0417 ATTEMPT3 REQUESTED RECOVER: 44D53DFC29D7943A95D89371DA58EC64
18:02Z ATTEMPT2 ACK: WITHHELD, neither read nor fitted
```

Across all four packet byte views, the complete inversion produced **five** first-flank-compatible 128-bit states. Iterating each state through positions 4..1,000,000 produced **zero** exact full 128-bit second-flank matches. Consequently **zero** original selected coupon candidates could be constructed and **zero** original K04 commitment successes can be claimed under this precise producer/serialization/spacing model.

A completely independent positive control used **three arbitrarily chosen nonzero 128-bit synthetic states**, four true output separations (4,17,256,4096) and all four packet byte views. In each of the **48/48** complete tests, the same inverse retained the genuine original state and predicted the full later two-word bracket. This validates the exact inversion and full-packet reconstruction and controls for accidental misuse of a truncated 64-bit output.

The executed local model was source-pinned and left original evidence, commitments, verifier, canonical candidate and result map unchanged. A concise independently implementable algorithm is

```python
B = 1 << 64
M = 1 << 128
A = 0xDA942042E4DD58B5
def invert(h, j):
    d = (j - A * h) % B
    if d >= A:
        return []
    lo = (d * B + A - 1) // A
    hi = ((d + 1) * B - 1) // A
    return [h * B + suffix for suffix in range(lo, min(hi, B - 1) + 1)
            if (((h * B + suffix) * A) % M) >> 64 == j]
```

For each of the four whole-packet interpretations, invert the first 16-byte flank with `invert`, advance every recovered X state by multiplication by A modulo M, and compare the next two upper 64-bit words to the 18:03 source flank at all later starts 4..1,000,000. This reproduces the source-match counts above.

## Scope and significance

This is a complete-candidate route with a finite **source-only** failure, distinct from earlier xoshiro256** affine inverses, xoshiro256+ low-bit state fits, Romu and 64-bit xorshift retry tests. It proves that the supplied two REQUESTED flanks cannot both be consecutive two-output packets of the specified persistent Lehmer64 generator within the stated output gap, assuming the flanks were copied correctly. It does not exclude a different multiplier, generator, per-attempt reset, intervening nonsequential packet layout, output index outside the bound, or physical/copy damage. The ordinary printer's MT correlations do not attest a selected-job Lehmer64 issuer.

**No new original K04 byte or exact K08 final word was recovered.** Do not extend this into a blind multiplicative-multiplier grid without a new source clue.


## Independent ordinary-printer source control (same invocation)

The original spool also contains exactly 128 ordinary five-minute ACK jobs PS-261003-0300..0427. To check whether this generator could explain the *ordinary* stream, apply the same whole-128-bit-state inverse to every adjacent original packet pair, four byte views, permitting 4..200 native outputs between consecutive packets. All selected ATTEMPT2 bytes remain withheld and the K04 target is not used:

- **508** source-selected adjacent-packet/view brackets.
- **499** complete 128-bit states compatible with each first packet.
- **0** matching full second packets over all 4..200 start offsets.
- Distinct planted source validation: generate 40 consecutive genuine Lehmer64 packets with hidden output gaps 4..23, in each of four byte views. **156/156** adjacent-packet bracket tests recover a true source-matching later packet.

The corroborating original check further disfavors a single persistent Lehmer64 source for the complete ordinary printer spool. It cannot exclude historical hardware implementing a different emitter or independently reseeded request jobs. The following reproducible extension to the committed SFT selects the source rows with job range 0300..0427, parses PAYLOAD, and loops `find(packet[i],packet[i+1],endian,swap,200)` for `i=0..126`, all four views. This addendum adds no historical selected coupon bytes or K08 wording.
