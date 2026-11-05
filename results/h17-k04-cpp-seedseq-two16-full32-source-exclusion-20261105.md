# K04 source-only exclusion: all two-uint16 C++ std::seed_seq initializers under p955

**Agent 8 | 5 November 2026, 18:27 UTC.** The newly tested, complete **2^32** seed-pair class fails the original printer-source register constraints. No original physical coupon byte or K08 final-caption word is recovered. Original six REC8 components remain PASS, K04/K08 MISSING, combined INCOMPLETE.

## Distinct complete-coupon reconstruction hypothesis

Previous [Agent4 one-uint32 C++ seed_seq exhaustive test](h17-k04-cpp-seedseq-full32-source-gate.md) covered `std::seed_seq{one_32bit_word}`, finding no seed consistent with pre-first-twist source words `S[3]=873F7515`, `S[4]=ADD0D034`. Our distinct architecture uses **two independent 16-bit initial entropy words** `std::seed_seq{uint16_t a, uint16_t b}`. The seed-sequence permutation and its first/second pass depend on input count and positions, so a pair is not equivalent to packing them into the one-word seed already excluded. A legacy ticket, job, clock or two-halfword entropy field could hypothetically supply two words. This producer is speculative; the original firmware, stage origin and historical paper-media integrity are unverified.

The previous p955 source model fixes the two 32-bit initialized-state words using **only the original 128 ordinary printer records**, excluding the disputed selected ESC-N 18:02 ACK2 and all late exceptional rows. They are necessary conditions for this proposed generator and chronology. Original printer source `evidence/print/spool-reconstruction.log` SHA256:
`7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.

## Exact domain and algorithm

Represent the two inputs as `a=index & 65535` and `b=index >> 16`. Enumerate **every index in [0, 2^32)** in a disjoint AVX2 eight-lane loop using four OpenMP CPU threads.

Implement the actual standard-library seed-sequence generation, starting from 624 copies of `0x8B8B8B8B`, with 624 first-pass rounds and second-pass rounds through `k=946`, the last stage capable of changing either `S[3]` or `S[4]`. Importantly, `k=0` contributes the input length **two**, `k=1` injects `a`, and `k=2` injects `b`. Those details make this a genuinely different search from one-uint32 seed_seq.

Nine independent source-independent native C++ standard-library seed-pair controls exactly matched the optimized model's two output words, including boundary inputs. Every candidate pair checks both source-state words with exact equality; the original K04 acceptance hash and selected copied ACK are never used to choose or filter seeds.

## Completed original-source outcome

Executed complete local source-pinned program with count `4,294,967,296`, start `0`, OpenMP four threads:

```text
NATIVE_STD_SEEDSEQ_TWO_WORD_CONTROLS=9 PASS
S3_MATCH seeds=3756/53326 S4=1CC06BC8
START=0 COUNT=4294967296 S3_HITS=1 PAIR_HITS=0 SECONDS=777.587 RATE=5523452/s THREADS=4
```

Exactly one pair satisfies `S[3]=873F7515`: `(a,b)=(3756,53326)`; it predicts `S[4]=1CC06BC8`, contradicting original `ADD0D034`. A **separately compiled native `std::seed_seq{3756u,53326u}`** reproduced the same exact `S[3]` and contradictory `S[4]`, independently of the vectorized code.

There are **zero source-compatible full two-uint16 seed pairs**, hence this particular C++ producer/initialization/chronology combination cannot construct a valid selected K04 coupon. This is a complete mathematical/computational negative for the tested domain, rather than a few sampled wrong seeds.

Reproducer: [Agent8 standalone C++17/AVX2/OpenMP SFT](../agents/agent8/k04_seedseq_two16_sft.cpp), compiled from original source locally. Exact byte-identical remote Git blob SHA1 `4b34810894be48ce8a67334e1b28bd783aca4f50` and local source SHA256 `469f057c1d00f46959c460674108254fba39edb65d887e87f7923ee027946b14`. The independent native confirmation is a six-line C++ standard-library program, with explicit raw output shown above.

## Scope and next decision

The source-derived p955 initial-state words are **conditional on a retrospectively fitted MT chronology**; the archive never identifies a C++ `std::seed_seq` writer, its entropy packing or its historical output stage. This negative does **not** exclude a two-full32-word seed, additional input entropy, a different output origin, NumPy or Python MT seeding, other printer producers, or a separate physically imprinted selected coupon. The complete original selected buffer and its route mask were not used for target search.

Do not automatically enlarge neighboring seed_seq parameter domains just because they are computationally enumerable: find a documented original entropy source, a historical generator-stage control, or a target-relevant physical-to-copied witness. The [5 November Critic stage-matching caution](../communications/broadcast/20261105T1725Z_Critic_stage-matched-witnesses-and-target-causal-research.md) still applies. Selected K04 physical coupon bits independently authenticated: **0/128**; author-final exact K08 words: **0**.
