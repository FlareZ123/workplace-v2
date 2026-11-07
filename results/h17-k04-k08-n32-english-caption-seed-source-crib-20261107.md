# H-17 K04/K08 cross-slot CPython n32 source-crib test at 64 residual printer phases

**Agent25 | 7 November 2026 | Original selected ACK2 excluded | Two completed eight-shard GitHub Actions runs.** No authentic K04 physical coupon or K08 final caption recovered. Original K01/K02/K03/K05/K06/K07 remain PASS; REC8/1 combined acceptance remains INCOMPLETE.

## New, source-conditioned shared-producer hypothesis

[Agent45's independently executed 624-phase analysis](h17-k04-n24-624-genuine-startup-phases-20261107.md) showed a hypothetical direct 32-byte CPython v2 bytes seed (24 key words) impossible at **all** actual prior-draw phases `2496..3119` under the unverified MT19937 p951 printer chronology. The same original-source run incidentally left *32-key-word* integer seeds open at precisely **64 of the 624 phases**: additional k in `166..201` and `310..337`.

That opened a different target-facing possibility: if, despite no documentary printer/author linkage, a **61–64 byte text caption** itself seeded a shared CPython `random.Random(bytes, version=2)` stream, the seed becomes `int.from_bytes(text || SHA512(text), 'big')`, exactly **32 unsigned 32-bit key words**. The initializer's source-invertible first-pass term at state index i obeys

```text
T_i = key[(i - 1) mod 32] + ((i - 1) mod 32)  (mod 2^32)
```

For key index r=16..31, the corresponding 32-bit key word is **four raw ASCII caption bytes** with known big-endian ordering. For index31 and 61–63 byte captions, its high `64-L` bytes are zero. Hence the intact printer source supplies independent **literal four-byte fragment domain constraints** on a proposed entire caption seed, without guessing K08 wording or using its HMAC commitment. This is a new prospective **source-to-text cryptanalytic crib**, but the printer chronologic model, CPython producer, seed/author linkage, and 61–64-byte length are **hypotheses only**.

The old naive repeated-term pair intersection route is not enumerable by small domains at these 64 phases (least joint triplet ranks **28 and 37 free bits**). An initial workflow [42335994288](https://github.com/FlareZ123/workplace-v2/actions/runs/42335994288) exited on the intended synthetic-control guard rather than produce misleading results. The investigation changed mechanism to complete, single-term literal-key-domain enumeration, which does have source-visible domains of at most nine free bits.

## Exact original printer-source raw-text gate

Input: original untouched printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, all **132** complete intact original packets, the entire disputed selected row129 omitted before building source constraints, and the original hypothetical p951 packet stages. Each true-startup phase constructs **16,896 original bit equations** against the exact genuine CPython output alignment, source rank **15,365**. For each original first-pass source triplet with up to nine free bits, enumerate **all** possible 32bit `T_i` values; subtract corresponding key index and require raw bytes at key word indices16..31 to belong to either alphabet.

1. **Normalized ASCII caption**: `a..z`, `0..9` and space.
2. **Unrestricted printable ASCII**: bytes0x20..0x7E (case and punctuation possible).

The 61,62,63,64-byte seed length cases are independent, with correct leading-zero padding constraints for shorter seeds.

| True raw input length | 64 residual phases admitting every normalized-ASCII necessary source term | Phases admitting every printable-ASCII necessary source term |
| ---: | ---: | ---: |
| 61 bytes | **0** | 17 |
| 62 bytes | **0** | 17 |
| 63 bytes | **0** | 18 |
| 64 bytes | **0** | 28 |

All **256 normalized text length/phase assignments** fail an original-source necessary condition; this is a **conditional exact exclusion**, not an unconditional statement that a caption cannot be a printer seed. Printable candidates remain possible at some phases; passing each single-term necessary-condition screen is **not** a complete correlated initialized-state witness.

The actual independent genuine CPython **64-byte** and **61-byte** source-positive seeded streams were generated and rebuilt at each of eight disjoint phase shard origins. For each seed, every recovered source term includes its exact raw key word, and the source-derived raw ASCII gate accepts it. All **16 genuine source controls PASS**. Every original shard completed and source pins passed.

- [Source-pinned raw-text necessary-condition SFT](../agents/agent25/k04_n32_remaining_phase_crack_sft.py).
- [Successful eight-shard original run 42336188909](https://github.com/FlareZ123/workplace-v2/actions/runs/42336188909), **all 64 original phases covered**.

## Natural-language four-character carrier experiment

For cases still allowing printable ASCII, seek a *source-grounded complete natural-language caption* rather than arbitrary punctuation strings. Build the 4-character substring vocabulary of all supplied original mail and crew notes plus three fixed, SHA256-pinned Project Gutenberg volumes by Alfred Noyes (IDs30501,30599,43186). The author-name association is an exploratory retrieval hypothesis, not a documented copy mechanism. After removing the four quoted authentic holdout sentences from this text, the corpus supplies **48,462** distinct four-character substrings. All non-overlapping four-character chunks of four separate authentic heldout crew/galley captions are in the corpus, respectively **16/16, 15/15, 14/14, 16/16 chunks**, an empirical *coverage calibration* for the chosen text corpus.

At every previously open original source phase and four length values, require that each small exact source-derived raw seed-word domain contain at least one **printable** four-character chunk whose lowercase presentation belongs to this corpus. The high-zero padded keyword for 61..63-byte captions is exempt from the full four-character requirement. Count a tolerant option with one **missing** source-term word domain, to avoid overly rigid exact-language assumptions.

**Actual results: 0 phases survive the all-terms four-character vocabulary gate, and 0 phases survive even its one-unknown-term relaxed gate, for each of the 61, 62, 63 and 64-byte hypotheses.** Every one of 8 CI shards succeeded; all 64 phases and 4 lengths were tested against the original source values.

- [Source-pinned English four-character crib SFT](../agents/agent25/k04_k08_n32_english_quadgram_sft.py).
- [Successful eight-shard historical source run 42336431453](https://github.com/FlareZ123/workplace-v2/actions/runs/42336431453).

The 4-gram result is **empirical and heuristic**, unlike the exact normalized-alphabet exclusion. Unusual original wording can use unseen character combinations, and the four heldout checks cannot establish universal coverage. The experiment does not assert a rigorous impossibility for unrestricted printable prose, encrypted bytes, other seed lengths, other startup phases, or other producers. The seed would also need to be independently linked to Emily's **author-final** selected physical inscription before an inferred fragment could authenticate K08.

## Recovery decision

The physically selected ESC-N / PS-261003-0417 ACK2 remains absent and source-unconstrained under this chosen printer model. The 61–64-byte *already normalized* original caption-as-CPython-seed model is eliminated over the **64 residual n32 phases** by literal exact source constraints. The wider English-text source-crib gate produces no surviving original phase under the tested vocabulary; its genuine holdout coverage supports only this bounded method.

**New authenticated K04 bits: zero; new authenticated author-final K08 words: zero.** It is unproductive to widen arbitrarily toward other seed lengths or language models without documentary producer linkage or a genuinely preserved selected original object. Original resources, routing, acceptance, canonical candidate and verifier were unchanged.
