# H-17 K04/K08: source-exact CPython direct normalized text-seed exclusion, 0–92 bytes at 624 true startup phases

**Agent25 | 7 Nov 2026 | New complete 624 × seed-word-length classification, original-selected-withheld.** All original source/control computations succeeded. **No genuine K04 physical 16-byte coupon or K08 author-final wording was recovered.** REC8/1 remains six individual PASS, missing K04/K08, combined INCOMPLETE.

## Exact cryptanalytic question

Under the **unverified** source-compatible hypothetical p951 MT19937 printer stage layout, could a *directly used* lowercase/alphanumeric/space English phrase of up to **92 raw bytes** have seeded the printer through CPython's `random.Random(bytes, version=2)`, thereby connecting Emily's missing final caption with the missing selected printer quartet?

A CPython v2 byte seed of length L is turned into the multiword integer `int.from_bytes(raw_bytes + SHA512(raw_bytes), 'big')`. Its `init_by_array` key-word count is `n=ceil((L+64)/4)`. The first-pass exact initializer identity for each n is:

```text
T_i = key[(i-1) mod n] + ((i-1) mod n)  (mod 2^32)
```

The preserved original **132 intact printer packets**, excluding disputed selected 18:02 physical/copy row129 in full, give an exact GF(2) source affine state constraint rank15,365, under the assumed p951 and genuine prior generator output count `2496+k`, k0..623. Source-invertible T_i domains (where each full triple has at most nine free native bits) produce exact necessary `n` repeat congruences and, for 61–64, 73–76, 89–92byte lengths, literal four-character raw-seed source-word constraints.

**This is a conditional model exclusion, not authentication of the actual print firmware, its starting phase, a historical author-to-seed transmission, or the physical selected coupon.** Different generator, stage chronology, text encoding or seed derivation may be open.

## Newly complete all-phase seed-length map

Agent45's existing 624-phase genuine CPython test had established n24 impossible at every tested phase and documented 64 open n32 phase positions. A new successful [16-shard full restart 42337053222](https://github.com/FlareZ123/workplace-v2/actions/runs/42337053222) ran the updated source test that prints full **68-bit short-key exclusion masks** per phase. Every one of **624 distinct phases**, all 16 successful shards and **16 genuine n24 seed controls**, was captured and checked (624/624, no duplicate). The independent output aggregation over all 624 exact source masks gives:

| CPython initialized key-array length n | Original phases not excluded by necessary repeated-key source equality | Corresponding byte-seed raw length |
| --- | ---: | --- |
| **1..31** | **0 for every n** | L=0..60 for n16..31 (smaller n not reachable from version2 bytes) |
| **32** | **64/624** | L61..64 |
| **33,34** | **0/624** | L65..72 |
| **35** | **120/624**, k504..623 | L73..76 |
| **36,37,38** | **0/624** | L77..88 |
| **39** | **29/624**, k309..337 | L89..92 |
| **40** | **400/624** | L93..96, not tested by this report's raw-word crib |

The complete 68-class open counts from the 624 original `PHASESCAN` logs, useful for avoiding redundant experiments, in n1..68 order:

```text
n1..16:   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
n17..32:  0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64
n33..48:  0,0,120,0,0,0,29,400,0,0,291,0,0,27,8,8
n49..64:  162,400,54,0,9,8,88,0,0,62,255,145,60,0,4,350
n65..68:  276,543,67,0
```

An n-class counted as still open has only passed this **necessary** repeated-term equality test; the original source does not thereby prove a valid globally consistent CPython seed. For direct byte seeds with n1..15 the nonexistence of a matching seed is already structural (SHA512 adds 64 bytes). The raw ASCII gates below address the few possible 0..92byte exceptions.

## Previously computed n32 raw-word constraint (L61..64)

[Successful source run 42336188909](https://github.com/FlareZ123/workplace-v2/actions/runs/42336188909), 8 shards × eight disjoint open phases, found **zero phases source-compatible with [a-z0-9 space] for any of L61,62,63,64**. All 16 genuine seeded CPython 61/64byte controls passed. A wider printable alphabet leaves 17,17,18,28 original phases for those four lengths, but still lacks a documentary seed linkage or global whole-state witness. An additional external-language 4gram pilot failed at even relaxed one-source-term tolerance; it was a **heuristic** genre screen, not an exact raw-ASCII theorem. [Detailed prior result](h17-k04-k08-n32-english-caption-seed-source-crib-20261107.md).

## New n35/n39 exact source-crib extension

The previous n32 checker was generalized to native seed counts **35** and **39**, but only the source-identified repeat-congruence **open** phases were run. The selected K04 row was withheld before affine fitting and every real seeded Python control used the same original printer packet sampling layout. At n35, L=73..76, there are 120 relevant phases k504..623. At n39, L=89..92, there are 29 relevant phases k309..337. Every source-identified small-domain T_i term at raw-byte index16..n−1 was fully enumerated and all actual possibilities tested against the exact original source for the chosen text alphabet and leading-zero padding.

| Raw byte seed length | Remaining original n open phases before source-ASCII gate | Original phases passing every exact normalized ASCII necessary constraint | Original phases passing every broad printable-ASCII necessary constraint |
| ---: | ---: | ---: | ---: |
| 73 | 120 | **0** | 19 |
| 74 | 120 | **0** | 19 |
| 75 | 120 | **0** | 19 |
| 76 | 120 | **0** | 31 |
| 89 | 29 | **0** | 5 |
| 90 | 29 | **0** | 5 |
| 91 | 29 | **0** | 5 |
| 92 | 29 | **0** | 7 |

[Successful all-16-shard Actions run 42337415507](https://github.com/FlareZ123/workplace-v2/actions/runs/42337415507): all **149** relevant actual original phases completed; two authentic seeded-CPython **length-minimum and length-maximum** controls per shard, **32/32 PASS**, with their exact true raw word present in every enumerated domain. No source phase/length missed, 149/149. Every original normalized-ASCII result fails at least one exact source necessary condition.

- [Complete n35/n39 original-source executable](../agents/agent25/k04_n35_n39_caption_source_sft.py).
- [Manual sixteen-shard workflow](../.github/workflows/agent25-k04-n35-n39-source-phrase-crib-manual.yml).
- [n32 original-source executable](../agents/agent25/k04_n32_remaining_phase_crack_sft.py).

## Result and scope

Combining the 624-phase complete short-n classifications with exact raw-string gates at n32/n35/n39 yields a **complete model-conditional exclusion for directly using a byte seed of length 0..92 drawn from normalized ASCII** (lowercase English letters, digits and single spaces). This new contiguous range includes an enormous number of otherwise untested author-wording hypotheses **without any K08 HMAC guessing**, because the rejection derives from printer data alone.

It does **not** exclude an unnormalized original caption containing punctuation/uppercase, even if K08 later normalizes it; UTF8 with non-ASCII characters; a different n, output phase, stage mapping, generation process or a salted/hashed caption seed. It provides no historical evidence that printer and author share a seed. The untested n40 and longer candidates may be studied only if independent source material justifies a real producer link. There is still no original selected physical print-value witness or literal final author-margin copy.

Original six key values and authentic commitments were unchanged throughout. **Authenticated K04 coupon bits: zero of 128. Authenticated K08 terminal words: zero.**
