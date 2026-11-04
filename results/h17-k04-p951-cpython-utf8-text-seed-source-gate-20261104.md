# K04 first-cycle CPython text-seed falsifier from an original native-register byte

**Agent 15 | 4 November 2026, UTC.** Conditional producer-family exclusion, independently executed against the unmodified original source in [successful path-scoped CI run 41743529149](https://github.com/FlareZ123/workplace-v2/actions/runs/41743529149). It recovers **zero authentic K04 target bits**, and makes no claim of identifying the real printer producer. The accepted components remain K01/K02/K03/K05/K06/K07, with K04/K08 and combined REC8/1 still unresolved.

## Different original-source mechanism

Existing [CPython first-cycle initialized-register analysis](h17-k04-p951-gf2-seed-initialization-cross.md) ruled out most small **integer** seed lengths under hypothetical printer p951 chronology, leaving sixteen large seed-array word lengths 606,607,608,609,610,611,613,614,615,616,618,619,620,621,622,623. It stopped with the selected payload's full 128-bit unknown quotient. This experiment asks a different source-dependent question: **could the long integer seed be the actual CPython v2 SHA-512-extended UTF-8 text seed, such as a textual concatenation of surviving documents?** Its answer is no within the model, for a concrete byte-local reason independent of guessing a complete seed.

Under CPython `Random(str)` / `seed(str, version=2)`, encode the text as UTF-8 bytes `B`, append `SHA512(B)`, convert big-endian to a nonnegative integer, then to little-endian 32-bit `init_by_array` key words. For a seed-array of **364 through 623 32-bit words**, the key index 22 is one complete word drawn from the UTF-8 text (exactly at original byte offset `len(B)-28 : len(B)-24` in big-endian byte order); the appended 64-byte digest occupies only lower word indices 0 through 15. The first CPython initialization mixing pass visits register word 23 exactly once in this key-length regime. Thus for initialized MT register `S` and standard reference array `G=init_genrand(19650218)` the reverse key relation is valid at `i=23`:

```text
mix_c(x) = c * (x XOR (x >> 30)) mod 2^32
P = ((S[22]+22) mod 2^32) XOR mix_1566083941(S[21])
Q = ((S[23]+23) mod 2^32) XOR mix_1566083941(S[22])
T[22] = (Q - (G[23] XOR mix_1664525(P))) mod 2^32
key[22] = (T[22]-22) mod 2^32
```

Using 132 **original intact printer ACK packets** and withholding row129, the original-source native MT recurrence under p951 first-output/first-cycle interpretation fixes `S[21]=2A1C6B55`, `S[22]=BBC8EF9C`, and `S[23]` low31 `69E5AA8F`; only its high bit is unknown. Evaluating both permitted completions produces exactly:

| Source-predicted `T[22]` | Implied key word | Implied four bytes in stored UTF-8 seed |
| --- | --- | --- |
| `7D6A4D0D` | `7D6A4CF7` | `7D 6A 4C F7` |
| `FD6A4D0D` | `FD6A4CF7` | `FD 6A 4C F7` |

Both have byte `F7`, which is **forbidden in a well-formed UTF-8 encoding at any position**, irrespective of character boundaries. Therefore the original intact-source equations contradict **all text-seeded CPython v2 generators at array lengths 364..623 under this p951 chronology**, including every one of the sixteen previously remaining integer-array lengths. This result does not depend on K04 acceptance or the disputed copied ACK2 value.

## Execution and controls

- [Standalone standard-library source-pinned SFT](../agents/agent15/k04_p951_utf8_seed_gate_sft.py) reconstructs all 133 hypothetical packet positions, deliberately **never decodes selected row129**, untempers all 132 other 16-byte copies, and computes masks with an independent 624-word forward/backward native MT recurrence. Source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The real source calculation yields register masks `FFFFFFFF,FFFFFFFF,7FFFFFFF` at S21..23, exactly the two `T[22]` values above, and zero possible UTF-8 completions. This reproduces the earlier Agent39 term's two options using a different local implementation rather than borrowing its full GF2 state basis. The method also reproduced those values directly on the user's unchanged attached original ZIP.
- **Three genuinely seeded positives** use `random.Random("A" * (4*n-64))` at actual CPython key-array lengths `n=249,606,623`. All return `T[22]=41414157` and key[22]=`41414141`, agreeing with Python's actual SHA512-extended integer seed semantics. Thus the method does *not* falsely reject string-seeded synthetic generators.
- The attached 50,526-byte original ZIP contains 46 files (56 entries including directories), totaling 118,273 uncompressed member bytes. A supplementary exact 4-byte scan found neither `7D6A4CF7` nor `FD6A4CF7` in any member or in raw ZIP bytes. This excludes a direct in-place raw byte seed fragment from those scanned carriers, **not** arbitrary transformed binary seeds.

An initial CI prototype importing the larger symbolic-state implementation failed; its specific failure was not diagnosed. The independent, minimal masked-recurrence replacement passed the follow-on Actions run **41743529149**. No recurring all-commit CI was introduced; workflow only runs on dispatch or change to its own SFT/workflow files.

## Scope and next cracking direction

This is a strong **conditional producer exclusion**, not evidence that the original printer ran Python at all. The historic original source does not attest p951 chronology, a shared PRNG, text seeding or identity of generation and physical ACK-copy stages. For **key-array lengths exceeding the single-pass range (e.g. >=646)**, CPython's initial register can be visited more than once, so the simple `T[22]=key[22]+22` identity need not hold; no universal long-seed exclusion is claimed. A separately generated binary seed with arbitrary bytes is not subject to UTF-8 invalidity, although the exact original-copy fragments above are absent from the surviving file bytes.

A worthwhile successor would identify a historically meaningful *binary seed layout* with the required final 28-byte-tail subword, or abandon the speculative MT producer if a better source-selected ACK2 mechanism emerges. The result is valuable primarily because it eliminates an otherwise plausible text-concatenation avenue for every surviving n606..623 within one concrete model. **K04 physical component and K08 terminal caption remain missing; combined original verifier INCOMPLETE.**
